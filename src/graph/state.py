from typing import TypedDict, List, Optional, Dict, Any


class IncidentState(TypedDict):
    """
    Global state machine schema shared across the 4 agents in LangGraph.
    """
    incident_id: str
    target_repo_path: str
    raw_error_log: str
    
    # Log Inspector output
    extracted_error_type: Optional[str]
    offending_file: Optional[str]
    stack_trace: Optional[str]
    
    # Code Diagnostician output
    diagnosis_report: Optional[str]
    repair_plan: Optional[str]
    
    # Developer Coder output
    patched_files: Optional[Dict[str, str]]  # filepath -> full patched content
    
    # QA Tester output & iteration loop
    test_passed: bool
    test_output: Optional[str]
    test_summary: Optional[str]
    attempt_count: int
    max_attempts: int
    
    # Completion & Pull Request
    pull_request_url: Optional[str]
    final_status: str  # "RESOLVED", "FAILED_MAX_RETRIES", "IN_PROGRESS"
    audit_history: List[str]
