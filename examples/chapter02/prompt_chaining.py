"""Prompt Chaining：生成文章大纲、撰写正文、编辑润色。"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


def ask_model(prompt: str) -> str:
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
            {"role": "system", "content": "你是一名专业内容策划与编辑。严格按用户要求完成当前步骤。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content or ""


def generate_outline(topic: str, audience: str) -> str:
    prompt = f"主题：{topic}。目标读者：{audience}。请生成一份结构清晰的文章大纲，包含标题、章节和每章要点。"
    return ask_model(prompt)


def write_article(topic: str, outline: str) -> str:
    prompt = f"请严格依据以下大纲撰写文章。主题：{topic}。大纲：{outline}。要求逻辑完整、表达清楚，不要编造具体数据。"
    return ask_model(prompt)


def edit_article(article: str) -> str:
    prompt = f"请编辑下面的文章，修正逻辑重复和表达问题，保留原有事实，不要新增未经证实的数据。文章：{article}"
    return ask_model(prompt)


def run_chain(topic: str, audience: str) -> dict:
    outline = generate_outline(topic, audience)
    article = write_article(topic, outline)
    final_article = edit_article(article)
    return {"outline": outline, "draft": article, "final": final_article}


if __name__ == "__main__":
    result = run_chain("企业如何从传统软件开发迈向 AI Agent 应用", "企业技术管理者和开发工程师")
    print("文章大纲：", result["outline"])
    print("最终文章：", result["final"])
