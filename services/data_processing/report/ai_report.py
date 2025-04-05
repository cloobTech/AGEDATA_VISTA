from openai import OpenAI
from settings.pydantic_config import settings


def interpret_result_with_ai(summary_text: str):

    client = OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"

    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for business teams. Generate simple, easy-to-understand summaries of data insights, suitable for presentations or dashboards. Avoid jargon."},
            {"role": "user", "content": f"Here are the results:\n{summary_text}"}
        ],
        stream=False,
    )

    ai_report = response.choices[0].message.content
    return ai_report
