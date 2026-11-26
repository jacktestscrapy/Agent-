"""Plan-and-Execute：先生成任务计划，再逐项执行并按需重新规划。"""
# 标准库：json 用于处理计划数据，os 用于读取模型配置。
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 读取 .env 中的 DeepSeek 配置，创建 OpenAI 兼容客户端。
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


# 统一封装模型文本请求，供规划器、执行器和重新规划器复用。
def ask_deepseek(messages: list[dict], temperature: float = 0.3) -> str:
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


# Planner：把总体目标拆解为带有编号、描述和状态的任务列表。
def create_plan(goal: str) -> list[dict]:
    messages = [
        {
            "role": "system",
            "content": (
                "你是任务规划器。将目标拆解为可执行任务。"
                "只返回 JSON 对象，包含 tasks 数组；每个任务包含 id、task、description、status。"
                "status 初始值为 pending，任务应有清晰的先后顺序。"
            ),
        },
        {"role": "user", "content": goal},
    ]
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)["tasks"]


# Executor：执行一个具体子任务，并要求模型区分事实与假设。
def execute_task(task: dict) -> str:
    messages = [
        {"role": "system", "content": "你是企业技术分析执行器，按任务说明完成工作，区分事实与假设。"},
        {
            "role": "user",
            "content": (
                "任务名称：" + task["task"]
                + "。任务描述：" + task["description"]
                + "。请输出具体执行结果、关键结论和仍需确认的事项。不要编造数据。"
            ),
        },
    ]
    return ask_deepseek(messages)


# Replanner：结合已完成任务和失败信息，生成后续可执行的新计划。
def replan(goal: str, completed: list[dict], failed_task: dict, failure_result: str) -> list[dict]:
    messages = [
        {
            "role": "system",
            "content": (
                "你是 Replanner。根据执行结果调整剩余计划。"
                "只返回 JSON 对象，包含 tasks 数组；每项包含 id、task、description、status。"
                "只规划尚未完成且仍有必要的任务。"
            ),
        },
        {
            "role": "user",
            "content": (
                "原始目标：" + goal
                + "。已完成任务：" + json.dumps(completed, ensure_ascii=False)
                + "。失败任务：" + json.dumps(failed_task, ensure_ascii=False)
                + "。失败结果：" + failure_result
                + "。可以调整执行方式，也可以将无法获取的信息标记为待验证。"
            ),
        },
    ]
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)["tasks"]


# 主流程：创建计划、逐项执行、记录状态，并在遇到失败时尝试重新规划。
def run_plan(goal: str, max_replans: int = 1) -> dict:
    plan = create_plan(goal)
    results = []
    replan_count = 0
    index = 0

    print("初始计划：", plan)

    # 通过索引跟踪当前任务，重新规划后可以替换尚未执行的计划部分。
    while index < len(plan):
        task = plan[index]
        print("执行任务：", task["task"])
        result = execute_task(task)
        print("执行结果：", result)

        # 教学示例用文本关键词模拟失败判断；生产系统应使用结构化状态码。
        if "无法完成" in result or "无法获取" in result:
            # 只有剩余重新规划预算未耗尽时，才请求 Replanner 生成新计划。
            if replan_count < max_replans:
                remaining = replan(goal, results, task, result)
                plan = plan[:index] + remaining
                replan_count += 1
                print("重新规划后的任务：", remaining)
                continue
            task["status"] = "blocked"
        else:
            task["status"] = "completed"

        results.append({
            "task": task["task"],
            "status": task["status"],
            "result": result,
        })
        index += 1

    return {"plan": plan, "results": results}


if __name__ == "__main__":
    result = run_plan("制定一个企业 AI Agent 项目的开发计划，并完成需求分析、架构设计和测试方案。")
    for item in result["results"]:
        print(item["task"], item["status"], item["result"])
