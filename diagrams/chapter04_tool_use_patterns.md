# 第4章工具调用与能力扩展模式

## Function Calling 与 Tool Registry

~~~mermaid
sequenceDiagram
    participant A as Agent 应用
    participant M as 模型
    participant R as Tool Registry
    participant T as 工具
    A->>M: 用户任务 + 已授权工具 Schema
    M-->>A: 结构化调用请求
    A->>R: 验证名称和参数
    R-->>A: 执行器
    A->>T: 调用
    T-->>A: 结果
    A->>M: 带调用 ID 的工具结果
    M-->>A: 最终回答或下一次调用
~~~

## MCP Host/Client/Server

~~~mermaid
flowchart LR
    U[用户] --> H[Host / Agent 应用]
    H --> M[模型]
    H --> C1[MCP Client]
    H --> C2[MCP Client]
    C1 <-->|MCP| S1[MCP Server: 知识库]
    C2 <-->|MCP| S2[MCP Server: 业务工具]
    S1 --> R[(资源)]
    S2 --> B[(业务系统)]
~~~

## 分层职责

~~~mermaid
flowchart TD
    A[模型：提出候选工具调用] --> B[应用：验证 Schema 与身份权限]
    B --> C[Registry/Client：解析允许的能力]
    C --> D[工具或 MCP Server：执行操作]
    D --> E[应用：记录结果并控制预算]
    E --> F[模型：整合观察或继续调用]
~~~
