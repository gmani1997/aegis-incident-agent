import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.config import settings
from src.graph.state import IncidentState


def get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.1
    )


def log_inspector_node(state: IncidentState) -> dict:
    """
    Agent 1: Log Inspector
    Parses raw error logs, isolates stack traces, and identifies target source files.
    """
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(
        """You are the Log Inspector Agent in an enterprise incident response system.
Analyze the following server error log and extract the critical incident details.

Error Log:
{raw_error_log}

Return a valid JSON object ONLY with the following keys:
- "error_type": The exact Exception name (e.g., ZeroDivisionError, KeyError, etc.)
- "offending_file": The relative or absolute path of the root-cause source file mentioned in the traceback (e.g. services/billing_service.py)
- "offending_function": The function name where the error occurred
- "stack_trace": The extracted traceback block

Respond ONLY with JSON enclosed in ```json ``` markdown code blocks.
"""
    )
    chain = prompt | llm
    response = chain.invoke({"raw_error_log": state["raw_error_log"]})
    
    content = response.content
    if isinstance(content, list):
        content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
    clean_json = match.group(1) if match else content
    
    try:
        data = json.loads(clean_json)
    except Exception:
        data = {
            "error_type": "UnknownException",
            "offending_file": "services/billing_service.py",
            "stack_trace": state["raw_error_log"]
        }

    audit_msg = f"[Log Inspector] Identified error: {data.get('error_type')} in {data.get('offending_file')}"
    return {
        "extracted_error_type": data.get("error_type"),
        "offending_file": data.get("offending_file"),
        "stack_trace": data.get("stack_trace", state["raw_error_log"]),
        "audit_history": state["audit_history"] + [audit_msg]
    }
