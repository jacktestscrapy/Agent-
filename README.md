# Agent设计模式：从单 Agent 到企业级多智能体系统

> 面向 AI Agent 开发者、AI 工程师和企业应用开发人员的系统化学习与实践项目。

本仓库围绕 Agent 设计模式展开，结合理论讲解、架构图、Python 实现、实践案例和综合项目，帮助学习者理解常见 Agent 模式，掌握模式选择、组合与落地方法。

## 学习目标

- 理解 Agent 的核心组成、运行机制与设计模式体系。
- 掌握 Workflow、动态执行、工具调用、任务拆分、Multi-Agent、Memory、评估优化、安全协作等模式。
- 学会根据任务复杂度、可靠性、成本与维护性选择合适的 Agent 架构。
- 使用 Python、DeepSeek API 与 LangGraph 等工具实现可运行的 Agent 应用。
- 综合构建具备规划、开发、测试、评审与人工审批能力的 AI 软件开发 Agent。

## 课程内容

| 章节 | 内容 |
|---|---|
| 第1章 | Agent设计模式基础 |
| 第2章 | 基础工作流设计模式：Prompt Chaining、Routing、Parallelization |
| 第3章 | 动态Agent执行模式：ReAct、Plan-and-Execute、Reflection |
| 第4章 | 工具调用与能力扩展模式：Tool-Use、Function Calling、Tool Registry、MCP |
| 第5章 | 任务调度与复杂任务拆分：Task Decomposition、Orchestrator-Workers、Supervisor、Handoff、Task Queue |
| 第6章 | Multi-Agent协作模式：Supervisor、Swarm、Debate、Group Collaboration |
| 第7章 | Agent Memory与知识管理模式 |
| 第8章 | Agent质量控制与优化模式：Evaluator-Optimizer、Self-Verification、Retry、Fallback |
| 第9章 | Agent安全与人工协同模式：Human-in-the-Loop、Guardrails、Permission、Audit |
| 第10章 | Agent模式组合与架构设计 |
| 第11章 | 综合实战：AI软件开发Agent |

## 综合项目：AI软件开发 Agent

综合项目将整合课程中的设计模式，构建一个协作式 AI 软件开发系统。根据开发需求完成需求分析、架构设计、任务拆分、代码实现、测试、代码审查、质量评估与交付。

预期角色包括：

- Router：识别任务与分发流程。
- Development Orchestrator：协调开发任务与 Agent。
- Requirement Agent：分析需求与验收标准。
- Architecture Agent：设计系统架构与技术方案。
- Backend / Frontend / Database Developer Agents：执行开发任务。
- Test Agent：执行测试与反馈。
- Code Review Agent：审查代码与质量。
- Shared State：维护任务、上下文、执行结果与协作状态。

项目将关注可执行工具、文件与代码仓库操作、测试反馈、自动修复、权限控制及人工审核等环节。

## 技术方向

- Python
- DeepSeek API
- LangGraph / LangChain
- Tool Calling / MCP
- Agent State、Memory 与任务调度
- 自动化测试、评估与可观测性

具体依赖与版本将随示例项目逐步更新。

## 仓库规划

```text
.
├── README.md                 # 项目介绍与学习导航
├── docs/                     # 分章节教程
├── diagrams/                  # 架构图、流程图与模式图
├── examples/                  # 分章节演示代码
├── exercises/                 # 练习与实践任务
├── projects/
│   └── ai-software-development-agent/  # 综合项目
├── references/                # 外部资料与参考来源
└── requirements.txt            # 项目依赖（逐步完善）
```

目录将随着内容的生成与审核逐步完善。

## 学习方式

1. 阅读章节内容，理解模式的动机、流程、边界与优缺点。
2. 查看架构图和代码示例，运行并观察 Agent 的执行过程。
3. 完成章节练习，尝试不同模式及组合。
4. 将各章节模式应用到综合项目中。
5. 对实现进行测试、评估与迭代优化。

## 参考资料

学习内容将结合官方文档、研究论文及工程实践，并在各章节注明相关出处。以下为项目的基础参考资料：

- [STORM: Self-Organizing Knowledge Retrieval and Synthesis](https://arxiv.org/abs/2402.14207)
- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [Building Effective AI Agents — Architecture Patterns](https://claude.com/resources/guides/building-effective-ai-agents/common-architecture-patterns)

## 内容状态

课程内容采用逐步研究、生成、审核与完善的方式维护。章节、代码与综合项目将陆续更新；尚未发布的内容不代表已经完成或经过验证。

---

欢迎通过 Issues 交流学习问题、改进建议与实践反馈。
