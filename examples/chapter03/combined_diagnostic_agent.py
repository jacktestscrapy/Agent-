from common import ask_deepseek, parse_json
from react_agent import run_react
from reflection import reflect_solution, refine_solution


def create_diagnostic_plan(question):
    messages = [
        {
            "role": "system",
            "content": "将问题拆成3个只读排查任务，只返回JSON：{tasks:[{id,task,description,depends_on}]}。"
        },
        {"role": "user", "content": question}
    ]
    return parse_json(ask_deepseek(messages))


def run_diagnostic(question):
    plan = create_diagnostic_plan(question)
    task_notes = []

    for task in plan["tasks"]:
        result = run_react(
            "请完成只读诊断任务：" + task["task"] + "。任务说明：" + task["description"],
            max_steps=3
        )
        task_notes.append("任务：" + task["task"] + " 结果：" + result)

    draft = ask_deepseek([
        {
            "role": "system",
            "content": "你是技术诊断报告撰写员。区分已知事实、推断和待验证事项。"
        },
        {
            "role": "user",
            "content": "用户问题：" + question + " 诊断记录：" + " ".join(task_notes)
        }
    ])

    feedback = reflect_solution(draft)
    if "PASS" not in feedback.upper():
        draft = refine_solution(draft, feedback)

    return draft


if __name__ == "__main__":
    question = "FastAPI 服务部署到 Docker 后无法连接 MySQL，请给出排查结论和验证步骤。"
    print(run_diagnostic(question))
