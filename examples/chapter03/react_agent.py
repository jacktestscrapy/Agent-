"""ReAct：让模型根据工具观察结果动态决定下一步行动。"""
# 标准库：json 用于解析模型的结构化动作，os 用于读取环境变量。
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 加载项目根目录或当前工作目录中的 .env 配置，并初始化 DeepSeek 兼容客户端。
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


# 请求模型根据当前对话状态选择下一步动作，并将 JSON 响应解析为字典。
def ask_for_action(messages: list[dict]) -> dict:
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)


# 模拟知识库检索工具：根据关键词返回匹配的知识片段。
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


# 模拟产品查询工具：根据产品名称返回对应的产品能力说明。
def get_product_info(product_name: str) -> str:
    products = {
        "Agent平台": "支持模型接入、工具调用和工作流编排。",
        "知识库系统": "支持文档导入、向量检索和知识问答。",
    }
    return products.get(product_name, "没有找到对应产品信息。")


# 工具注册表：模型只能选择这里登记的工具名称，程序再映射到对应函数。
TOOLS = {
    "search": search_knowledge,
    "product": get_product_info,
}


# ReAct 主循环：模型决策、程序调用工具、观察结果，再进入下一轮决策。
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

    # 限制最大循环轮数，避免模型持续调用工具导致成本失控。
    for step in range(max_steps):
        decision = ask_for_action(messages)
        action = decision["action"]
        print("第", step + 1, "轮决策：", decision)

        # 模型明确返回 finish 时，结束循环并返回最终答案。
        if action == "finish":
            answer = decision["answer"]
            print("最终答案：", answer)
            return answer

        # 由程序执行白名单工具，并把工具返回值作为 Observation 反馈给模型。
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
