import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

MODEL = os.getenv("DEEPSEEK_MODEL")


def ask_deepseek(messages, temperature=0.2):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content


def parse_json(text):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        cleaned = cleaned.rsplit("```", 1)[0].strip()
    return json.loads(cleaned)
