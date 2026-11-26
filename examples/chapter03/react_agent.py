"""ReAct：让模型根据工具观察结果动态决定下一步行动。"""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


def ask_for_action(messages: list[dict]) -> dict:
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)


def search_knowledge(query: str) -> str:
    knowledge = {
        "Agent": "Agent 能够围绕目标动态选择行动、调用工具，并根据观察结果推进任务。",
        "Workflow": "Workflow 通过预先定义的步骤和控制逻辑组织任务执行。",
        "ReAct": "ReAct 通过 Reason、Act、Observe 循环，让模型根据工具返回结果决定下一步。",
    }
    for key, value in knowledge.items():
        if key.lower() in query.lower():
            return value
    return "知识库中没有找到直接匹配的内容。"


def get_product_info(product_name: str) -> str:
    products = {
        "Agent平台": "支持模型接入、工具调用和工作流编排。",
        "知识库系统": "支持文档导入、向量检索和知识问答。",
    }
    return products.get(product_name, "没有找到对应产品信息。")


TOOLS = {
    "search": search_knowledge,
    "product": get_product_info,
}


def run_react_agent(question: str, max_steps: int = 6) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个 ReAct Agent。根据当前任务和观察结果决定下一步行动。"
                "只能返回 JSON。需要查询知识时返回 "
                '{"action":"search","input":"查询内容"}；'
                "需要查询产品时返回 "
                '{"action":"product","input":"产品名称"}；'
                '任务完成时返回 {"action":"finish","answer":"最终回答"}。'
                "每次只选择一个动作，不要编造工具观察结果。"
            ),
        },
        {"role": "user", "content": question},
    ]

    observations = []

    for step in range(max_steps):
        decision = ask_for_action(messages)
        action = decision["action"]
        print("第", step + 1, "轮决策：", decision)

        if action == "finish":
            answer = decision["answer"]
            print("最终答案：", answer)
            return answer

        observation = TOOLS[action](decision["input"])
        observations.append(observation)
        print("工具观察：", observation)

        messages.append({"role": "assistant", "content": json.dumps(decision, ensure_ascii=False)})
        messages.append({
            "role": "user",
            "content": "工具执行结果 Observation：" + observation + "。请根据结果决定下一步行动。",
        })

    return "已达到最大执行轮数，停止 Agent。当前观察结果：" + " ".join(observations)


if __name__ == "__main__":
    run_react_agent("请解释 Agent 和 Workflow 的区别，并查询 Agent 平台可以提供哪些能力。")
