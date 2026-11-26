"""综合案例：组合 Plan-and-Execute、ReAct 和 Reflection 诊断技术问题。"""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


def ask_deepseek(messages: list[dict], temperature: float = 0.2) -> str:
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def create_plan(problem: str) -> list[dict]:
    messages = [
        {
            "role": "system",
            "content": (
                "你是技术问题诊断 Planner。将问题拆分为3到5个只读诊断任务。"
                "只返回 JSON 对象，包含 tasks 数组，每个任务包含 id、task、description、status。"
            ),
        },
        {"role": "user", "content": problem},
    ]
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)["tasks"]


def search_knowledge(query: str) -> str:
    return (
        "知识库记录：Docker 容器中的 localhost 指向当前容器自身。"
        "如果 FastAPI 和 MySQL 分属不同容器，应用应使用 MySQL 服务名或容器网络别名连接。"
        "修改连接地址前，应先确认 Docker 网络和服务配置。"
    )


def inspect_config(query: str) -> str:
    return "模拟配置检查结果：DB_HOST=localhost，DB_PORT=3306，DB_NAME=company。"


def check_service(query: str) -> str:
    return "模拟服务检查结果：MySQL 容器状态为 running，监听端口为 3306。"


def read_logs(query: str) -> str:
    return (
        "模拟日志内容：pymysql.err.OperationalError: "
        "Can't connect to MySQL server on 'localhost' (Connection refused)。"
    )


TOOLS = {
    "search_knowledge": search_knowledge,
    "inspect_config": inspect_config,
    "check_service": check_service,
    "read_logs": read_logs,
}


def run_react(task: str, max_steps: int = 5) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "你是技术诊断 ReAct Agent。根据当前任务和观察结果选择下一步工具。"
                "只能返回 JSON。可用动作：search_knowledge、inspect_config、"
                "check_service、read_logs。工具调用格式为 "
                '{"action":"工具名","input":"查询内容"}；'
                '完成时返回 {"action":"finish","answer":"本任务结论"}。'
                "每轮只选择一个动作，不要编造工具返回值。"
            ),
        },
        {"role": "user", "content": task},
    ]
    observations = []

    for step in range(max_steps):
        response = client.chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL"),
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        decision = json.loads(response.choices[0].message.content)
        print("ReAct 第", step + 1, "轮决策：", decision)

        if decision["action"] == "finish":
            return decision["answer"]

        observation = TOOLS[decision["action"]](decision["input"])
        observations.append(observation)
        print("工具观察：", observation)

        messages.append({"role": "assistant", "content": json.dumps(decision, ensure_ascii=False)})
        messages.append({
            "role": "user",
            "content": "Observation：" + observation + "。请继续判断下一步，或结束当前任务。",
        })

    return "达到最大执行轮数。已获得的观察结果：" + " ".join(observations)


def reflect_report(report: str) -> dict:
    messages = [
        {
            "role": "system",
            "content": (
                "你是独立的技术诊断评审员。检查报告是否有配置或日志依据，"
                "是否解释问题原因，是否给出可执行的修复建议、验证步骤和风险提示。"
                "只返回 JSON 对象，包含 passed、issues、suggestions。"
            ),
        },
        {"role": "user", "content": "请评审以下诊断报告：" + report},
    ]
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)


def refine_report(report: str, feedback: dict) -> str:
    messages = [
        {"role": "system", "content": "你是技术诊断报告撰写助手，根据评审意见完善报告。"},
        {
            "role": "user",
            "content": (
                "原报告：" + report
                + "。评审意见：" + json.dumps(feedback, ensure_ascii=False)
                + "。输出完整报告，区分已观察到的事实、原因判断、建议操作和待验证事项。"
                "不要声称已经修改真实环境。"
            ),
        },
    ]
    return ask_deepseek(messages)


def run_diagnosis(problem: str) -> dict:
    plan = create_plan(problem)
    print("Planner 生成的计划：", plan)

    task_results = []
    for task in plan:
        result = run_react(task["task"] + "。任务说明：" + task["description"])
        task_results.append({"task": task["task"], "result": result})

    evidence = " ".join(item["task"] + "：" + item["result"] for item in task_results)
    report = ask_deepseek([
        {
            "role": "system",
            "content": "你是企业技术问题诊断报告生成器。区分事实与推断，不要编造信息。",
        },
        {
            "role": "user",
            "content": (
                "根据以下诊断过程和观察结果生成报告，说明问题原因、修复建议、"
                "验证步骤和风险提示。诊断过程：" + evidence
            ),
        },
    ])

    feedback = reflect_report(report)
    print("Reflection 评价：", feedback)
    if not feedback["passed"]:
        report = refine_report(report, feedback)

    return {
        "plan": plan,
        "task_results": task_results,
        "report": report,
        "feedback": feedback,
    }


if __name__ == "__main__":
    result = run_diagnosis("FastAPI 服务部署后无法连接 MySQL，请排查原因并给出修复建议。")
    print("最终诊断报告：", result["report"])
