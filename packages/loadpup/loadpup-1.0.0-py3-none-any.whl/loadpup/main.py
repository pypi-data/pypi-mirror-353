"""
LoadPup主管理模块

这个模块包含了LoadPup压测工具的主要管理逻辑。
LoadPupManager类负责统一管理不同类型的压测工具，支持单次测试和多并发测试。

主要功能：
- 统一管理OpenAI和Dify压测工具
- 支持多并发级别的批量测试
- 生成汇总报告和对比分析
- 提供配置工厂方法
- 支持同步执行模式
"""

import logging
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

# 使用兼容的导入方式，支持包内和独立使用
try:
    from .openai_benchmark import OpenAIBenchmark
    from .dify_benchmark import DifyBenchmark
except ImportError:
    # 如果相对导入失败，尝试直接导入
    from openai_benchmark import OpenAIBenchmark
    from dify_benchmark import DifyBenchmark


class LoadPupManager:
    """
    压测管理器
    
    这是LoadPup的核心管理类，负责协调和管理不同类型的压测工具。
    支持创建、配置和运行不同API类型的性能测试。
    
    属性:
        benchmark_types (Dict): 支持的压测工具类型映射表
    """
    
    def __init__(self):
        """
        初始化压测管理器
        
        设置支持的压测工具类型，目前包括OpenAI和Dify两种API类型。
        """
        self.benchmark_types = {
            'openai': OpenAIBenchmark,
            'dify': DifyBenchmark
        }
    
    def create_benchmark(self, benchmark_type: str, config: Dict[str, Any]):
        """
        创建指定类型的压测实例
        
        根据传入的类型字符串，创建相应的压测工具实例。
        支持的类型包括'openai'和'dify'。
        
        Args:
            benchmark_type (str): 压测工具类型，如'openai'或'dify'
            config (Dict[str, Any]): 压测配置参数字典
            
        Returns:
            BenchmarkBase: 对应类型的压测实例
            
        Raises:
            ValueError: 当传入不支持的压测类型时抛出
        """
        if benchmark_type not in self.benchmark_types:
            raise ValueError(f"不支持的压测类型: {benchmark_type}, 支持的类型: {list(self.benchmark_types.keys())}")
        
        benchmark_class = self.benchmark_types[benchmark_type]
        return benchmark_class(config)
    
    def run_single_benchmark(self, benchmark_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行单个压测任务
        
        创建指定类型的压测实例并执行完整的测试流程。
        包括配置验证、压测执行、报告生成和结果保存。
        
        Args:
            benchmark_type (str): 压测工具类型
            config (Dict[str, Any]): 压测配置参数
            
        Returns:
            Dict[str, Any]: 包含测试结果的报告字典
        """
        benchmark = self.create_benchmark(benchmark_type, config)
        return benchmark.run_and_save()
    
    def run_parallel_benchmarks(self, parallel_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        运行多个并发数的压测任务
        
        依次执行不同并发数配置的压测，并生成汇总报告。
        每个配置会创建独立的压测实例，确保测试结果的独立性。
        
        Args:
            parallel_configs (List[Dict[str, Any]]): 包含多个并发配置的列表
            
        Returns:
            List[Dict[str, Any]]: 所有测试结果的列表
        """
        all_results = []
        
        for config in parallel_configs:
            benchmark_type = config.get('benchmark_type', 'openai')
            parallel = config.get('parallel', 1)
            
            logging.info(f"\n开始测试 {benchmark_type} 并发数: {parallel}")
            
            try:
                # 执行单个并发数的测试
                result = self.run_single_benchmark(benchmark_type, config)
                all_results.append(result)
                logging.info(f"完成并发数 {parallel} 的测试")
            except Exception as e:
                logging.error(f"并发数 {parallel} 测试失败: {str(e)}")
                continue
        
        # 如果有成功的测试结果，生成汇总报告
        if all_results:
            self._save_summary_report(all_results, parallel_configs[0].get('output_dir', 'output'))
        
        return all_results
    
    def _save_summary_report(self, results: List[Dict[str, Any]], output_dir: str):
        """
        保存汇总报告
        
        将多个并发数测试的结果汇总成一个报告，便于对比分析不同并发数下的性能表现。
        
        Args:
            results (List[Dict[str, Any]]): 所有测试结果的列表
            output_dir (str): 输出目录路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 创建DataFrame，便于处理表格数据
        df = pd.DataFrame(results)
        
        # 保存Excel格式的汇总报告
        excel_file = f"{output_dir}/summary_report_{timestamp}.xlsx"
        df.to_excel(excel_file, index=False)
        
        logging.info(f"\n汇总报告已保存到: {excel_file}")
        print("\n测试结果汇总:")
        print(df.to_string(index=False))


def create_openai_config(args) -> Dict[str, Any]:
    """
    创建OpenAI压测配置
    
    根据命令行参数创建OpenAI API压测的配置字典。
    包括模型信息、并发参数、prompt设置等。
    
    Args:
        args: 命令行参数对象，包含OpenAI相关的配置参数
        
    Returns:
        Dict[str, Any]: OpenAI压测配置字典
    """
    return {
        'benchmark_type': 'openai',
        'base_url': args.base_url,
        'model': args.model,
        'parallel': args.parallel,
        'prompt_length': args.prompt_length,
        'output_length': args.output_length,
        'temperature': getattr(args, 'temperature', 0.7),
        'tokenizer_path': getattr(args, 'tokenizer_path', './tokenizer_dir'),
        'output_dir': args.output_dir
    }


def create_dify_config(args) -> Dict[str, Any]:
    """
    创建Dify压测配置
    
    根据命令行参数创建Dify API压测的配置字典。
    包括API地址、密钥、查询文件、请求数量等配置。
    
    Args:
        args: 命令行参数对象，包含Dify相关的配置参数
        
    Returns:
        Dict[str, Any]: Dify压测配置字典
    """
    return {
        'benchmark_type': 'dify',
        'api_url': args.api_url,
        'api_key': args.api_key,
        'parallel': args.parallel,
        'query_file': getattr(args, 'query_file', None),
        'total_requests': getattr(args, 'total_requests', args.parallel * 10),
        'tokenizer_path': getattr(args, 'tokenizer_path', './tokenizer_dir'),
        'output_dir': args.output_dir
    } 