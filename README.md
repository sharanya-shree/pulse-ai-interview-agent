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

## Current Architecture & Scope (Person 1 / Foundation Phase)

This repository currently establishes the **Monorepo Foundation & Backend API Specification**:
- Modular project structure for `frontend`, `backend`, `data`, and configuration files.
- FastAPI backend application with exact `POST /api/interview` schema validation per Technical Specification.
- Pydantic v2 request/response models (`InterviewRequest`, `InterviewResponse`, `InterviewFeedback`, `CandidateData`).
- PostgreSQL state persistence models (`InterviewSessionModel`) for tracking session history, topics covered, questions asked, and feedback.
- Environment configuration via `.env.example` (no secrets committed).
- Pytest testing harness.

> **Note**: The complete AI agent orchestration (LangGraph workflow) and frontend UI components will be implemented in subsequent development phases by Person 2 and Person 3.

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
- PostgreSQL database (optional for foundation stage; default SQLite/Postgres URL configurable via `.env`)

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv

   # On Windows (PowerShell)
   .venv\Scripts\Activate.ps1

   # On Linux/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Copy `.env.example` to `.env` in the root or backend directory:
   ```bash
   cp ../.env.example .env
   ```

5. **Run the FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The backend API will be available at:
   - Server: `http://localhost:8000`
   - Interactive Swagger Docs: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

---

## Running Backend Tests

Run the Pytest suite from the `backend/` directory:

```bash
pytest
```

---

## Environment Variables Required

Place these in your local `.env` file (refer to `.env.example`):

```env
DATABASE_URL=postgresql://user:password@localhost:5432/pulse_ai_db
OPENAI_API_KEY=your_openai_api_key_here
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0
```

---

## Data Placement Note

Please place the event organizer dataset files inside the `data/` directory:
- `data/curriculum.json`
- `data/candidates.json`

*(Do not commit secret credentials or fake dataset files).*
