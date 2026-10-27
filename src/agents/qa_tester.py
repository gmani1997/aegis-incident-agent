from src.tools.runner import run_pytest_in_sandbox
from src.graph.state import IncidentState


def qa_tester_node(state: IncidentState) -> dict:
    """
    Agent 4: QA Tester
    Runs the automated pytest test suite against the patched repository.
    Verifies if 100% of unit tests pass.
    """
    repo_path = state["target_repo_path"]
    test_result = run_pytest_in_sandbox(repo_path)
    
    passed = test_result["passed"]
    output = test_result["output"]
    attempt = state.get("attempt_count", 1)

    if passed:
        summary = f"PASSED: 100% unit tests validated successfully on attempt #{attempt}."
        audit_msg = f"[QA Tester] Verification SUCCESS: All tests passed on attempt #{attempt}!"
    else:
        summary = f"FAILED: Tests failed on attempt #{attempt}. Self-correction loop triggered."
        audit_msg = f"[QA Tester] Verification FAILED on attempt #{attempt}. Routing back to Developer Coder."

    return {
        "test_passed": passed,
        "test_output": output,
        "test_summary": summary,
        "audit_history": state["audit_history"] + [audit_msg]
    }
