# 第2章演示代码

本章提供四个可运行示例：

- `prompt_chaining.py`：AI 文章生成链，包含大纲生成、正文撰写和编辑润色。
- `routing.py`：智能客服意图识别与处理器路由。
- `parallelization.py`：并行执行多维度市场分析并汇总。
- `workflow_composition.py`：需求理解、并行分析、综合汇总的组合工作流。

## 环境准备

Python 3.10+，在仓库根目录执行：

```bash
pip install -r requirements.txt
```

在项目根目录创建 `.env` 文件，填写以下配置后运行：

```dotenv
DEEPSEEK_API_KEY=你的_API_Key
DEEPSEEK_MODEL=deepseek-chat
```

代码通过 `python-dotenv` 自动加载 `.env`，API Key 和模型名称均不写死在代码中。

```bash
python examples/chapter02/prompt_chaining.py
python examples/chapter02/routing.py
python examples/chapter02/parallelization.py
python examples/chapter02/workflow_composition.py
```

所有示例统一使用 DeepSeek OpenAI 兼容客户端；API Key 和模型名称从 `.env` 加载：

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

response = client.chat.completions.create(
    model=os.getenv("DEEPSEEK_MODEL"),
    messages=[{"role": "user", "content": "你好"}]
)
```

说明：示例重点展示模式结构，真实生产系统应补充超时、限流、重试、结构化输出校验、日志和权限控制。


`.env` 文件示例：

```dotenv
DEEPSEEK_API_KEY=你的_API_Key
DEEPSEEK_MODEL=deepseek-chat
```

请勿将包含真实密钥的 `.env` 文件提交到版本库。
