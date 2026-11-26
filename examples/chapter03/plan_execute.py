from common import ask_deepseek, parse_json


def create_plan(goal):
    messages = [
        {
            "role": "system",
            "content": (
                "你是任务规划器。将目标拆解为3到5个可执行任务。"
                "只返回JSON：{tasks:[{id,task,description,depends_on}]}。"
                "任务必须是只读分析或生成建议，不得修改生产系统。"
            )
        },
        {"role": "user", "content": goal}
    ]
    return parse_json(ask_deepseek(messages))


def execute_task(task):
    messages = [
        {"role": "system", "content": "你是企业技术分析执行器，区分事实与假设。"},
        {
            "role": "user",
            "content": "任务：" + task["task"] + "。说明：" + task["description"]
        }
    ]
    return ask_deepseek(messages)


def run_plan(goal):
    plan = create_plan(goal)
    completed = set()
    results = []

    for task in plan["tasks"]:
        dependencies = task.get("depends_on", [])
        if not set(dependencies).issubset(completed):
            raise ValueError("任务依赖尚未完成：" + task["id"])

        result = execute_task(task)
        completed.add(task["id"])
        results.append({"task": task["task"], "result": result})
        print("已完成", task["id"], task["task"])

    return results


if __name__ == "__main__":
    goal = "分析 FastAPI 服务在 Docker 环境中无法连接 MySQL 的可能原因，并提出安全排查步骤。"
    for item in run_plan(goal):
        print(item["task"], item["result"])
