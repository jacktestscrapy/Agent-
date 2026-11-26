"""Reflection：生成初始方案，评价结果，再根据反馈进行修正。"""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


def ask_deepseek(messages: list[dict], temperature: float = 0.3) -> str:
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def generate_solution(requirement: str) -> str:
    messages = [
        {"role": "system", "content": "你是企业架构师，请给出结构清晰、可执行的技术方案。"},
        {
            "role": "user",
            "content": (
                "根据以下需求设计技术方案，并包含系统架构、核心模块、技术选型、"
                "权限安全、测试验收和部署方式。需求：" + requirement
            ),
        },
    ]
    return ask_deepseek(messages)


def reflect_solution(solution: str) -> dict:
    messages = [
        {
            "role": "system",
            "content": (
                "你是严格的技术方案评审员。检查完整性、正确性、可行性和安全性。"
                "只返回 JSON 对象，包含 score、passed、issues、suggestions。"
                "score 为 0 到 100 的整数；达到 85 分且没有关键问题时 passed 才为 true。"
            ),
        },
        {"role": "user", "content": "请评审以下方案：" + solution},
    ]
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)


def refine_solution(solution: str, feedback: dict) -> str:
    messages = [
        {"role": "system", "content": "你是技术方案修订专家，只修复评审指出的问题，保留原方案中合理的内容。"},
        {
            "role": "user",
            "content": (
                "原方案：" + solution
                + "。评审反馈：" + json.dumps(feedback, ensure_ascii=False)
                + "。请输出完整修订版技术方案。"
            ),
        },
    ]
    return ask_deepseek(messages)


def run_reflection(requirement: str, max_iterations: int = 2) -> dict:
    solution = generate_solution(requirement)
    history = []

    for index in range(max_iterations):
        feedback = reflect_solution(solution)
        history.append(feedback)
        print("第", index + 1, "轮评审反馈：", feedback)

        if feedback["passed"]:
            break

        solution = refine_solution(solution, feedback)
        print("第", index + 1, "轮修正完成。")

    return {"solution": solution, "history": history}


if __name__ == "__main__":
    requirement = (
        "设计一个企业内部知识库问答系统，支持文档上传、权限控制、"
        "检索问答和运行监控。"
    )
    result = run_reflection(requirement)
    print("最终技术方案：", result["solution"])
