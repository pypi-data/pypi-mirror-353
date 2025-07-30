"""
压测工具基础抽象类模块

这个模块定义了所有压测工具的基础接口和共同功能。
BenchmarkBase类作为抽象基类，提供了统一的压测流程、结果处理和报告生成功能。

主要功能：
- 定义标准的压测接口
- 提供统一的日志系统
- 实现通用的结果统计和报告生成
- 支持多种格式的输出（JSON、Excel）
- 提供配置验证框架
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os
import json
import logging
import time
from datetime import datetime
import pandas as pd


class BenchmarkBase(ABC):
    """
    压测工具基础抽象类
    
    这是所有压测工具类的基类，定义了标准的压测流程和接口。
    子类需要实现具体的压测逻辑，但可以复用通用的功能如日志、报告生成等。
    
    属性:
        config (Dict[str, Any]): 压测配置参数
        results (List): 存储详细的请求结果
        start_time (float): 压测开始时间戳
        end_time (float): 压测结束时间戳
        total_requests (int): 总请求数
        successful_requests (int): 成功请求数
        failed_requests (int): 失败请求数
        total_input_tokens (int): 总输入token数
        total_output_tokens (int): 总输出token数
        total_latency (float): 总延迟时间
        output_dir (str): 输出目录路径
        logger (logging.Logger): 日志记录器
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化压测基类
        
        Args:
            config (Dict[str, Any]): 包含压测配置的字典，如并发数、输出目录等
        """
        self.config = config
        self.results = []
        self.start_time = None
        self.end_time = None
        
        # 统计数据初始化
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_latency = 0
        
        # 设置输出目录，默认按压测类型分类
        self.output_dir = config.get('output_dir', f'output/{self.get_benchmark_type()}')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置日志系统
        self._setup_logging()
    
    @abstractmethod
    def get_benchmark_type(self) -> str:
        """
        返回压测类型名称
        
        这是一个抽象方法，子类必须实现。
        用于标识不同的压测工具类型，如'openai'、'dify'等。
        
        Returns:
            str: 压测类型的字符串标识
        """
        pass
    
    @abstractmethod
    def run_benchmark(self) -> Dict[str, Any]:
        """
        运行压测的核心方法
        
        这是一个抽象方法，子类必须实现具体的压测逻辑。
        该方法应该执行实际的API请求测试，并更新相关统计数据。
        
        Returns:
            Dict[str, Any]: 包含压测结果的字典
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        验证配置是否有效
        
        这是一个抽象方法，子类需要根据自己的需求实现配置验证逻辑。
        用于在压测开始前检查配置参数的完整性和有效性。
        
        Returns:
            bool: 配置有效返回True，否则返回False
        """
        pass
    
    def _setup_logging(self):
        """
        设置日志系统
        
        配置文件和控制台的双重日志输出，确保测试过程可追踪。
        修复了重复日志的问题，每个logger实例只保留一份handler。
        """
        log_file = os.path.join(self.output_dir, 'benchmark.log')
        
        # 配置统一的日志格式：时间 - 类名 - 级别 - 消息
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 获取以类名命名的logger实例
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        
        # 清除已有的handlers，避免重复日志输出
        if logger.handlers:
            logger.handlers.clear()
        
        # 设置文件处理器，将日志写入文件
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 设置控制台处理器，将日志输出到终端
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 防止日志向上传播到根logger，避免重复输出
        logger.propagate = False
        
        self.logger = logger
    
    def generate_report(self) -> Dict[str, Any]:
        """
        生成测试报告
        
        基于收集的统计数据计算各种性能指标，生成标准化的测试报告。
        包括成功率、平均延迟、吞吐量、QPS等关键指标。
        
        Returns:
            Dict[str, Any]: 包含完整测试结果的报告字典
            
        Raises:
            ValueError: 当测试未完成时抛出异常
        """
        if not self.start_time or not self.end_time:
            raise ValueError("测试未完成，无法生成报告")
        
        # 计算测试总时长
        test_duration = self.end_time - self.start_time
        
        # 计算平均值（避免除零错误）
        avg_input_tokens = self.total_input_tokens / self.total_requests if self.total_requests > 0 else 0
        avg_output_tokens = self.total_output_tokens / self.successful_requests if self.successful_requests > 0 else 0
        avg_latency = self.total_latency / self.successful_requests if self.successful_requests > 0 else 0
        throughput = self.total_output_tokens / test_duration if test_duration > 0 else 0
        qps = self.successful_requests / test_duration if test_duration > 0 else 0
        
        return {
            "测试类型": self.get_benchmark_type(),
            "并发数": self.config.get('parallel', 1),
            "测试总时长(s)": round(test_duration, 2),
            "总请求数": self.total_requests,
            "成功请求数": self.successful_requests,
            "失败请求数": self.failed_requests,
            "成功率(%)": round(self.successful_requests / self.total_requests * 100, 2) if self.total_requests > 0 else 0,
            "平均输入长度(tokens)": round(avg_input_tokens, 2),
            "平均输出长度(tokens)": round(avg_output_tokens, 2),
            "平均吞吐量(token/s)": round(throughput, 2),
            "平均QPS": round(qps, 2),
            "平均延迟(s)": round(avg_latency, 4)
        }
    
    def save_results(self, report: Dict[str, Any]):
        """
        保存测试结果到文件
        
        将测试报告同时保存为JSON和Excel两种格式，方便不同场景的使用。
        文件名包含时间戳，避免覆盖历史测试结果。
        
        Args:
            report (Dict[str, Any]): 要保存的测试报告数据
            
        Returns:
            tuple: 返回(json_file, excel_file)文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存JSON格式报告，便于程序处理
        json_file = os.path.join(self.output_dir, f'report_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
        
        # 保存Excel格式报告，便于人工查看和分析
        df = pd.DataFrame([report])
        excel_file = os.path.join(self.output_dir, f'report_{timestamp}.xlsx')
        df.to_excel(excel_file, index=False)
        
        self.logger.info(f"测试结果已保存到: {json_file} 和 {excel_file}")
        
        return json_file, excel_file
    
    def run_and_save(self) -> Dict[str, Any]:
        """
        执行完整的压测流程并保存结果
        
        这是对外的主要接口方法，封装了完整的压测流程：
        1. 验证配置
        2. 执行压测
        3. 生成报告
        4. 保存结果
        
        Returns:
            Dict[str, Any]: 最终的测试报告
            
        Raises:
            ValueError: 当配置验证失败时抛出异常
        """
        if not self.validate_config():
            raise ValueError("配置验证失败")
        
        self.logger.info(f"开始 {self.get_benchmark_type()} 压测...")
        self.logger.info(f"配置参数: {self.config}")
        
        # 执行具体的压测逻辑
        result = self.run_benchmark()
        
        # 生成标准化报告
        report = self.generate_report()
        
        # 保存结果到文件
        self.save_results(report)
        
        return report 