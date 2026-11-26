"""组合 Workflow：先提取问题，再并行分析，最后汇总。"""
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


def ask(prompt: str) -> str:
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
            {"role": "system", "content": "你是一名企业研究分析师。不要编造事实和数据。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


def understand_request(request: str) -> str:
    return ask(f"请提炼用户需求、研究主题和输出重点：{request}")


def analyze(topic: str, dimension: str) -> str:
    return ask(f"围绕以下主题，从{dimension}角度进行分析：{topic}")


def run_workflow(request: str) -> dict:
    requirement = understand_request(request)
    dimensions = ["市场趋势", "用户场景", "竞争方案"]
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            name: executor.submit(analyze, requirement, name)
            for name in dimensions
        }
        analyses = {name: future.result() for name, future in futures.items()}

    combined = " ".join(f"{name}：{content}" for name, content in analyses.items())
    final = ask(f"请整合以下内容，输出结构化报告，指出结论、风险和待验证问题：{combined}")
    return {"requirement": requirement, "analyses": analyses, "final": final}


if __name__ == "__main__":
    result = run_workflow("评估企业是否应该建设内部 AI Agent 开发平台")
    print("需求理解：", result["requirement"])
    print("最终报告：", result["final"])
