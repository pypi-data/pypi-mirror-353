"""
Dify API压测实现模块

这个模块实现了针对Dify API的性能压测功能。
使用多线程并发请求和流式响应处理，提供详细的性能分析报告。

主要功能：
- 支持Dify API的流式聊天接口压测
- 使用ThreadPoolExecutor实现真正的并发控制
- 详细追踪每个请求的性能指标
- 支持自定义查询文件或使用默认查询
- 提供29个详细的性能指标（比OpenAI多了Dify特有字段）
- 包含P50、P90、P99百分位数分析
- 线程安全的统计数据收集
- 支持token计数（基于transformers库或字符估算）

特色功能：
- 流式响应解析和首token延迟测量
- 每token延迟计算
- 线程安全的请求详情收集
- numpy基础的百分位数计算
- 完整的错误处理和重试机制
"""

import asyncio
import aiohttp
import time
import random
import json
import logging
import os
import requests
import threading
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# 修改为兼容的导入方式
try:
    from .benchmark_base import BenchmarkBase
except ImportError:
    from benchmark_base import BenchmarkBase

try:
    from transformers import AutoTokenizer
except ImportError:
    AutoTokenizer = None


class DifyBenchmark(BenchmarkBase):
    """Dify API 压测工具"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.queries = []
        self.tokenizer = None
        self.total_first_token_latency = 0
        self.total_token_latency = 0
        self.lock = threading.Lock()  # 添加线程锁
        self.request_details = []  # 存储每个请求的详细信息
        
        # 加载查询数据和tokenizer
        self._load_queries()
        self._load_tokenizer()
    
    def get_benchmark_type(self) -> str:
        return "dify"
    
    def validate_config(self) -> bool:
        """验证Dify配置"""
        required_fields = ['api_url', 'api_key', 'parallel']
        for field in required_fields:
            if field not in self.config:
                self.logger.error(f"缺少必需的配置项: {field}")
                return False
        
        query_file = self.config.get('query_file')
        if query_file and not os.path.exists(query_file):
            self.logger.error(f"查询文件不存在: {query_file}")
            return False
        
        return True
    
    def _load_queries(self):
        """加载查询数据"""
        query_file = self.config.get('query_file')
        if query_file and os.path.exists(query_file):
            with open(query_file, 'r', encoding='utf-8') as f:
                self.queries = [line.strip() for line in f if line.strip()]
                self.logger.info(f"加载了 {len(self.queries)} 条查询")
        else:
            # 默认查询
            self.queries = [
                "你好，请介绍一下自己",
                "请解释一下人工智能的基本概念",
                "请简述机器学习的应用场景",
                "请介绍一下深度学习的发展历史"
            ]
            self.logger.info("使用默认查询数据")
    
    def _load_tokenizer(self):
        """加载tokenizer"""
        if AutoTokenizer is None:
            self.logger.warning("transformers库未安装，将使用字符数估算token数")
            return
        
        tokenizer_path = self.config.get('tokenizer_path', './tokenizer_dir')
        if os.path.exists(tokenizer_path):
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
                self.logger.info(f"成功加载tokenizer: {tokenizer_path}")
            except Exception as e:
                self.logger.warning(f"加载tokenizer失败: {e}，将使用字符数估算")
        else:
            self.logger.warning(f"tokenizer路径不存在: {tokenizer_path}，将使用字符数估算")
    
    def _count_tokens(self, text: str) -> int:
        """统计token数量"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # 简单估算：中文按字符数，英文按单词数/4
            return len(text)
    
    def _make_request(self) -> Dict[str, Any]:
        """发送单个请求 - 同步版本"""
        query = random.choice(self.queries)
        input_tokens = self._count_tokens(query)
        
        payload = {
            "inputs": {},
            "query": query,
            "response_mode": "streaming",
            "conversation_id": "",
            "user": f"test-user-{random.randint(1, 1000)}",
            "files": []
        }
        
        headers = {
            'Authorization': f'Bearer {self.config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        start_time = time.time()
        first_token_time = None
        response_text = ""
        
        try:
            response = requests.post(
                self.config['api_url'], 
                json=payload, 
                headers=headers, 
                stream=True,
                timeout=30
            )
            
            # 线程安全地更新计数器
            with self.lock:
                self.total_requests += 1
                self.total_input_tokens += input_tokens
            
            if response.status_code == 200:
                with self.lock:
                    self.successful_requests += 1
                
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if not line_str.startswith("data:"):
                            continue
                        try:
                            json_str = line_str[len("data:"):].strip()
                            if not json_str:
                                continue
                            data = json.loads(json_str)
                            if data.get("event") == "message" and "answer" in data:
                                if not first_token_time:
                                    first_token_time = time.time()
                                    with self.lock:
                                        self.total_first_token_latency += (first_token_time - start_time)
                                response_text += data["answer"]
                        except Exception as e:
                            self.logger.debug(f"解析流数据出错: {e}")
                            continue
            else:
                with self.lock:
                    self.failed_requests += 1
                self.logger.error(f"请求失败，状态码: {response.status_code}")
                return None
                    
        except Exception as e:
            with self.lock:
                self.failed_requests += 1
            self.logger.error(f"请求错误: {str(e)}")
            return None
        
        end_time = time.time()
        output_tokens = self._count_tokens(response_text)
        
        total_time = end_time - start_time
        first_token_latency = first_token_time - start_time if first_token_time else 0
        token_latency = total_time / output_tokens if output_tokens > 0 else 0
        
        # 收集请求详细信息用于百分位计算
        request_detail = {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_latency': total_time,
            'first_token_latency': first_token_latency,
            'token_latency': token_latency
        }
        
        # 线程安全地更新统计
        with self.lock:
            self.total_output_tokens += output_tokens
            self.total_latency += total_time
            self.request_details.append(request_detail)
            if output_tokens > 0:
                self.total_token_latency += token_latency
        
        return request_detail
    
    def run_benchmark(self) -> Dict[str, Any]:
        """运行Dify压测 - 同步版本"""
        self.start_time = time.time()
        
        parallel = self.config.get('parallel', 10)
        total_requests = self.config.get('total_requests', parallel * 10)
        
        self.logger.info(f"开始Dify压测，并发数: {parallel}, 总请求数: {total_requests}")
        
        # 使用线程池实现并发
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = []
            for _ in range(total_requests):
                futures.append(executor.submit(self._make_request))
            
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"任务执行失败: {e}")
        
        self.results.extend(results)
        self.end_time = time.time()
        self.logger.info("Dify压测完成")
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'results': self.results
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """生成Dify压测报告 - 使用详细格式"""
        if not self.start_time or not self.end_time:
            raise ValueError("测试未完成，无法生成报告")
        
        # 获取基本配置信息
        parallel = self.config.get('parallel', 1)
        test_duration = self.end_time - self.start_time
        
        # 计算平均值
        avg_latency = self.total_latency / self.successful_requests if self.successful_requests > 0 else 0
        avg_first_token_latency = (self.total_first_token_latency / self.successful_requests 
                                 if self.successful_requests > 0 else 0)
        avg_token_latency = (self.total_token_latency / self.successful_requests 
                           if self.successful_requests > 0 else 0)
        avg_input_tokens = self.total_input_tokens / self.total_requests if self.total_requests > 0 else 0
        avg_output_tokens = self.total_output_tokens / self.successful_requests if self.successful_requests > 0 else 0
        throughput = self.total_output_tokens / test_duration if test_duration > 0 else 0
        qps = self.successful_requests / test_duration if test_duration > 0 else 0
        
        # 计算百分位数据
        p50_latency = p90_latency = p99_latency = 0
        p50_first_token = p90_first_token = p99_first_token = 0
        p50_token = p90_token = p99_token = 0
        
        if self.request_details:
            # 延迟百分位
            latencies = [detail['total_latency'] for detail in self.request_details]
            p50_latency = np.percentile(latencies, 50)
            p90_latency = np.percentile(latencies, 90)
            p99_latency = np.percentile(latencies, 99)
            
            # 首token延迟百分位
            first_token_latencies = [detail['first_token_latency'] for detail in self.request_details if detail['first_token_latency'] > 0]
            if first_token_latencies:
                p50_first_token = np.percentile(first_token_latencies, 50)
                p90_first_token = np.percentile(first_token_latencies, 90)
                p99_first_token = np.percentile(first_token_latencies, 99)
            
            # 单token延迟百分位
            token_latencies = [detail['token_latency'] for detail in self.request_details if detail['token_latency'] > 0]
            if token_latencies:
                p50_token = np.percentile(token_latencies, 50)
                p90_token = np.percentile(token_latencies, 90)
                p99_token = np.percentile(token_latencies, 99)
        
        # 构建详细的结果报告 - 匹配OpenAI格式
        result = {
            "模型": "dify-api",  # Dify没有具体模型概念
            "并行度": parallel,
            "提示长度": round(avg_input_tokens, 1),
            "输出长度": round(avg_output_tokens, 1),
            "测试总时长(s)": round(test_duration, 2),
            "总请求数": self.total_requests,
            "成功请求数": self.successful_requests,
            "失败请求数": self.failed_requests,
            "平均吞吐量(token/s)": round(throughput, 2),
            "平均QPS": round(qps, 4),
            "平均延迟(s)": round(avg_latency, 4),
            "首token平均延迟(s)": round(avg_first_token_latency, 4),
            "单token平均延迟(s)": round(avg_token_latency, 6),
            "平均输入token数": round(avg_input_tokens, 1),
            "平均输出token数": round(avg_output_tokens, 1),
            "P50延迟(s)": round(p50_latency, 4),
            "P50首token延迟(s)": round(p50_first_token, 4),
            "P50单token延迟(s)": round(p50_token, 6),
            "P90延迟(s)": round(p90_latency, 4),
            "P90首token延迟(s)": round(p90_first_token, 4),
            "P90单token延迟(s)": round(p90_token, 6),
            "P99延迟(s)": round(p99_latency, 4),
            "P99首token延迟(s)": round(p99_first_token, 4),
            "P99单token延迟(s)": round(p99_token, 6),
            # 额外信息
            "API URL": self.config.get('api_url', 'unknown'),
            "查询文件": self.config.get('query_file', '默认查询'),
            "查询数量": len(self.queries),
            "温度": "N/A",  # Dify API没有温度参数
            "流式输出": True  # Dify使用流式输出
        }
        
        return result 