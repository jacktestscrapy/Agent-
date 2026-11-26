# 第3章演示代码

本章提供三个独立示例和一个综合组合示例：

- `react_agent.py`：ReAct 推理、行动与观察循环。模型根据工具观察结果动态选择下一步，示例工具为本地知识库查询和产品信息查询。
- `plan_execute.py`：Plan-and-Execute 规划与执行。模型先生成任务计划，再由执行器逐项执行；当任务无法完成时，Replanner 根据执行结果调整后续计划。
- `reflection.py`：Reflection 反思与修正。先生成技术方案，再由独立评价步骤检查完整性、正确性、可行性和安全性，最后根据反馈修正。
- `combined_diagnostic_agent.py`：综合企业技术问题诊断案例，组合 Plan-and-Execute、ReAct 和 Reflection。

## 环境准备

Python 3.10+，在仓库根目录执行：

```bash
pip install -r requirements.txt
```

在项目根目录创建 `.env` 文件：

```dotenv
DEEPSEEK_API_KEY=你的_API_Key
DEEPSEEK_MODEL=deepseek-chat
```

所有示例均通过 `python-dotenv` 加载项目根目录的 `.env`，API Key 和模型名称不写在代码中。

## 运行示例

请在仓库根目录执行：

```bash
python examples/chapter03/react_agent.py
python examples/chapter03/plan_execute.py
python examples/chapter03/reflection.py
python examples/chapter03/combined_diagnostic_agent.py
```

## 示例观察重点

### ReAct

观察模型每一轮返回的 action，程序根据 action 映射到已注册工具，执行后将 Observation 回传给模型。模型可以继续调用工具，也可以选择 finish。

### Plan-and-Execute

观察 Planner 生成的任务列表、Executor 的逐项执行结果，以及任务失败时 Replanner 如何根据已完成任务和失败原因调整剩余计划。

### Reflection

观察 Generator、Reflector、Feedback 和 Refiner 的职责区别。反思轮数由 `max_iterations` 控制，避免无限修改。

### 综合案例

案例模拟 FastAPI 服务部署后无法连接 MySQL 的问题。工具返回的是教学用本地模拟信息，不会连接真实服务器、读取真实配置或修改系统。观察 Planner 如何拆分任务，ReAct 如何根据工具结果继续排查，以及 Reflection 如何检查诊断报告中的依据和建议。

## 统一代码规范

所有 DeepSeek 示例统一采用以下客户端初始化方式：

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)
```

模型名称通过 `os.getenv("DEEPSEEK_MODEL")` 读取。示例重点展示设计模式本身，真实生产系统还应根据业务需要补充超时、限流、重试、结构化输出校验、日志、持久化状态和权限控制。

请勿将包含真实密钥的 `.env` 文件提交到版本库。
