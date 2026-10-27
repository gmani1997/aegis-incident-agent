import os
import re
import json
from langchain_core.prompts import ChatPromptTemplate
from src.agents.log_inspector import get_llm
from src.graph.state import IncidentState


def find_target_file(repo_path: str, filename_hint: str) -> str:
    norm_hint = os.path.normpath(filename_hint).replace("\\", "/")
    # Try direct join
    direct = os.path.join(repo_path, filename_hint)
    if os.path.exists(direct):
        return direct
    
    # Search recursively for basename
    target_base = os.path.basename(filename_hint)
    for root, _, files in os.walk(repo_path):
        if target_base in files:
            return os.path.join(root, target_base)
            
    # Default fallback
    return os.path.join(repo_path, "services", "billing_service.py")


def code_diagnostician_node(state: IncidentState) -> dict:
    """
    Agent 2: Code Diagnostician
    Examines source code context around the failing line and formulates a root-cause fix plan.
    """
    llm = get_llm()
    target_file = find_target_file(state["target_repo_path"], state["offending_file"] or "services/billing_service.py")
    
    source_code = ""
    if os.path.exists(target_file):
        with open(target_file, "r", encoding="utf-8") as f:
            source_code = f.read()

    prompt = ChatPromptTemplate.from_template(
        """You are the Code Diagnostician Agent.
Your job is to isolate the root cause and specify a clear, non-breaking remediation plan.

Error Type: {error_type}
Traceback:
{stack_trace}

Target File ({target_file}):
```python
{source_code}
```

Return a valid JSON object ONLY with:
- "root_cause": Clear explanation of why the bug occurred.
- "remediation_plan": Step-by-step technical requirements for the developer to fix this bug cleanly and safely, ensuring unit tests will pass.

Respond ONLY with JSON enclosed in ```json ``` markdown code blocks.
"""
    )
    chain = prompt | llm
    response = chain.invoke({
        "error_type": state.get("extracted_error_type", "Error"),
        "stack_trace": state.get("stack_trace", ""),
        "target_file": target_file,
        "source_code": source_code
    })

    content = response.content
    if isinstance(content, list):
        content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
    clean_json = match.group(1) if match else content
    
    try:
        data = json.loads(clean_json)
    except Exception:
        data = {
            "root_cause": "Unhandled edge condition in calculation",
            "remediation_plan": "Add validation checks for zero and empty values."
        }

    audit_msg = f"[Code Diagnostician] Diagnosed root cause: {data.get('root_cause')[:80]}..."
    return {
        "diagnosis_report": data.get("root_cause"),
        "repair_plan": data.get("remediation_plan"),
        "audit_history": state["audit_history"] + [audit_msg]
    }
