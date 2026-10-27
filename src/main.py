import os
import uuid
from typing import Dict
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from src.schemas import IncidentRemediationRequest, IncidentRemediationResponse
from src.graph.workflow import build_aegis_graph
from src.graph.state import IncidentState
from src.config import settings

app = FastAPI(
    title="Aegis-Agent Incident Response API",
    description="Autonomous Multi-Agent System for Incident Response, Automated Bug Diagnosis, and Self-Healing Code Remediation.",
    version="1.0.0"
)

# Enable CORS for dashboard/frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory incident store
incident_db: Dict[str, IncidentRemediationResponse] = {}

# Compile LangGraph Workflow
graph = build_aegis_graph()


@app.get("/")
def root():
    return {
        "service": "Aegis-Agent Multi-Agent Incident Response",
        "status": "operational",
        "docs_url": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy", "gemini_model": settings.GEMINI_MODEL}


@app.post("/api/v1/incidents/remediate", response_model=IncidentRemediationResponse)
def remediate_incident(payload: IncidentRemediationRequest):
    """
    Ingests server error logs, extracts tracebacks, triggers the 4 LangGraph agents,
    iteratively heals broken code via pytest loops, and outputs resolution status.
    """
    incident_id = str(uuid.uuid4())[:8]
    target_repo = payload.target_repo_path or os.path.abspath(settings.DEFAULT_TARGET_REPO_PATH)

    if not os.path.exists(target_repo):
        raise HTTPException(status_code=400, detail=f"Target repository path '{target_repo}' not found.")

    initial_state: IncidentState = {
        "incident_id": incident_id,
        "target_repo_path": target_repo,
        "raw_error_log": payload.raw_error_log,
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
        "max_attempts": payload.max_repair_attempts or settings.MAX_REPAIR_ATTEMPTS,
        "pull_request_url": None,
        "final_status": "IN_PROGRESS",
        "audit_history": [f"[System] API Incident #{incident_id} received. Running state machine..."]
    }

    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent workflow execution error: {str(e)}")

    response = IncidentRemediationResponse(
        incident_id=incident_id,
        status=final_state.get("final_status", "UNKNOWN"),
        test_passed=final_state.get("test_passed", False),
        attempt_count=final_state.get("attempt_count", 0),
        extracted_error_type=final_state.get("extracted_error_type"),
        offending_file=final_state.get("offending_file"),
        pull_request_url=final_state.get("pull_request_url"),
        diagnosis_report=final_state.get("diagnosis_report"),
        audit_history=final_state.get("audit_history", [])
    )

    incident_db[incident_id] = response
    return response


@app.get("/api/v1/incidents/{incident_id}", response_model=IncidentRemediationResponse)
def get_incident(incident_id: str):
    """
    Retrieves incident remediation details and audit history.
    """
    if incident_id not in incident_db:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return incident_db[incident_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
