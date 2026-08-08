# Pulse AI Interview Agent

[![Problem Statement](https://img.shields.io/badge/ABTalks%20Hackathon-PS2%3A%20Interview%20Agent-blue)](https://github.com/)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Pydantic%20%7C%20SQLAlchemy-green)](https://fastapi.tiangolo.com/)
[![Orchestration](https://img.shields.io/badge/Orchestration-LangGraph-orange)](https://www.langchain.com/langgraph)

An intelligent, conversational AI Interview Agent built for the **ABTalks Vibe Code Hackathon — Problem Statement 2 ("The Interview Agent")**.

---

## Objective

The objective of **Pulse AI Interview Agent** is to conduct realistic, multi-turn technical interviews tailored to a candidate's learning journey:
- Personalizes questions based on candidate profiles and completed learning modules from a 31-day curriculum.
- Dynamically generates follow-up questions and maintains multi-turn conversation context.
- Targets at least 10 meaningful questions covering at least 6 unique curriculum days.
- Produces structured actionable feedback (`summary`, `strengths`, `gaps`, `next`) upon interview completion.

---

## Current Architecture & Scope

This repository now includes a working hackathon demo experience:
- A FastAPI backend with the validated `POST /api/interview` and `GET /api/candidates` endpoints.
- A polished static frontend that loads official candidates, starts interviews, submits answers, and displays structured feedback.
- LangGraph-backed interview workflow with duplicate-question protection, follow-up handling, and session persistence.
- Environment configuration via `.env.example` with no secrets committed.
- Pytest validation for the backend workflow.

---

## Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | Next.js, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend** | Python, FastAPI, Pydantic v2 |
| **AI Orchestration** | LangGraph |
| **LLM Integration** | GPT-5.6 API integration (to be added) |
| **Database & State** | PostgreSQL (SQLAlchemy ORM + session state) |
| **Testing** | Pytest + TestClient / HTTPX |
| **Version Control** | Git + GitHub |

---

## Repository Structure

```
pulse-ai-interview-agent/
│
├── frontend/             # Next.js frontend application space
│   └── README.md
│
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── main.py       # FastAPI app initialization & health endpoint
│   │   ├── core/         # Settings & database engine connection
│   │   ├── models/       # Pydantic schemas & SQLAlchemy ORM session state
│   │   ├── routes/       # POST /api/interview endpoint router
│   │   └── services/     # LangGraph agent workflow services
│   ├── tests/            # Pytest test suite
│   ├── requirements.txt  # Backend Python dependencies
│   └── README.md
│
├── data/                 # Dataset folder for curriculum.json & candidates.json
│   └── README.md
│
├── PROMPTS.md            # AI usage prompt log (permanent development record)
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore configuration
└── README.md             # Project documentation
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` / `venv`
- PostgreSQL database (required for the backend session layer; configure `DATABASE_URL` in `.env`)

### Backend Setup

1. Navigate to the backend directory.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and adjust values as needed.
5. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

The backend API will be available at:
- http://localhost:8000
- http://localhost:8000/docs
- http://localhost:8000/health

### Frontend Setup

1. Serve the static frontend from the `frontend/` directory:
   ```bash
   cd frontend
   python -m http.server 8080
   ```
2. Open http://localhost:8080 in a browser.

### Running Tests

Run the backend test suite from the `backend/` directory:

```bash
python -m pytest -q
```

### Environment Variables

Use the values from `.env.example` and keep secrets in local `.env` only. The frontend uses `NEXT_PUBLIC_API_URL` and should not receive any API keys or database credentials.
