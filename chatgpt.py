import json
import asyncio
import openai
import configparser

from os.path import exists
from typing import List


def load_history(history_path: str = "./history.json") -> List[dict]:
    history = []

    if exists(history_path):
        with open(history_path, "r") as h:
            history = json.load(h)

    return history


def save_history(history: List[dict] = [],
                 history_path: str = "./history.json") -> None:
    with open(history_path, "w+") as h:
        json.dump(history, h)


def ask_gpt(query: str) -> str:
    if len(query) == 0:
        return ""

    config = configparser.ConfigParser()
    config.read("./config.ini")

    open_ai_api_key = config['OPENAI']["API_KEY"]
    client = openai.OpenAI(api_key=open_ai_api_key)

    open_ai_model = config['OPENAI']["MODEL"]

    messages = load_history()

    if len(messages) == 0:
        messages = [
                {
                    "role": "system",
                    "content": "You are an intelligent assistant.",
                },
            ]

    messages.append(
        {"role": "user", "content": query}
    )

    chat = client.chat.completions.create(
        model=open_ai_model,
        messages=messages,
    )

    answer = chat.choices[0].message.content

    messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    save_history(messages)

    return answer


async def generate_response(query: str) -> str:
    get_answer = asyncio.to_thread(ask_gpt, query)
    answer = await get_answer
    return answer
