from app.agents.llm_client import call_gemini


def run_research_agent(topic: str) -> str:
    prompt = f"""Explain "{topic}" clearly and accurately, as if to someone with no background in the subject.

Rules:
- Use simple, everyday words. Avoid jargon; if a technical term is unavoidable, explain it in one short phrase right after using it.
- Stick to well-established facts. Do not guess or make up specifics (numbers, dates, names) you're not confident about.
- Structure: a 1-sentence plain definition, then 3-4 short paragraphs covering what it is, why it matters today, and anything important to know.
- Keep total length under 200 words.

Topic: {topic}"""

    return call_gemini(prompt)