"""演示 Agent Loop：模型决定下一步动作，程序执行工具并回传观察结果。

本示例使用规则决策模拟 LLM，确保无需 API Key 即可运行。
运行：python agent_loop_demo.py
"""
from dataclasses import dataclass, field


def search_knowledge(query: str) -> str:
    """模拟知识库搜索工具。"""
    knowledge = {
        "agent": "Agent 是能够围绕目标选择行动、调用工具并根据观察结果推进任务的系统。",
        "workflow": "Workflow 使用预先定义的步骤和控制逻辑组织任务。",
    }
    for key, value in knowledge.items():
        if key in query.lower():
            return value
    return "知识库中没有找到直接匹配的内容。"


@dataclass
class AgentState:
    question: str
    observations: list[str] = field(default_factory=list)
    finished: bool = False


def decide(state: AgentState) -> dict:
    """用简单规则模拟模型决策。"""
    if not state.observations:
        return {"action": "search", "input": state.question}
    return {"action": "finish", "input": ""}


def run_agent(question: str, max_steps: int = 5) -> str:
    state = AgentState(question=question)

    for step in range(max_steps):
        print(f"\n[第 {step + 1} 轮] 当前问题：{state.question}")
        decision = decide(state)
        print("决策：", decision)

        if decision["action"] == "search":
            result = search_knowledge(decision["input"])
            state.observations.append(result)
            print("工具观察：", result)
        elif decision["action"] == "finish":
            state.finished = True
            break
        else:
            raise ValueError(f"未知动作：{decision['action']}")

    if not state.finished and len(state.observations) >= max_steps:
        print("达到最大执行轮数，停止循环。")

    return "\n".join(state.observations) or "没有获得结果。"


if __name__ == "__main__":
    answer = run_agent("什么是 Agent？")
    print("\n最终结果：")
    print(answer)
