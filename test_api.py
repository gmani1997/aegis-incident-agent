import json
import urllib.request

payload = {
    "raw_error_log": """2026-10-27 08:35:12.419 ERROR [uvicorn.error] Exception in ASGI application
Traceback (most recent call last):
  File "services/billing_service.py", line 20, in calculate_itemized_split
    per_person = total_amount / participants
ZeroDivisionError: float division by zero
INFO: 127.0.0.1:51234 - "POST /api/v1/billing/split HTTP/1.1" 500 Internal Server Error""",
    "max_repair_attempts": 3
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/incidents/remediate",
    data=data,
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as resp:
        print("Status Code:", resp.getcode())
        result = json.loads(resp.read().decode("utf-8"))
        print("\n--- REMEDIATION API RESPONSE ---")
        print(f"Incident ID   : {result['incident_id']}")
        print(f"Status        : {result['status']}")
        print(f"Tests Passed  : {result['test_passed']}")
        print(f"Offending File: {result['offending_file']}")
        print(f"PR URL        : {result['pull_request_url']}")
        print("\nAudit Logs:")
        for log in result['audit_history']:
            print(f"  * {log}")
except Exception as e:
    print("API Error:", e)
