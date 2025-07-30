#!/usr/bin/env python3
'''
LoadPup CLI - 简化的命令行接口
'''

import argparse
import sys
import logging
from typing import List, Dict, Any

# 使用兼容的导入方式
try:
    from .main import LoadPupManager, create_openai_config, create_dify_config
except ImportError:
    from main import LoadPupManager, create_openai_config, create_dify_config


def parse_parallel_list(parallel_str: str) -> List[int]:
    """
    解析并发数字符串
    
    将形如"1;2;4"的字符串解析为整数列表[1, 2, 4]。
    支持单个数字或分号分隔的多个数字。
    
    Args:
        parallel_str (str): 并发数字符串，如"1"或"1;2;4"
        
    Returns:
        List[int]: 解析后的并发数列表
        
    Raises:
        ValueError: 当输入格式不正确或包含非正整数时抛出
    """
    try:
        if ';' in parallel_str:
            # 处理多个并发数的情况
            parallel_list = [int(p.strip()) for p in parallel_str.split(';')]
        else:
            # 处理单个并发数的情况
            parallel_list = [int(parallel_str)]
        
        # 验证所有并发数都是正整数
        for p in parallel_list:
            if p <= 0:
                raise ValueError(f"并发数必须是正整数，得到: {p}")
                
        return parallel_list
    except ValueError as e:
        raise ValueError(f"并发数格式错误: {parallel_str}. 应该是正整数或用分号分隔的正整数列表。详细错误: {str(e)}")


def setup_openai_parser(subparsers):
    """
    设置OpenAI子命令的参数解析器
    
    定义OpenAI API压测所需的所有命令行参数，包括必需参数和可选参数。
    
    Args:
        subparsers: argparse的子解析器对象
        
    Returns:
        ArgumentParser: 配置好的OpenAI参数解析器
    """
    openai_parser = subparsers.add_parser(
        'openai', 
        help='OpenAI API压测',
        description='对OpenAI兼容的API进行性能压测，支持自定义模型、prompt长度、输出长度等参数'
    )
    
    # 必需参数
    openai_parser.add_argument(
        '--base_url', 
        required=True,
        help='OpenAI API的基础URL，如: https://api.openai.com/v1'
    )
    openai_parser.add_argument(
        '--model', 
        required=True,
        help='要测试的模型名称，如: gpt-3.5-turbo'
    )
    openai_parser.add_argument(
        '--parallel', 
        required=True,
        help='并发数，支持单个数字(如"4")或多个数字用分号分隔(如"1;2;4")'
    )
    
    # 可选参数，带有合理的默认值
    openai_parser.add_argument(
        '--prompt_length', 
        type=int, 
        default=500,
        help='输入prompt的token长度，默认500'
    )
    openai_parser.add_argument(
        '--output_length', 
        type=int, 
        default=200,
        help='期望输出的token长度，默认200'
    )
    openai_parser.add_argument(
        '--temperature', 
        type=float, 
        default=0.7,
        help='模型温度参数，控制输出随机性，默认0.7'
    )
    openai_parser.add_argument(
        '--tokenizer_path', 
        default='./tokenizer_dir',
        help='分词器路径，用于token计算，默认./tokenizer_dir'
    )
    openai_parser.add_argument(
        '--output_dir', 
        default='output/openai',
        help='测试结果输出目录，默认output/openai'
    )
    
    return openai_parser


def setup_dify_parser(subparsers):
    """
    设置Dify子命令的参数解析器
    
    定义Dify API压测所需的所有命令行参数，包括API配置、查询设置等。
    
    Args:
        subparsers: argparse的子解析器对象
        
    Returns:
        ArgumentParser: 配置好的Dify参数解析器
    """
    dify_parser = subparsers.add_parser(
        'dify', 
        help='Dify API压测',
        description='对Dify API进行性能压测，支持自定义查询内容、并发数、总请求数等参数'
    )
    
    # 必需参数
    dify_parser.add_argument(
        '--api_url', 
        required=True,
        help='Dify API的完整URL，如: http://your-dify-host/v1/chat-messages'
    )
    dify_parser.add_argument(
        '--api_key', 
        required=True,
        help='Dify API密钥，用于身份验证'
    )
    dify_parser.add_argument(
        '--parallel', 
        required=True,
        help='并发数，支持单个数字(如"4")或多个数字用分号分隔(如"1;2;4")'
    )
    
    # 可选参数
    dify_parser.add_argument(
        '--query_file',
        help='包含查询内容的文件路径，每行一个查询。如不指定则使用默认查询'
    )
    dify_parser.add_argument(
        '--total_requests', 
        type=int,
        help='总请求数。如不指定，则为并发数的10倍'
    )
    dify_parser.add_argument(
        '--tokenizer_path', 
        default='./tokenizer_dir',
        help='分词器路径，用于token计算，默认./tokenizer_dir'
    )
    dify_parser.add_argument(
        '--output_dir', 
        default='output/dify',
        help='测试结果输出目录，默认output/dify'
    )
    
    return dify_parser


def validate_openai_args(args) -> bool:
    """
    验证OpenAI参数的有效性
    
    检查OpenAI相关参数是否符合要求，如URL格式、数值范围等。
    
    Args:
        args: 解析后的命令行参数对象
        
    Returns:
        bool: 参数有效返回True，否则返回False
    """
    # 验证prompt和output长度
    if args.prompt_length <= 0:
        print(f"错误: prompt_length必须是正整数，得到: {args.prompt_length}")
        return False
    
    if args.output_length <= 0:
        print(f"错误: output_length必须是正整数，得到: {args.output_length}")
        return False
    
    # 验证temperature范围
    if not (0.0 <= args.temperature <= 2.0):
        print(f"错误: temperature应在0.0-2.0范围内，得到: {args.temperature}")
        return False
    
    # 验证URL格式（简单检查）
    if not (args.base_url.startswith('http://') or args.base_url.startswith('https://')):
        print(f"错误: base_url应以http://或https://开头，得到: {args.base_url}")
        return False
    
    return True


def validate_dify_args(args) -> bool:
    """
    验证Dify参数的有效性
    
    检查Dify相关参数是否符合要求，如API密钥格式、请求数等。
    
    Args:
        args: 解析后的命令行参数对象
        
    Returns:
        bool: 参数有效返回True，否则返回False
    """
    # 验证API密钥不为空
    if not args.api_key.strip():
        print("错误: api_key不能为空")
        return False
    
    # 验证URL格式（简单检查）
    if not (args.api_url.startswith('http://') or args.api_url.startswith('https://')):
        print(f"错误: api_url应以http://或https://开头，得到: {args.api_url}")
        return False
    
    # 验证总请求数（如果指定）
    if hasattr(args, 'total_requests') and args.total_requests is not None:
        if args.total_requests <= 0:
            print(f"错误: total_requests必须是正整数，得到: {args.total_requests}")
            return False
    
    return True


def run_openai_benchmark(args) -> bool:
    """
    执行OpenAI压测
    
    根据解析的参数执行OpenAI API的性能压测。
    支持多并发数的批量测试。
    
    Args:
        args: 解析后的OpenAI命令行参数
        
    Returns:
        bool: 执行成功返回True，否则返回False
    """
    try:
        # 解析并发数列表
        parallel_list = parse_parallel_list(args.parallel)
        
        # 验证参数
        if not validate_openai_args(args):
            return False
        
        # 创建管理器实例
        manager = LoadPupManager()
        
        # 为每个并发数创建配置
        configs = []
        for parallel in parallel_list:
            args.parallel = parallel
            config = create_openai_config(args)
            configs.append(config)
        
        # 执行批量压测
        print(f"开始OpenAI压测，并发数列表: {parallel_list}")
        results = manager.run_parallel_benchmarks(configs)
        
        if results:
            print(f"OpenAI压测完成，共执行 {len(results)} 个测试")
            return True
        else:
            print("OpenAI压测失败，没有成功的测试结果")
            return False
            
    except Exception as e:
        print(f"OpenAI压测执行失败: {str(e)}")
        return False


def run_dify_benchmark(args) -> bool:
    """
    执行Dify压测
    
    根据解析的参数执行Dify API的性能压测。
    支持多并发数的批量测试。
    
    Args:
        args: 解析后的Dify命令行参数
        
    Returns:
        bool: 执行成功返回True，否则返回False
    """
    try:
        # 解析并发数列表
        parallel_list = parse_parallel_list(args.parallel)
        
        # 验证参数
        if not validate_dify_args(args):
            return False
        
        # 创建管理器实例
        manager = LoadPupManager()
        
        # 为每个并发数创建配置
        configs = []
        for parallel in parallel_list:
            args.parallel = parallel
            # 如果没有指定total_requests，设置为并发数的10倍
            if not hasattr(args, 'total_requests') or args.total_requests is None:
                args.total_requests = parallel * 10
            config = create_dify_config(args)
            configs.append(config)
        
        # 执行批量压测
        print(f"开始Dify压测，并发数列表: {parallel_list}")
        results = manager.run_parallel_benchmarks(configs)
        
        if results:
            print(f"Dify压测完成，共执行 {len(results)} 个测试")
            return True
        else:
            print("Dify压测失败，没有成功的测试结果")
            return False
            
    except Exception as e:
        print(f"Dify压测执行失败: {str(e)}")
        return False


def main():
    """
    主函数 - 命令行入口点
    
    解析命令行参数，根据子命令类型执行相应的压测逻辑。
    支持OpenAI和Dify两种API类型的压测。
    """
    # 创建主解析器
    parser = argparse.ArgumentParser(
        description='LoadPup - 专业的API性能压测工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # OpenAI API压测
  python cli.py openai --base_url "https://api.openai.com/v1" --model "gpt-3.5-turbo" --parallel "1;2;4"
  
  # Dify API压测
  python cli.py dify --api_url "http://localhost/v1/chat-messages" --api_key "your-key" --parallel "1;2"
        """
    )
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(
        dest='command', 
        help='选择压测类型',
        metavar='{openai,dify}'
    )
    
    # 设置OpenAI和Dify子命令的解析器
    setup_openai_parser(subparsers)
    setup_dify_parser(subparsers)
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 如果没有提供子命令，显示帮助信息
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    
    # 根据子命令执行相应的压测
    success = False
    if args.command == 'openai':
        success = run_openai_benchmark(args)
    elif args.command == 'dify':
        success = run_dify_benchmark(args)
    
    # 根据执行结果设置退出码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 