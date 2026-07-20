from app.agents.llm_client import call_gemini


def run_summary_agent(research_text: str) -> str:
    prompt = f"""Summarize the following research into a concise summary (3-5 sentences), highlighting only the most important points.

Research:
{research_text}"""

    return call_gemini(prompt)