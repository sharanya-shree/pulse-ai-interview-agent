# Pulse AI Interview Agent — Backend Service

This is the Python FastAPI backend service for the **Pulse AI Interview Agent** (ABTalks Vibe Code Hackathon — Problem Statement 2).

## Architecture Overview

- **Framework**: FastAPI + Pydantic v2
- **Database**: PostgreSQL (SQLAlchemy ORM + session state models)
- **AI Orchestration**: LangGraph (Foundation integration ready for Person 2)
- **Testing**: Pytest + HTTPX / TestClient

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application instance & health route
│   ├── core/
│   │   ├── config.py        # Environment settings (Pydantic Settings)
│   │   └── database.py      # SQLAlchemy PostgreSQL engine & session setup
│   ├── models/
│   │   ├── interview.py     # Pydantic API schemas (InterviewRequest, InterviewResponse)
│   │   └── db.py            # SQLAlchemy session state database model
│   ├── routes/
│   │   └── interview.py     # POST /api/interview endpoint router
│   └── services/            # AI Agent services (to be built by Person 2)
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   └── test_interview.py    # Unit tests for API contract validation
├── requirements.txt
└── README.md
```

## Setup & Running Locally

### 1. Create and activate a Virtual Environment

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run FastAPI Application

```bash
uvicorn app.main:app --reload --port 8000
```

The server will start at `http://localhost:8000`.
- OpenAPI Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 4. Run Pytest Suite

```bash
pytest
```

## API Endpoint Specification

### `POST /api/interview`

#### Initial Request Payload:
```json
{
  "sessionId": "abc-123",
  "candidate": {
    "id": "cand-01",
    "name": "Jane Doe",
    "experienceLevel": "Intermediate",
    "completedDays": [1, 2, 3, 4]
  }
}
```

#### Subsequent Request Payload:
```json
{
  "sessionId": "abc-123",
  "message": "I choose asynchronous processing because it handles high IO concurrency."
}
```

#### Response Format (In Progress):
```json
{
  "reply": "Thank you. Let's move on to the next question...",
  "done": false
}
```

#### Response Format (Completed):
```json
{
  "reply": "Interview completed! Here is your feedback.",
  "done": true,
  "feedback": {
    "summary": "Solid technical performance with clear explanations.",
    "strengths": ["Clear system design reasoning", "Good knowledge of Day 3 topics"],
    "gaps": ["Concurrency edge cases"],
    "next": ["Review distributed lock patterns"]
  }
}
```
