"""
LoadPup - 统一API性能压测工具包

这是一个专业的API性能压测工具，支持对OpenAI和Dify API进行全面的性能测试和分析。
主要功能包括：
- 支持多种API类型的压测（OpenAI、Dify）
- 多并发级别测试
- 详细的性能指标统计（延迟、吞吐量、成功率等）
- 百分位数分析（P50、P90、P99）
- 多格式报告输出（JSON、Excel）
- 实时日志记录和监控

版本: 1.0.0
作者: LoadPup Team
许可证: Apache 2.0
"""

# 导入主要类和函数，方便外部使用
try:
    # 尝试相对导入（在包内使用时）
    from .main import LoadPupManager, create_openai_config, create_dify_config
    from .benchmark_base import BenchmarkBase
    from .openai_benchmark import OpenAIBenchmark
    from .dify_benchmark import DifyBenchmark
except ImportError:
    # 如果相对导入失败，使用直接导入（standalone使用时）
    from main import LoadPupManager, create_openai_config, create_dify_config
    from benchmark_base import BenchmarkBase
    from openai_benchmark import OpenAIBenchmark
    from dify_benchmark import DifyBenchmark

# 定义包的公开接口
__all__ = [
    'LoadPupManager',
    'BenchmarkBase', 
    'OpenAIBenchmark',
    'DifyBenchmark',
    'create_openai_config',
    'create_dify_config'
]

# 版本信息
__version__ = '1.0.0'
__author__ = 'LoadPup Team'
__license__ = 'Apache 2.0'



