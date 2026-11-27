"""Routing：先识别客服意图，再分发到对应处理器。"""
import os
from dotenv import load_dotenv
import json
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


def classify_intent(user_input: str) -> dict:
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
            {
                "role": "system",
                "content": '你是客服意图分类器。只能返回JSON对象，字段为category、reason。category只能是 presales、technical_support、order_query、other。',
            },
            {"role": "user", "content": user_input},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def presales_handler(user_input: str) -> str:
    return f"售前咨询处理：已收到问题「{user_input}」，将为你介绍产品功能、规格和购买方案。"


def technical_support_handler(user_input: str) -> str:
    return f"技术支持处理：已收到问题「{user_input}」，请提供产品型号、版本和错误日志以便排查。"


def order_query_handler(user_input: str) -> str:
    return f"订单查询处理：已收到请求「{user_input}」，请先完成身份验证，再查询订单状态。"


def fallback_handler(user_input: str) -> str:
    return f"暂时无法识别请求类型：「{user_input}」，请补充问题背景。"


ROUTES = {
    "presales": presales_handler,
    "technical_support": technical_support_handler,
    "order_query": order_query_handler,
    "other": fallback_handler,
}


def run_router(user_input: str) -> dict:
    route = classify_intent(user_input)
    handler = ROUTES.get(route["category"], fallback_handler)
    return {"route": route, "answer": handler(user_input)}


if __name__ == "__main__":
    request = "昨天购买的设备无法开机，应该怎么处理？"
    result = run_router(request)
    print("路由结果：", result["route"])
    print("处理结果：", result["answer"])
