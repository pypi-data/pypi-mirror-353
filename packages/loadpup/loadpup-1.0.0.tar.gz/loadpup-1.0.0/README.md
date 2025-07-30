# LoadPup - 专业的API性能压测工具

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](https://github.com/anonNo2/LoadPup)

LoadPup是一个专业的API性能压测工具，专门设计用于对大语言模型(LLM)API进行全面的性能测试和分析。支持OpenAI兼容接口和Dify API，提供详细的性能指标分析和百分位数统计。

## ✨ 核心特性

### 🚀 多API支持
- **OpenAI兼容接口**: 基于evalscope库的高性能压测
- **Dify API**: 专门优化的流式响应压测
- **统一接口**: 一致的配置和使用体验

### 📊 详细性能分析
- **27-29个详细指标**: 全方位性能数据收集
- **百分位数分析**: P50、P90、P99延迟分析
- **多维度指标**: 延迟、吞吐量、成功率、token统计
- **首token延迟**: 流式响应的关键指标

### 🎯 灵活配置
- **多并发测试**: 支持"1;2;4;8"格式的批量并发测试
- **自定义参数**: 模型、prompt长度、温度等可配置
- **查询文件**: 支持自定义测试查询集合
- **输出格式**: JSON和Excel双格式报告

### 🛡️ 稳定可靠
- **同步执行**: 避免异步复杂性，更稳定
- **错误处理**: 完善的异常处理和重试机制
- **线程安全**: 多线程环境下的数据安全
- **日志系统**: 详细的测试过程记录

## 📋 系统要求

- Python 3.11+
- 依赖库：
  - evalscope (OpenAI压测引擎)
  - requests (HTTP请求)
  - pandas (数据处理)
  - numpy (数值计算)
  - openpyxl (Excel文件)
  - transformers (可选，用于token计数)

## 🔧 安装

### 1. 克隆仓库
```bash
git clone https://github.com/anonNo2/LoadPup.git
cd LoadPup
```

### 2. 安装依赖
```bash
# 使用pip安装
pip install -r requirements.txt

# 或使用poetry (推荐)
poetry install
```

### 3. 安装evalscope (OpenAI压测必需)
```bash
pip install evalscope
```

## 🚀 快速开始

### OpenAI API压测

```bash
# 基础压测
python loadpup/cli.py openai \
  --base_url "https://api.openai.com/v1" \
  --model "gpt-3.5-turbo" \
  --parallel "1;2;4" \
  --prompt_length 500 \
  --output_length 200

# 详细配置
python loadpup/cli.py openai \
  --base_url "https://your-api.com/v1" \
  --model "your-model" \
  --parallel "1;2;4;8" \
  --prompt_length 1000 \
  --output_length 500 \
  --temperature 0.7 \
  --output_dir "output/my_test"
```

### Dify API压测

```bash
# 基础压测
python loadpup/cli.py dify \
  --api_url "http://your-dify.com/v1/chat-messages" \
  --api_key "app-your-key" \
  --parallel "1;2;4" \
  --total_requests 100

# 使用自定义查询文件
python loadpup/cli.py dify \
  --api_url "http://your-dify.com/v1/chat-messages" \
  --api_key "app-your-key" \
  --parallel "2;4;8" \
  --query_file "queries.txt" \
  --total_requests 200 \
  --output_dir "output/dify_test"
```

## 📊 测试报告

### 报告格式

LoadPup生成两种格式的详细报告：

1. **JSON格式** (`report_YYYYMMDD_HHMMSS.json`)
2. **Excel格式** (`report_YYYYMMDD_HHMMSS.xlsx`)
3. **汇总报告** (`summary_report_YYYYMMDD_HHMMSS.xlsx`) - 多并发对比

### OpenAI报告指标 (27个)

```json
{
  "模型": "gpt-3.5-turbo",
  "并行度": 4,
  "提示长度": 500,
  "输出长度": 200,
  "测试总时长(s)": 45.23,
  "总请求数": 40,
  "成功请求数": 40,
  "失败请求数": 0,
  "平均吞吐量(token/s)": 176.8,
  "平均QPS": 0.88,
  "平均延迟(s)": 4.52,
  "首token平均延迟(s)": 1.23,
  "单token平均延迟(s)": 0.015,
  "平均输入token数": 500,
  "平均输出token数": 200,
  "P50延迟(s)": 4.31,
  "P50首token延迟(s)": 1.18,
  "P50单token延迟(s)": 0.014,
  "P90延迟(s)": 5.67,
  "P90首token延迟(s)": 1.45,
  "P90单token延迟(s)": 0.018,
  "P99延迟(s)": 6.23,
  "P99首token延迟(s)": 1.67,
  "P99单token延迟(s)": 0.021,
  "API URL": "https://api.openai.com/v1",
  "温度": 0.7,
  "流式输出": true
}
```

### Dify报告指标 (29个)

Dify报告包含所有OpenAI指标，plus：
- 查询文件路径
- 查询数量统计
- Dify特有的API响应字段

## 📁 项目结构

```
LoadPup/
├── loadpup/                    # 主要源码包
│   ├── __init__.py            # 包初始化和公共接口
│   ├── benchmark_base.py      # 压测基类，定义通用接口
│   ├── openai_benchmark.py    # OpenAI API压测实现
│   ├── dify_benchmark.py      # Dify API压测实现
│   ├── main.py               # 主管理器和配置工厂
│   └── cli.py                # 命令行接口
├── output/                    # 测试结果输出目录
│   ├── openai/               # OpenAI测试结果
│   └── dify/                 # Dify测试结果
├── README.md                 # 项目文档
├── requirements.txt          # 依赖列表
├── pyproject.toml           # Poetry配置
└── LICENSE                  # 开源协议
```

## ⚙️ 高级配置

### 自定义查询文件 (Dify)

创建`queries.txt`文件，每行一个查询：

```text
请介绍一下人工智能的发展历史
解释一下机器学习和深度学习的区别
请简述自然语言处理的应用场景
描述一下大语言模型的工作原理
```

### 环境变量配置

```bash
# 设置默认的tokenizer路径
export TOKENIZER_PATH="/path/to/your/tokenizer"

# 设置默认输出目录
export OUTPUT_DIR="/path/to/output"
```

### 批量测试脚本

```bash
#!/bin/bash
# 多API对比测试

# OpenAI测试
python loadpup/cli.py openai \
  --base_url "https://api.openai.com/v1" \
  --model "gpt-3.5-turbo" \
  --parallel "1;2;4;8" \
  --output_dir "comparison/openai"

# Dify测试
python loadpup/cli.py dify \
  --api_url "http://your-dify.com/v1/chat-messages" \
  --api_key "your-key" \
  --parallel "1;2;4;8" \
  --output_dir "comparison/dify"
```

## 🔍 性能优化建议

### 1. 并发数设置
- 从小并发开始：1 → 2 → 4 → 8 → 16
- 观察系统资源使用情况
- 避免过高并发导致的资源耗尽

### 2. 网络优化
- 确保网络带宽充足
- 考虑使用内网环境测试
- 监控网络延迟对结果的影响

### 3. 系统资源
- 监控CPU和内存使用率
- 适当调整请求超时时间
- 考虑使用更高配置的测试机器

## 🐛 故障排除

### 常见问题

1. **ModuleNotFoundError: No module named 'evalscope'**
   ```bash
   pip install evalscope
   ```

2. **请求超时**
   ```python
   # 检查网络连接和API服务状态
   # 增加timeout参数或降低并发数
   ```

3. **Token计数不准确**
   ```bash
   # 安装transformers库
   pip install transformers
   # 或指定正确的tokenizer路径
   ```

4. **日志重复输出**
   - 已修复，每个logger实例只保留一份handler

### 调试模式

```bash
# 启用详细日志
python loadpup/cli.py openai --debug \
  --base_url "https://api.openai.com/v1" \
  --model "gpt-3.5-turbo" \
  --parallel "1"
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发环境设置

```bash
# 使用poetry管理依赖
poetry install --dev

# 运行测试
python -m pytest tests/

# 代码格式化
black loadpup/
isort loadpup/
```

## 📄 开源协议

本项目采用 Apache 2.0 协议 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [evalscope](https://github.com/modelscope/evalscope) - OpenAI压测核心引擎
- [requests](https://requests.readthedocs.io/) - HTTP请求库
- [pandas](https://pandas.pydata.org/) - 数据处理库
- [numpy](https://numpy.org/) - 数值计算库

## 📧 联系方式

- 项目主页: [https://github.com/anonNo2/LoadPup](https://github.com/anonNo2/LoadPup)
- 问题反馈: [GitHub Issues](https://github.com/anonNo2/LoadPup/issues)
- 邮件: anon2010@163.com

---

**LoadPup** - 让API性能测试更简单、更专业、更准确！ 🚀 