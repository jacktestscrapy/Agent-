"""对比固定 Workflow 与动态 Agent 的执行方式。
运行：python workflow_vs_agent.py
"""


def workflow_answer(question: str) -> str:
    # 流程由开发者预先确定：分类 -> 检索 -> 组织答案
    category = "产品问题" if "产品" in question else "通用问题"
    knowledge = {
        "产品问题": "请先检查产品版本、配置和运行日志。",
        "通用问题": "请补充问题背景、预期结果和实际错误信息。",
    }
    retrieved = knowledge[category]
    return f"[Workflow]\n分类：{category}\n检索结果：{retrieved}"


def agent_answer(question: str) -> str:
    # 用规则模拟模型的动态选择：根据问题决定是否查询不同工具。
    actions = []
    if "报错" in question or "错误" in question:
        actions.append("查询错误知识库")
    if "版本" in question:
        actions.append("查询版本信息")
    if not actions:
        actions.append("请求用户补充信息")

    return "[Agent 模拟决策]\n" + "\n".join(
        f"{index}. {action}" for index, action in enumerate(actions, 1)
    )


if __name__ == "__main__":
    user_question = "产品升级后报错，当前版本是多少？"
    print(workflow_answer(user_question))
    print()
    print(agent_answer(user_question))
