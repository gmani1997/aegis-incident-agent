# 🛡️ Aegis-Agent: Autonomous Enterprise Incident Response Multi-Agent System

An end-to-end autonomous incident response system built with **LangGraph**, **Google Gemini**, **FastAPI**, and **Pytest**.

Aegis ingests server error logs and stack traces, isolates root-cause bugs across target repositories, applies code refactoring, validates fixes via iterative unit test execution (`pytest`), and automatically generates Git commits and GitHub Pull Requests.

---

## 🏗️ Architecture

```
                       [Incoming Error Log / Webhook]
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │   1. Log Inspector     │
                        │  (Extracts Stack Trace)│
                        └────────────┬───────────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │ 2. Code Diagnostician  │
                        │ (Isolates Root Cause)  │
                        └────────────┬───────────┘
                                     │
                                     ▼
                   ┌───►┌────────────────────────┐
                   │    │   3. Developer Coder   │
                   │    │ (Writes Safe Patches)  │
                   │    └────────────┬───────────┘
[Self-Correction]  │                 │
[Loop on Failure]  │                 ▼
                   │    ┌────────────────────────┐
                   └────┤     4. QA Tester       │
                        │(Executes pytest Suite) │
                        └────────────┬───────────┘
                                     │ (100% Passed)
                                     ▼
                        ┌────────────────────────┐
                        │    5. PR Generator     │
                        │(Auto Git Commit & PR)  │
                        └────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Local Environment
```bash
# Clone and enter workspace
cd aegis-incident-agent

# Create venv and install dependencies
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Configure your API Key
cp .env.example .env
# Add GEMINI_API_KEY in .env

# Run local standalone remediation
python run_local.py

# Start FastAPI server
uvicorn src.main:app --reload --port 8000
```

### 2. Docker Deployment
```bash
docker compose up --build
```

---

## 📡 REST API Endpoints

* **`POST /api/v1/incidents/remediate`**: Ingest error log and trigger multi-agent remediation loop.
* **`GET /api/v1/incidents/{incident_id}`**: Check remediation status and detailed audit trace.
* **`GET /health`**: Health check and active LLM configuration.
* **`GET /docs`**: Interactive Swagger UI.

---

## 📁 Repository Structure
```
├── src/
│   ├── agents/
│   │   ├── log_inspector.py        # Agent 1: Traceback & offending file parser
│   │   ├── code_diagnostician.py   # Agent 2: Root-cause diagnosis & repair planner
│   │   ├── developer_coder.py      # Agent 3: Patch authoring with test feedback
│   │   ├── qa_tester.py            # Agent 4: Pytest execution & verification
│   │   └── pr_generator.py         # Agent 5: Git commit & GitHub PR automation
│   ├── graph/
│   │   ├── state.py                # TypedDict state machine schema
│   │   └── workflow.py             # LangGraph state machine & conditional edges
│   ├── tools/
│   │   └── runner.py               # Subprocess sandbox pytest test runner
│   ├── config.py                   # Pydantic Settings & environment variables
│   ├── schemas.py                  # FastAPI request/response models
│   └── main.py                     # FastAPI REST server
├── sandbox/
│   └── broken_service/             # Target repository with reproducible bugs & pytest
├── data/
│   └── sample_logs/                # Production server error logs & tracebacks
├── Dockerfile                      # Container definition
├── docker-compose.yml              # Multi-container orchestration
├── run_local.py                    # Local CLI pipeline runner
├── test_api.py                     # API client verification test
└── requirements.txt                # Python dependencies
```
