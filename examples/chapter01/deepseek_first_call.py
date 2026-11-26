"""使用 DeepSeek 的 OpenAI 兼容接口完成一次 LLM 调用。

安装：pip install openai
设置环境变量 DEEPSEEK_API_KEY 后运行本文件。
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


def ask_deepseek(question: str) -> str:
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
            {"role": "system", "content": "你是一名严谨的 AI Agent 技术讲师。回答清晰、准确，并给出必要的例子。"},
            {"role": "user", "content": question},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


if __name__ == "__main__":
    print(ask_deepseek("用一个简单例子解释 Agent 和 Workflow 的区别。"))
