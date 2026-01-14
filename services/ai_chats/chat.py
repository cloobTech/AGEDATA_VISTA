from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from schemas.chat import Message
from typing import Dict, List
from settings.pydantic_config import settings

# Groq via OpenAI-compatible API
client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

SYSTEM_PROMPT = "You are a helpful AI agent."

# DEV ONLY (memory resets on restart)
sessions: Dict[str, List[Message]] = {}


def build_messages(history: List[Message]) -> List[ChatCompletionMessageParam]:
    messages: List[ChatCompletionMessageParam] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    for m in history:
        messages.append(
            {
                "role": m.role,  # pyright: ignore
                "content": m.content,
            }
        )

    return messages


def chat(session_id: str, user_message: str) -> str:
    history = sessions.get(session_id, [])

    history.append(
        Message(role="user", content=user_message)
    )

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=build_messages(history),
    )

    reply = response.choices[0].message.content or "No reply"

    history.append(
        Message(role="assistant", content=reply)
    )

    sessions[session_id] = history

    return reply
