import os
import re
from langchain_core.prompts import ChatPromptTemplate
from src.agents.log_inspector import get_llm
from src.agents.code_diagnostician import find_target_file
from src.graph.state import IncidentState


def developer_coder_node(state: IncidentState) -> dict:
    """
    Agent 3: Developer Coder
    Writes the patched code and saves it to disk. 
    If this is a retry attempt, it incorporates feedback from failed unit tests!
    """
    llm = get_llm()
    target_file = find_target_file(state["target_repo_path"], state["offending_file"] or "services/billing_service.py")
    
    current_code = ""
    if os.path.exists(target_file):
        with open(target_file, "r", encoding="utf-8") as f:
            current_code = f.read()

    # Read unit test file if available to ensure coder writes code matching test expectations
    test_file_path = os.path.join(state["target_repo_path"], "tests", "test_billing_service.py")
    test_suite_content = ""
    if os.path.exists(test_file_path):
        with open(test_file_path, "r", encoding="utf-8") as f:
            test_suite_content = f.read()

    attempt = state.get("attempt_count", 0) + 1
    feedback = state.get("test_output", "No previous test run.")

    prompt = ChatPromptTemplate.from_template(
        """You are the Developer Coder Agent in an autonomous self-healing multi-agent system.
Your task is to provide the COMPLETE, FULL replacement Python code for the file that fixes all bugs and makes all unit tests pass with 100% success.

Target File Path: {target_file}
Attempt: {attempt}
Diagnosis: {diagnosis}
Remediation Plan: {repair_plan}

Current File Content:
```python
{current_code}
```

Unit Tests in Repository (Your code MUST satisfy these tests):
```python
{test_suite_content}
```

Previous Test Run Output (If any failures, inspect carefully to fix):
```
{feedback}
```

CRITICAL INSTRUCTIONS:
1. Return the ENTIRE Python source code for the file, from imports down to the last line.
2. Ensure edge cases are handled:
   - Handle division by zero gracefully (return 0.0 if participants <= 0).
   - Safely handle promo_code when it is None, empty, or mixed case (e.g., None -> return subtotal).
   - Safely extract customer_id and items with default fallbacks (.get('customer_id', 'UNKNOWN'), .get('items', [])).
3. Do NOT omit any functions or docstrings.
4. Respond ONLY with the Python code wrapped in ```python ... ``` markdown blocks.
"""
    )
    chain = prompt | llm
    response = chain.invoke({
        "target_file": target_file,
        "attempt": attempt,
        "diagnosis": state.get("diagnosis_report", ""),
        "repair_plan": state.get("repair_plan", ""),
        "current_code": current_code,
        "test_suite_content": test_suite_content,
        "feedback": feedback
    })

    content = response.content
    if isinstance(content, list):
        content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    match = re.search(r"```(?:python)?\s*([\s\S]*?)\s*```", content)
    patched_code = match.group(1).strip() if match else content.strip()

    # Write patched code directly to the target file
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(patched_code)

    audit_msg = f"[Developer Coder] Generated and applied code patch (Attempt #{attempt}) to {os.path.basename(target_file)}"
    return {
        "patched_files": {target_file: patched_code},
        "attempt_count": attempt,
        "audit_history": state["audit_history"] + [audit_msg]
    }
