# 第三章演示代码

| 文件 | 说明 |
|---|---|
| common.py | DeepSeek 客户端与 JSON 解析 |
| react_agent.py | ReAct 工具调用循环 |
| plan_execute.py | Planner 与 Executor |
| reflection.py | 生成、评审、修正闭环 |
| combined_diagnostic_agent.py | 三种模式组合的技术诊断案例 |

## 环境准备

在项目根目录创建 .env：

~~~dotenv
DEEPSEEK_API_KEY=你的DeepSeek_API_Key
DEEPSEEK_MODEL=deepseek-chat
~~~

安装依赖：

~~~bash
pip install -r requirements.txt
~~~

从项目根目录运行：

~~~bash
python examples/chapter03/react_agent.py
python examples/chapter03/plan_execute.py
python examples/chapter03/reflection.py
python examples/chapter03/combined_diagnostic_agent.py
~~~

模型 API Key 与模型名称均从环境变量读取。示例工具只访问代码中的模拟知识和配置，不会连接真实企业系统。

课堂建议：先单独运行三个模式，再运行综合案例，观察规划、动态行动与质量评价如何衔接。正式项目还应增加结构化输出约束、异常重试、超时、状态持久化、权限校验和审计。
