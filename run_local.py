import os
import sys
import uuid

# Force UTF-8 stdout encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from src.graph.workflow import build_aegis_graph
from src.graph.state import IncidentState


def run_pipeline():
    print("=" * 70)
    print("[AEGIS-AGENT] Autonomous Incident Response Multi-Agent System")
    print("=" * 70)

    log_file_path = os.path.abspath("data/sample_logs/zero_division_trace.log")
    with open(log_file_path, "r", encoding="utf-8") as f:
        raw_log = f.read()

    initial_state: IncidentState = {
        "incident_id": str(uuid.uuid4())[:8],
        "target_repo_path": os.path.abspath("sandbox/broken_service"),
        "raw_error_log": raw_log,
        "extracted_error_type": None,
        "offending_file": None,
        "stack_trace": None,
        "diagnosis_report": None,
        "repair_plan": None,
        "patched_files": None,
        "test_passed": False,
        "test_output": None,
        "test_summary": None,
        "attempt_count": 0,
        "max_attempts": 3,
        "pull_request_url": None,
        "final_status": "IN_PROGRESS",
        "audit_history": ["[System] Incident ingested. Initiating multi-agent state machine..."]
    }

    graph = build_aegis_graph()
    
    print("\n[Executing State Machine Workflow with Gemini...]")
    final_output = graph.invoke(initial_state)

    print("\n" + "=" * 70)
    print("[EXECUTION RESULTS]")
    print("=" * 70)
    print(f"Incident ID     : {final_output['incident_id']}")
    print(f"Final Status    : {final_output['final_status']}")
    print(f"Attempts Taken  : {final_output['attempt_count']}")
    print(f"Tests Passed    : {final_output['test_passed']}")
    print(f"Pull Request URL: {final_output.get('pull_request_url')}")
    print("\n[Audit History]:")
    for entry in final_output["audit_history"]:
        print(f"  * {entry}")
    print("=" * 70)


if __name__ == "__main__":
    run_pipeline()
