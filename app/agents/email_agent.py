from app.agents.llm_client import call_gemini


def run_email_agent(summary: str, original_request: str) -> str:
    prompt = f"""Write a short, clear, professional email based on the summary below. It should be easy to read quickly — simple sentences, no jargon, no filler phrases like "I hope this finds you well."

Format exactly like this:
Subject: [clear, specific subject line]

[Greeting]

[2-3 short paragraphs covering the key points from the summary]

[Sign-off]
[Your Name]

Context for the email: {original_request}

Summary to base it on:
{summary}"""

    return call_gemini(prompt)