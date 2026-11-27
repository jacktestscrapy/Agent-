"""Parallelization：并行执行多个独立分析任务，再汇总结果。"""
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


def analyze_dimension(topic: str, dimension: str) -> str:
    prompt = f"请从「{dimension}」角度分析主题「{topic}」。列出关键观察、依据类型和不确定性。不要编造数据。"
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
            {"role": "system", "content": "你是一名严谨的商业研究分析师。区分事实、假设和推断。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


def summarize(topic: str, results: dict) -> str:
    sections = " ".join(f"{name}分析：{content}" for name, content in results.items())
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
            {"role": "system", "content": "你负责汇总多维度分析。指出共同结论、差异、风险和待验证事项。"},
            {"role": "user", "content": f"主题：{topic}。请汇总以下分析：{sections}"},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


def run_parallel_analysis(topic: str) -> dict:
    dimensions = ["市场机会", "用户需求", "竞争格局"]
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            dimension: executor.submit(analyze_dimension, topic, dimension)
            for dimension in dimensions
        }
        results = {dimension: future.result() for dimension, future in futures.items()}

    final_report = summarize(topic, results)
    return {"analyses": results, "summary": final_report}


if __name__ == "__main__":
    report = run_parallel_analysis("企业级 AI Agent 开发平台")
    for dimension, content in report["analyses"].items():
        print(dimension, "分析：", content)
    print("综合报告：", report["summary"])
