# 第三章架构图源文件

## ReAct
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

## Plan-and-Execute
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

## Reflection
~~~mermaid
flowchart TD
 A[需求] --> B[Generator]
 B --> C[Evaluator]
 C --> D{达到质量标准}
 D -->|否| E[Refiner]
 E --> C
 D -->|是| F[输出结果]
~~~

## 三种模式组合
~~~mermaid
flowchart TD
 A[用户目标] --> B[Planner]
 B --> C[Executor]
 C --> D[ReAct工具执行]
 D --> E[执行结果]
 E --> F[Reflection]
 F --> G{质量通过}
 G -->|否| B
 G -->|是| H[最终交付]
~~~
