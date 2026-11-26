# 第1章演示代码

- `agent_loop_demo.py`：无需 API Key，使用规则模拟 Agent Loop。
- `workflow_vs_agent.py`：对比固定 Workflow 与动态 Agent 决策。
- `deepseek_first_call.py`：调用 DeepSeek OpenAI 兼容接口，需要配置 `DEEPSEEK_API_KEY`。

建议使用 Python 3.10+。运行前可安装：

```bash
pip install -r requirements.txt
```

在仓库根目录执行：

```bash
python examples/chapter01/agent_loop_demo.py
python examples/chapter01/workflow_vs_agent.py
python examples/chapter01/deepseek_first_call.py
```
