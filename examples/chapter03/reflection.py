from common import ask_deepseek


def generate_solution(requirement):
    return ask_deepseek([
        {"role": "system", "content": "你是企业架构师，请给出结构清晰、可执行的技术方案。"},
        {"role": "user", "content": requirement}
    ])


def reflect_solution(solution):
    return ask_deepseek([
        {
            "role": "system",
            "content": "你是严格的技术方案评审员。检查完整性、正确性、可行性和安全性。"
            "指出具体问题；若无关键缺陷，明确写出 PASS。"
        },
        {"role": "user", "content": "请评审以下方案：" + solution}
    ])


def refine_solution(solution, feedback):
    return ask_deepseek([
        {"role": "system", "content": "你是技术方案修订专家，只修复评审指出的问题。"},
        {
            "role": "user",
            "content": "原方案：" + solution + " 评审反馈：" + feedback + " 输出完整修订版。"
        }
    ])


def run_reflection(requirement, max_iterations=2):
    solution = generate_solution(requirement)

    for index in range(max_iterations):
        feedback = reflect_solution(solution)
        print("第", index + 1, "轮评审反馈", feedback)
        if "PASS" in feedback.upper():
            break
        solution = refine_solution(solution, feedback)

    return solution


if __name__ == "__main__":
    requirement = (
        "设计企业内部技术问题诊断助手，能够查询知识库、分析部署配置，"
        "输出诊断依据、修复建议和验证步骤。"
    )
    print(run_reflection(requirement))
