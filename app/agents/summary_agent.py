from app.agents.llm_client import call_gemini


def run_summary_agent(research_text: str) -> str:
    prompt = f"""Summarize the following in plain, simple language that anyone can understand — no jargon, no filler sentences, no repeating the same point twice.

Give exactly 3-4 short sentences covering only the most important points. Do not add information that isn't in the text below.

Text to summarize:
{research_text}"""

    return call_gemini(prompt)