# 第3章 动态 Agent 执行模式

## 学习目标
- 理解 ReAct、Plan-and-Execute、Reflection 的设计动机和边界。
- 使用 DeepSeek API 实现工具循环、任务规划和结果反思。
- 组合三种模式构建受控的企业技术诊断流程。
- 为 Agent 设置预算、状态、权限和停止条件。

## 3.1 从 Workflow 到动态 Agent
固定 Workflow 适合流程稳定、步骤明确的任务；当工具选择、信息需求和后续步骤无法预知时，动态 Agent 可以根据当前状态与观察结果调整行动。

| 维度 | Workflow | 动态 Agent |
|---|---|---|
| 执行路径 | 预先定义 | 根据状态调整 |
| 决策 | 程序规则为主 | 模型决策与程序约束结合 |
| 可预测性 | 较高 | 相对较低 |
| 调试 | 节点和边 | 还需记录模型决策与工具轨迹 |
| 适用任务 | 稳定重复任务 | 信息不完整、步骤不确定任务 |

动态不等于放任模型控制程序。LLM 负责理解、规划和提出行动；Python 负责工具执行、参数校验、状态管理、权限与预算；高风险操作由业务规则或人工审批控制。

## 3.2 ReAct：推理、行动与观察
ReAct（Reasoning and Acting）通过 Reason → Act → Observe 循环，让模型根据工具观察结果决定下一步。

~~~mermaid
flowchart TD
 A[用户目标] --> B[模型决策]
 B --> C{动作类型}
 C -->|工具调用| D[程序校验参数]
 D --> E[执行工具]
 E --> F[观察结果]
 F --> B
 C -->|完成| G[输出答案]
~~~

步骤：
1. 接收目标并构建上下文。
2. 模型选择工具或决定结束。
3. 程序检查工具名与参数。
4. 程序执行工具并返回观察结果。
5. 模型依据观察继续行动或结束。

模型只生成工具调用意图，程序通过白名单映射执行工具，禁止执行模型生成的任意代码。

适用场景：故障排查、知识检索、多轮信息查询和探索型任务。

主要风险与控制：
- 无限循环：最大步数、超时和预算。
- 重复调用：记录工具调用历史，检测重复参数。
- 错误工具：白名单、清晰描述和参数校验。
- 错误结论：保留证据，重要事实进行外部验证。

## 3.3 Plan-and-Execute：先规划，再执行
该模式先将复杂目标拆解为结构化子任务，再逐项执行。常见组件：
- Planner：生成任务计划。
- Executor：执行单个任务，可调用函数或 ReAct 子 Agent。
- State：记录任务状态、结果和错误。
- Replanner：在失败或环境变化时调整计划。

~~~mermaid
flowchart TD
 A[复杂目标] --> B[Planner]
 B --> C[结构化计划]
 C --> D[Executor]
 D --> E{执行成功}
 E -->|是| F[更新状态]
 E -->|否| G[Replanner]
 G --> D
 F --> H{全部完成}
 H -->|否| D
 H -->|是| I[汇总交付]
~~~

计划至少包含任务 ID、描述、依赖和状态。工程实现应检查 ID 唯一性、依赖有效性、循环依赖及任务范围。

~~~json
{
  "goal": "诊断 FastAPI 无法连接 MySQL",
  "tasks": [
    {"id": "T1", "task": "检查连接配置", "depends_on": [], "status": "pending"},
    {"id": "T2", "task": "检查容器网络", "depends_on": ["T1"], "status": "pending"},
    {"id": "T3", "task": "汇总诊断结论", "depends_on": ["T1", "T2"], "status": "pending"}
  ]
}
~~~

适用场景：软件开发、研究分析、复杂业务流程。计划不是不可变指令，执行反馈可能要求重新规划。

## 3.4 Reflection：评价与修正
Reflection 通过评价初始结果、生成反馈并据此修正，建立质量闭环。

~~~mermaid
flowchart TD
 A[需求] --> B[Generator生成]
 B --> C[Evaluator评价]
 C --> D{达到质量标准}
 D -->|否| E[Refiner修正]
 E --> C
 D -->|是| F[输出结果]
~~~

- Generator：生成初稿或执行结果。
- Evaluator / Reflector：按明确标准评价。
- Feedback：记录缺陷和修改方向。
- Refiner：结合反馈修正。

技术方案可评价完整性、正确性、可行性和安全性；代码还应结合语法检查、单元测试和静态分析。模型自评不能代替外部验证，避免让错误结果只是表达得更流畅。

## 3.5 模式比较与组合
| 模式 | 核心问题 | 典型用途 |
|---|---|---|
| ReAct | 下一步做什么 | 搜索、诊断、工具探索 |
| Plan-and-Execute | 复杂目标如何拆解 | 项目开发、研究任务 |
| Reflection | 结果是否足够好 | 代码、报告、方案评审 |

常见组合：
- Plan-and-Execute + ReAct：全局由 Planner 管理，局部不确定任务交给 ReAct。
- ReAct + Reflection：动态收集证据后检查结论。
- Plan-and-Execute + Reflection：执行子任务后评价质量，必要时返工。
- 三者组合：规划全局任务、动态执行局部步骤、评价最终交付。

## 3.6 企业级工程控制
### 预算与停止条件
设置最大模型轮数、工具调用次数、执行时长、重试次数和 Token 预算。达到预算应停止并返回部分结果与未完成原因。

### 状态与恢复
保存 task_id、goal、当前步骤、任务列表、工具调用摘要、观察结果、错误、预算消耗和最终状态。长任务可持久化到数据库或检查点存储。

### 权限与审批
| 操作 | 建议策略 |
|---|---|
| 查询公开知识库 | 自动执行 |
| 查询业务数据 | 校验用户权限 |
| 修改业务数据 | 规则校验并审批 |
| 删除文件、发布代码 | 人工确认与审计 |
| 任意 Shell 命令 | 默认禁止，采用受限白名单 |

### 可观测性
记录任务 ID、模型名、提示词版本、动作、工具名、参数摘要、结果摘要、耗时、Token、错误和状态。日志不得包含 API Key、密码等敏感信息。

## 3.7 综合案例：企业技术问题诊断 Agent
业务问题：员工反馈 FastAPI 服务部署后无法连接 MySQL。

1. Planner 拆解为检查连接配置、容器网络、错误日志和整理报告。
2. Executor 执行可控的只读查询。
3. 线索不足时，ReAct 决定继续检查网络或查询知识库。
4. Reflection 检查结论是否有证据支撑、是否区分事实与推测、建议是否安全。
5. 输出原因、证据、修复建议、验证步骤和未确认事项。

示例线索：应用运行在 Docker 容器内，数据库地址配置为 localhost。容器内 localhost 指向应用容器自身，而非另一个 MySQL 容器。该结论仍需结合 Docker 网络、服务定义和实际配置验证，不能仅凭单一线索断言。

## 3.8 本章小结
- ReAct：推理、行动、观察的动态循环。
- Plan-and-Execute：先生成结构化计划，再执行并根据反馈调整。
- Reflection：按明确标准评价结果并修正。
- 企业应用通常组合使用这些模式，并由程序控制权限、状态和预算。

**设计原则：** 流程稳定时优先使用 Workflow；只有动态决策、复杂规划或质量反馈确实带来收益时，再引入 Agent 模式。

## 参考资料
1. [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
2. [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
3. [Plan-and-Solve Prompting](https://arxiv.org/abs/2305.04091)（提示策略研究，不等同于完整 Plan-and-Execute 架构）
4. [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
5. [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
