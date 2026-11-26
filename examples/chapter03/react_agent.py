import json

from common import ask_deepseek, parse_json


KNOWLEDGE = {
    "localhost": "Docker 容器内的 localhost 指向当前容器自身。",
    "mysql": "MySQL 默认监听 3306 端口，容器间通信通常使用同一网络中的服务名。",
    "connection refused": "连接被拒绝通常表示目标端口没有服务监听，或连接被主动拒绝。"
}


def search_knowledge(query):
    matches = [value for key, value in KNOWLEDGE.items() if key.lower() in query.lower()]
    return " ".join(matches) if matches else "知识库没有找到直接匹配项。"


def inspect_demo_config(target):
    config = {
        "database_host": "localhost",
        "database_port": 3306,
        "runtime": "Docker container"
    }
    return json.dumps(config, ensure_ascii=False)


TOOLS = {
    "search_knowledge": search_knowledge,
    "inspect_demo_config": inspect_demo_config
}


def run_react(question, max_steps=5):
    messages = [
        {
            "role": "system",
            "content": (
                "你是企业技术诊断 Agent。每轮只返回 JSON："
                "{\"action\":\"工具名或finish\",\"input\":\"工具输入\",\"answer\":\"最终答案\"}。"
                "可用工具 search_knowledge(query) 和 inspect_demo_config(target)。"
                "只能选择给定工具，不得编造工具执行结果。"
            )
        },
        {"role": "user", "content": question}
    ]

    for step in range(max_steps):
        raw = ask_deepseek(messages)
        decision = parse_json(raw)
        action = decision["action"]

        if action == "finish":
            return decision.get("answer", "任务结束。")

        if action not in TOOLS:
            observation = "工具不存在，程序拒绝执行。"
        else:
            observation = TOOLS[action](decision.get("input", ""))

        print("Step", step + 1, "Action", action, "Observation", observation)
        messages.append({"role": "assistant", "content": raw})
        messages.append({
            "role": "user",
            "content": "工具执行结果：" + observation + "。请继续决策，或返回 finish。"
        })

    return "已达到最大执行轮数，停止继续调用工具。"


if __name__ == "__main__":
    print(run_react("FastAPI 部署在 Docker 后无法连接 MySQL，请检查可能原因。"))
