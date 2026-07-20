from typing import TypedDict
from langgraph.graph import StateGraph, END

from app.agents.research_agent import run_research_agent
from app.agents.summary_agent import run_summary_agent
from app.agents.email_agent import run_email_agent


class WorkflowState(TypedDict):
    original_request: str
    research_output: str
    summary_output: str
    email_output: str


def research_node(state: WorkflowState) -> WorkflowState:
    result = run_research_agent(state["original_request"])
    return {**state, "research_output": result}


def summary_node(state: WorkflowState) -> WorkflowState:
    result = run_summary_agent(state["research_output"])
    return {**state, "summary_output": result}


def email_node(state: WorkflowState) -> WorkflowState:
    result = run_email_agent(state["summary_output"], state["original_request"])
    return {**state, "email_output": result}


def build_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("research", research_node)
    graph.add_node("summary", summary_node)
    graph.add_node("email", email_node)

    graph.set_entry_point("research")
    graph.add_edge("research", "summary")
    graph.add_edge("summary", "email")
    graph.add_edge("email", END)

    return graph.compile()


workflow_graph = build_graph()