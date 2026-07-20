from app.agents.llm_client import call_gemini


def run_email_agent(summary: str, original_request: str) -> str:
    prompt = f"""Write a professional, well-formatted email based on the following summary. The email should be ready to send as-is, with an appropriate subject line, greeting, body, and sign-off (use a generic placeholder like "[Your Name]" for the sender).

Original request context: {original_request}

Summary to base the email on:
{summary}"""

    return call_gemini(prompt)