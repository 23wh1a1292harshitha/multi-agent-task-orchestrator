from groq import Groq

from app.config import settings

_client = Groq(api_key=settings.groq_api_key)


def call_gemini(prompt: str) -> str:
    response = _client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()