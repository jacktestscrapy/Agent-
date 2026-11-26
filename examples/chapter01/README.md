# 第1章演示代码

- `agent_loop_demo.py`：无需 API Key，使用规则模拟 Agent Loop。
- `workflow_vs_agent.py`：对比固定 Workflow 与动态 Agent 决策。
- `deepseek_first_call.py`：调用 DeepSeek OpenAI 兼容接口，需要配置 `DEEPSEEK_API_KEY`。

## 环境要求

建议 Python 3.10+，在仓库根目录执行：

```bash
pip install -r requirements.txt
python examples/chapter01/agent_loop_demo.py
python examples/chapter01/workflow_vs_agent.py
python examples/chapter01/deepseek_first_call.py
```

## DeepSeek 客户端统一规范

所有需要访问 DeepSeek 的演示代码统一采用以下初始化方式：

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)
```

请先设置环境变量 `DEEPSEEK_API_KEY`。示例的输出语句和返回值不使用 `\\n` 拼接换行，多个信息项直接使用空格分隔。
