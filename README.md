# Pulse AI Interview Agent

An intelligent, conversational AI Interview Agent built for the **ABTalks Vibe Code Hackathon — Problem Statement 2 ("The Interview Agent")**.

---

## Objective

Pulse AI Interview Agent conducts realistic, multi-turn technical interviews tailored to a candidate's learning journey.

The application:

- Personalizes questions using official candidate profiles and learning progress from the supplied 31-day curriculum.
- Maintains multi-turn interview context and session state.
- Generates follow-up questions based on the candidate's previous answers.
- Targets at least **10 meaningful questions** across at least **6 unique curriculum days**.
- Prevents exact duplicate questions and protects completed sessions from continuing.
- Produces structured actionable feedback with:
  - `summary`
  - `strengths`
  - `gaps`
  - `next`

---

## Current Architecture

The repository contains a working end-to-end hackathon demo:

- **FastAPI backend** exposing `POST /api/interview` and `GET /api/candidates`.
- **LangGraph interview workflow** for stateful interview progression, curriculum coverage, follow-ups, duplicate-question protection, and completion.
- **PostgreSQL-backed session state**, with a local SQLite fallback for development/demo environments when PostgreSQL is unavailable.
- **Static frontend** using HTML, CSS, and JavaScript.
- Candidate selection and profile display.
- Interview chat interface.
- Interview progress tracking.
- Structured completion feedback.
- Interview restart flow.
- **Official ABTalks resources** under `docs/abtalks/` are treated as the source of truth.
- **Pytest test suite** covering API validation, candidate handling, workflow hardening, and database fallback behavior.
- Secrets are kept out of source control; `.env.example` documents configuration without containing real credentials.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI, Pydantic |
| AI Orchestration | LangGraph |
| LLM Integration | Configurable API-based LLM |
| Database & State | PostgreSQL, SQLAlchemy ORM, SQLite fallback for local demo |
| Testing | Pytest, FastAPI TestClient / HTTPX |
| Version Control | Git + GitHub |

---

## Repository Structure

```text
pulse-ai-interview-agent/
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── api.js
│   ├── styles.css
│   └── README.md
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── models/
│   │   ├── routes/
│   │   └── services/
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── docs/
│   └── abtalks/
│       ├── curriculum.json
│       ├── candidates.json
│       └── technical-spec.md
│
├── data/
│
├── PROMPTS.md
├── .env.example
├── .gitignore
└── README.md
```

---

## Official ABTalks Resources

The organizer-provided files under `docs/abtalks/` are the authoritative source for the project.

### `curriculum.json`

Contains the supplied 31-day learning curriculum used to ground interview questions.

### `candidates.json`

Contains the supplied candidate profiles and learning progress used for interview personalization.

### `technical-spec.md`

Contains the official technical and API requirements for the hackathon problem statement.

These organizer-provided files must not be replaced with invented data.

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip`
- Python virtual environment (`venv`)
- PostgreSQL for the primary session-state configuration
- A local `.env` file based on `.env.example`

---

## Backend Setup

From the repository root:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file using `.env.example` as the template.

Configure the required database and LLM settings.

Start the FastAPI backend:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The backend will be available at:

```text
http://localhost:8000
```

FastAPI Swagger documentation:

```text
http://localhost:8000/docs
```

Health endpoint:

```text
http://localhost:8000/health
```

---

## Frontend Setup

The current hackathon demo uses a static HTML/CSS/JavaScript frontend.

From the repository root:

```bash
python -m http.server 8080 --directory frontend
```

Open:

```text
http://localhost:8080/
```

If port `8080` is already in use, use another port:

```bash
python -m http.server 8081 --directory frontend
```

Then open:

```text
http://localhost:8081/
```

The frontend connects to the backend at:

```text
http://localhost:8000
```

by default.

---

## Running the Complete Demo

Run the backend in one terminal:

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Run the frontend in another terminal from the project root:

```bash
python -m http.server 8080 --directory frontend
```

Then open:

```text
http://localhost:8080/
```

---

## Interview Flow

The complete user flow is:

```text
Candidate Selection
        ↓
Candidate Profile
        ↓
Start Interview
        ↓
Interview Question
        ↓
Candidate Answer
        ↓
Contextual Follow-up
        ↓
Curriculum Progression
        ↓
10+ Questions / 6+ Curriculum Days
        ↓
Interview Completion
        ↓
Structured Feedback
        ↓
Start New Interview
```

The backend remains the source of truth for interview progression and session state.

---

## API

### `POST /api/interview`

The interview endpoint supports both initial interview creation and subsequent interview turns according to the official technical specification.

A completed interview response contains structured feedback:

```json
{
  "reply": "...",
  "done": true,
  "feedback": {
    "summary": "...",
    "strengths": [],
    "gaps": [],
    "next": []
  }
}
```

### `GET /api/candidates`

Returns the candidate catalog used by the frontend.

---

## Interview Requirements

The final implementation targets:

- At least **10 meaningful questions**.
- At least **6 unique curriculum days**.
- Questions grounded in the official curriculum.
- Candidate-specific interview personalization.
- Multi-turn conversation context.
- Follow-up questions based on previous candidate answers.
- Exact duplicate-question protection.
- Persistent session state.
- Completed-session protection.
- Structured final feedback.

---

## Testing

Run the backend tests from the `backend/` directory:

```bash
python -m pytest -q
```

Final local verification:

```text
10 passed, 3 warnings
```

The three warnings were framework/dependency deprecation warnings and did not cause test failures.

The test suite covers areas including:

- API validation.
- Candidate data handling.
- Interview workflow behavior.
- Session validation.
- Workflow hardening.
- Duplicate-question protection.
- Completed-session behavior.
- Database fallback behavior.

---

## Environment Variables

Use `.env.example` as the configuration template.

Keep real credentials in a local `.env` file only.

Typical configuration includes:

```env
DATABASE_URL=
GEMINI_API_KEY=
LLM_MODEL=
```

Do not commit real values.

### Security Requirements

Never commit:

- API keys.
- Database passwords.
- Authentication tokens.
- Private credentials.
- Other secrets.
- Generated local database files.

The frontend must never receive backend API keys or database credentials.

---

## Database & Session State

The application is designed around PostgreSQL for persistent interview session state.

Session information can include:

- Session ID.
- Candidate information.
- Conversation history.
- Questions asked.
- Curriculum days covered.
- Current interview state.
- Completion status.
- Final feedback.

For local development/demo environments, the project also contains a SQLite fallback so the application can be exercised when PostgreSQL is unavailable.

Generated local database files are ignored by Git.

---

## AI Usage Log

The project maintains an AI-development record in:

```text
PROMPTS.md
```

This file records the prompts used by the three team members during development, as required by the hackathon.

---

## Development Guidelines

When extending the project:

1. Preserve the official ABTalks resources.
2. Do not invent candidate or curriculum data.
3. Do not expose secrets.
4. Preserve the `/api/interview` contract unless the official technical specification requires a change.
5. Keep interview progression in the backend.
6. Keep frontend presentation separate from interview/business logic.
7. Add tests for important behavioral changes.
8. Do not commit generated database files or environment secrets.

---

## Project Status

The project is in its final hackathon-demo state.

Implemented capabilities include:

- End-to-end candidate-to-feedback interview flow.
- Candidate-specific interview personalization.
- Stateful LangGraph interview workflow.
- Curriculum-aware questioning.
- Contextual follow-up questions.
- Duplicate-question protection.
- Minimum question and curriculum coverage targets.
- Session persistence and local fallback.
- Completed-session protection.
- Responsive polished frontend.
- Backend API validation.
- Automated backend tests.
- Secure environment configuration.
- AI usage prompt logging.

---

## Local Demo

For the final local demo, run:

### Terminal 1 — Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Frontend

```bash
python -m http.server 8080 --directory frontend
```

Then open:

```text
http://localhost:8080/
```

The application is ready for the hackathon demonstration.