import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class IncidentRemediationRequest(BaseModel):
    raw_error_log: str = Field(..., description="Raw server error log or Python traceback string")
    target_repo_path: Optional[str] = Field(None, description="Path to target repo sandbox (defaults to configured broken service)")
    max_repair_attempts: Optional[int] = Field(3, description="Maximum self-correction iteration attempts")


class IncidentRemediationResponse(BaseModel):
    incident_id: str
    status: str
    test_passed: bool
    attempt_count: int
    extracted_error_type: Optional[str] = None
    offending_file: Optional[str] = None
    pull_request_url: Optional[str] = None
    diagnosis_report: Optional[str] = None
    audit_history: List[str] = []
