from langgraph.graph import StateGraph, END
from src.graph.state import IncidentState
from src.agents.log_inspector import log_inspector_node
from src.agents.code_diagnostician import code_diagnostician_node
from src.agents.developer_coder import developer_coder_node
from src.agents.qa_tester import qa_tester_node
from src.agents.pr_generator import pr_generator_node
from src.config import settings


def should_continue(state: IncidentState) -> str:
    """
    Self-Correction Conditional Edge:
    - If tests pass -> proceed to PR generation.
    - If tests fail and attempts < max_attempts -> loop back to Developer Coder with test failures.
    - If tests fail and attempts >= max_attempts -> abort to END with FAILED_MAX_RETRIES.
    """
    if state.get("test_passed", False):
        return "generate_pr"
    
    attempts = state.get("attempt_count", 1)
    max_attempts = state.get("max_attempts", settings.MAX_REPAIR_ATTEMPTS)
    
    if attempts < max_attempts:
        return "developer_coder"  # Self-correction loop!
    else:
        return END  # Exceeded max attempts


def build_aegis_graph():
    """
    Constructs the 4-agent state machine workflow in LangGraph.
    """
    workflow = StateGraph(IncidentState)

    # Add Nodes
    workflow.add_node("log_inspector", log_inspector_node)
    workflow.add_node("code_diagnostician", code_diagnostician_node)
    workflow.add_node("developer_coder", developer_coder_node)
    workflow.add_node("qa_tester", qa_tester_node)
    workflow.add_node("generate_pr", pr_generator_node)

    # Set Entry Point
    workflow.set_entry_point("log_inspector")

    # Connect Edges
    workflow.add_edge("log_inspector", "code_diagnostician")
    workflow.add_edge("code_diagnostician", "developer_coder")
    workflow.add_edge("developer_coder", "qa_tester")

    # Conditional Branch from QA Tester
    workflow.add_conditional_edges(
        "qa_tester",
        should_continue,
        {
            "developer_coder": "developer_coder",
            "generate_pr": "generate_pr",
            END: END
        }
    )

    workflow.add_edge("generate_pr", END)

    return workflow.compile()
