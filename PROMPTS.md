# AI Usage Log

## Person 1

### Prompt 1 — Project Foundation

```text
We are building a hackathon project called "Pulse AI Interview Agent" for ABTalks Vibe Code Hackathon — Problem Statement 2: "The Interview Agent".

You are working inside the Git repository:
pulse-ai-interview-agent

IMPORTANT:
This is a team project with 3 people working sequentially on the SAME GitHub repository.
I am Person 1 / Team Lead.
Your current task is ONLY to establish the project foundation and backend foundation.
Do NOT implement the complete AI interviewer yet.
Do NOT implement the LangGraph interview workflow yet.
Do NOT build the complete frontend yet.
Do NOT invent requirements or API endpoints that are not specified.

==================================================
PROJECT REQUIREMENTS — SOURCE OF TRUTH
==================================================

Problem Statement 2 requires an AI Interview Agent that:

1. Conducts a realistic, conversational, multi-turn technical interview.
2. Personalizes the interview based on the candidate's learning journey.
3. Uses the supplied 31-day curriculum.
4. Uses the supplied candidate profiles.
5. Asks intelligent follow-up questions based on previous answers.
6. Maintains conversation context throughout the interview.
7. Asks at least 8 questions covering at least 4 different curriculum days.
8. Our internal target is HIGHER:
   - At least 10 meaningful questions
   - At least 6 unique curriculum days
9. Produces structured actionable feedback at the end.
10. Must expose the HTTP endpoint defined by the Technical Specification.

The supplied Technical Specification defines the required endpoint:

POST /api/interview

Initial request:
{
  "sessionId": "abc-123",
  "candidate": { ...candidate data... }
}

Subsequent request:
{
  "sessionId": "abc-123",
  "message": "candidate's latest answer"
}

The response must contain:
{
  "reply": "...",
  "done": false
}

When the interview is complete:
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

The exact Technical Specification supplied by the organizers is the authority for the API contract. Do not invent alternative required endpoints.

==================================================
LOCKED TECHNOLOGY STACK
==================================================

Use this stack and do not substitute technologies without asking me first:

Frontend:
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui

Backend:
- Python
- FastAPI
- Pydantic

AI orchestration:
- LangGraph

Application LLM:
- GPT-5.6 through an API integration
- Do NOT implement the LLM integration yet in this task.

Database/state:
- PostgreSQL

Data:
- Supplied curriculum JSON
- Supplied candidate profiles JSON

Testing:
- Pytest

Deployment later:
- Frontend: Vercel
- Backend: Render

Version control:
- Git + GitHub

Breeth is NOT a mandatory dependency. Do not add Breeth in this foundation task.

Do NOT add a vector database unless a later requirement clearly needs one.

==================================================
CURRENT TASK — PERSON 1, FOUNDATION ONLY
==================================================

Create a clean, maintainable monorepo foundation for the project.

Create a structure similar to:

pulse-ai-interview-agent/
│
├── frontend/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── models/
│   │   ├── services/
│   │   └── core/
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── data/
│   ├── curriculum.json
│   └── candidates.json
│
├── PROMPTS.md
├── README.md
├── .gitignore
└── other configuration files only where genuinely necessary

Do not fabricate curriculum or candidate data.

If the supplied JSON files are not currently available in the workspace, create the data directory and clearly document where they must be placed, but DO NOT invent fake curriculum/candidate content.

==================================================
BACKEND FOUNDATION
==================================================

Set up a minimal FastAPI application.

Create:

POST /api/interview

For this foundation stage, it only needs to establish the correct request/response models and a basic route structure.

Create Pydantic models for:

- initial interview request
- subsequent interview request
- interview response
- feedback response
- candidate data where appropriate

The endpoint may return a temporary foundation response for now, but it must have the correct architecture so Person 2 can implement the actual interview agent later.

Do NOT implement the final interview logic yet.

==================================================
SESSION STATE FOUNDATION
==================================================

Prepare the backend architecture for session-based interview state using PostgreSQL.

We will eventually need state including concepts such as:

- sessionId
- candidate information/reference
- conversation history
- questions asked
- curriculum days covered
- current topic
- interview status
- final feedback

For this task:

- Set up the database configuration structure.
- Create appropriate database/session models or schemas.
- Use environment variables for database configuration.
- Do NOT hard-code credentials.
- Create an .env.example file.
- Do NOT create or commit a real .env file.

Do not over-engineer the database.

==================================================
CONFIGURATION AND SECURITY
==================================================

Create an appropriate .gitignore covering at least:

- Python virtual environments
- __pycache__
- .pyc files
- Node modules
- Next.js build output
- environment files containing secrets
- IDE/editor temporary files

Create:

.env.example

with placeholders for future configuration such as:

DATABASE_URL=
OPENAI_API_KEY=

Do not put real API keys anywhere in the repository.

==================================================
TESTING FOUNDATION
==================================================

Set up Pytest for the backend.

Create a basic test verifying that:

- the FastAPI application starts
- POST /api/interview is reachable
- the request validation structure exists

Do not try to test the final AI behavior yet.

==================================================
PROMPTS.MD — VERY IMPORTANT
==================================================

The hackathon requires an AI-usage log.

Create:

PROMPTS.md

This file must become the permanent log of the AI prompts used during development.

For this first task, record this exact prompt as:

# AI Usage Log

## Person 1

### Prompt 1 — Project Foundation

Then include the full prompt that you are currently receiving.

From this point onward, whenever I give you a new development prompt, we will append that prompt to PROMPTS.md.

Do NOT delete previous prompt entries.
Do NOT replace the log.
The log must accumulate throughout the project.

==================================================
README
==================================================

Create a concise README.md explaining:

- Project name
- PS2 objective
- Current architecture
- Technology stack
- Repository structure
- How to set up the backend locally
- How to run the FastAPI application
- How to run backend tests
- Environment variables required
- Note that the AI interview logic will be implemented in a later stage

Do not claim features are implemented if they are not.

==================================================
IMPORTANT DEVELOPMENT RULES
==================================================

1. Inspect the current repository before making changes.
2. Do not overwrite or delete useful existing files.
3. Do not invent organizer requirements.
4. Do not implement Person 2's AI agent yet.
5. Do not implement the full frontend yet.
6. Do not add unnecessary dependencies.
7. Keep the code modular so another developer can continue from it.
8. Use clear names and comments only where useful.
9. Make the project runnable after this task.
10. Do not create fake API keys or secrets.
11. Do not fabricate curriculum/candidate data.
12. Do not make Git commits yourself. I will review the changes first and handle Git manually.
13. At the end, provide me with:
    - files created
    - files modified
    - dependencies added
    - commands needed to run the foundation
    - tests performed
    - any issues or assumptions

Before finishing, verify that the project structure is coherent and that the FastAPI foundation and tests work.

Again: THIS TASK IS ONLY THE FOUNDATION FOR PERSON 1.
Do not build the complete application in one shot.
```
### Prompt 2 — ABTalks Resource Analysis

The official ABTalks PS2 resources have now been added to the repository under docs/abtalks/.

Read and inspect all three files:
- docs/abtalks/curriculum.json
- docs/abtalks/candidates.json
- docs/abtalks/technical-spec.md

Treat these organizer-provided files as the authoritative source for the PS2 implementation.

For now, DO NOT modify any files, generate code, or implement features.

Only analyze the resources and report:
1. The structure and important fields of curriculum.json.
2. The structure and important fields of candidates.json.
3. Every important API contract and submission requirement in technical-spec.md.
4. Any requirements that our current foundation must account for.
5. Any inconsistencies or important details we should be aware of.

Do not fabricate, alter, or replace any data from these official resources.

After the analysis, stop and wait for further instructions.

### Prompt 3 — Foundation Verification

Now verify the current Person 1 foundation without adding new features.

Please:
1. Inspect the current repository structure and existing implementation.
2. Set up/use the backend Python environment as needed.
3. Install the dependencies from backend/requirements.txt if they are not already installed.
4. Run the existing pytest test suite.
5. Start the FastAPI application if needed and verify:
   - GET /health
   - POST /api/interview with a valid initial request
   - POST /api/interview with a valid subsequent request
   - invalid request validation
6. Check that the official files under docs/abtalks/ remain unchanged.
7. Check that no secrets or .env files are being tracked.
8. Do not implement LangGraph, LLM, adaptive interviewing, or feedback generation yet.
9. Do not make any Git commits or pushes.

If anything fails, diagnose and fix only issues necessary to make the current foundation work.

At the end, report:
- tests passed/failed
- endpoints verified
- files changed, if any
- any remaining issues

Then stop and wait for my instructions.