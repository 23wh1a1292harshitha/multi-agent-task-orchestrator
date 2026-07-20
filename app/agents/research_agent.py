from app.agents.llm_client import call_gemini


def run_research_agent(topic: str) -> str:
    prompt = f"""You are a research assistant. Provide a factual, well-organized research briefing on the following topic. Include key concepts, current relevance, and important considerations. Keep it to around 200-300 words.

Topic: {topic}"""

    return call_gemini(prompt)