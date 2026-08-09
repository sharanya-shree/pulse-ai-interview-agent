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

## Person 2

### Prompt 2 — ABTalks Resource Analysis

```text
We are now implementing the Person 2 backend AI interview workflow.

Before making changes, inspect the existing backend implementation and preserve the existing POST /api/interview API contract and Pydantic schemas.

Implement ONLY the interview state/workflow service layer for now.

Requirements:

1. Create the interview agent workflow inside:
   backend/app/services/

2. Use LangGraph for the interview state workflow.

3. The workflow must maintain these state concepts:
   - session_id
   - candidate information
   - conversation history
   - completed curriculum days
   - curriculum topics/questions already covered
   - number of meaningful questions asked
   - current question
   - interview completion status
   - collected information needed for final feedback

4. The interview should:
   - personalize questions using the candidate profile and completedDays
   - target at least 10 meaningful questions
   - cover at least 6 unique curriculum days
   - maintain multi-turn conversation context
   - generate follow-up questions based on the candidate's previous answer
   - avoid repeatedly asking the same question/topic
   - eventually produce structured feedback with:
     summary
     strengths
     gaps
     next

5. Use the existing docs/abtalks/curriculum.json and candidate schema as the source of curriculum/candidate data. Do not invent a different candidate schema.

6. Do NOT implement the frontend.

7. Do NOT change PROMPTS.md.

8. Do NOT change the public API request/response schema unless absolutely required by the existing technical specification.

9. Do not commit anything.

10. Before writing code, inspect:
    - backend/app/models/interview.py
    - backend/app/routes/interview.py
    - backend/app/models/db.py
    - backend/app/core/database.py
    - backend/app/core/config.py
    - backend/app/main.py
    - backend/requirements.txt

11. If dependencies such as LangGraph or the required LLM SDK are missing, identify them and add only the necessary dependency entries to backend/requirements.txt.

12. Keep the implementation modular so the existing route can call the service cleanly.

After implementation:
- show me every file you changed
- explain the workflow/state design
- show the important code changes
- do NOT commit
- do NOT modify unrelated files
```

### Prompt 2 — Workflow Verification and Hardening

```text
We have reviewed the Person 2 implementation. Do NOT commit anything.

Before making changes, verify the implementation against the actual PS2 requirements and existing API contract.

Focus specifically on these issues:

1. LLM model configuration:
   - Do not hardcode a model that conflicts with the project's agreed LLM integration.
   - Use the existing application configuration/environment approach.
   - Do not add or expose any API key.
   - The workflow must continue to work without OPENAI_API_KEY using the existing mock/fallback behavior.

2. Interview progression:
   - Verify that a complete interview actually reaches BOTH:
       a) at least 10 meaningful questions
       b) at least 6 unique curriculum days
   - Do not merely rely on the termination condition; verify the generated sequence.
   - Ensure follow-up questions are genuinely based on the candidate's previous answer/context.
   - Ensure the same question is not repeatedly generated.

3. Curriculum:
   - Verify that questions use the official docs/abtalks/curriculum.json data.
   - Do not invent or replace the supplied curriculum schema.

4. Session state:
   - Verify that an initial POST with sessionId + candidate creates the session.
   - Verify subsequent POST requests using only sessionId + message continue the same conversation.
   - Verify conversation history, questions asked, covered curriculum days and feedback are persisted.

5. Feedback:
   - Verify completion produces exactly the required structured fields:
       summary
       strengths
       gaps
       next

6. Tests:
   Add focused tests for the above behavior, especially:
   - initial interview turn
   - subsequent turn with the same sessionId
   - 10-question / 6-unique-day completion
   - structured feedback
   - behavior without OPENAI_API_KEY

7. Keep the existing POST /api/interview request and response contract unchanged unless the technical specification absolutely requires otherwise.

After making changes:
- show every changed file
- explain what was fixed
- run the complete pytest suite
- show the complete pytest result
- DO NOT commit
```

### Prompt 3 — ABTalks Resource Analysis

```text
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
```

### Prompt 4 — Foundation Verification

```text
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
```

## Person 3

### Prompt 1 — First, Make Copilot Understand the Existing Project

```text
You are helping me complete the final implementation of the Vicodathon hackathon project.

I am Person 3, the final developer. Person 1 and Person 2 have already implemented the backend, LangGraph interview workflow, PostgreSQL session state, official curriculum/candidate data, and initial project configuration.

I need you to work ONLY on top of the existing codebase.

First, inspect the entire repository before changing anything, especially:

- backend/
- frontend/
- docs/abtalks/curriculum.json
- docs/abtalks/candidates.json
- docs/abtalks/technical-spec.md
- backend/app/
- backend/tests/
- .env.example
- README files
- package/dependency files

Do NOT rewrite working code just for style.
Do NOT replace the official curriculum, candidates, or technical specification.
Do NOT hardcode API keys or secrets.
Do NOT commit or create a real .env file.
Do NOT remove existing functionality.

Give me a concise report containing:

1. What is already implemented.
2. What is incomplete.
3. What is broken or risky.
4. What Person 3 should implement.
5. Which files you recommend changing.
6. Which files should NOT be changed.

Do not modify files yet. Only inspect and report.
```

### Prompt 2 — Complete the Frontend

```text
Now implement the missing frontend functionality for the Vicodathon project.

Goal: create a complete, polished interview experience using the existing backend API.

Before coding, inspect the existing backend API models/routes so the frontend matches the actual API contract.

The frontend should support this complete flow:

1. Landing page
2. Candidate selection using the official candidates from docs/abtalks/candidates.json
3. Candidate profile/summary
4. Start interview
5. Interview chat interface
6. Display current question number and progress
7. Candidate submits an answer
8. Show interviewer response/follow-up
9. Continue until the backend marks the interview complete
10. Show completion screen
11. Show structured interview feedback if available
12. Allow starting a new interview

Requirements:

- Use the existing backend instead of duplicating interview logic in the frontend.
- Use the existing /api/interview API contract.
- Keep the UI responsive.
- Make loading states clear.
- Add error states for backend failures.
- Prevent accidental duplicate submissions while a request is pending.
- Preserve the interview session_id on the client.
- Clearly show interview progress.
- Make the interface suitable for a hackathon demo.
- Do not hardcode candidate data if it can be loaded from the official candidate JSON.
- Do not expose OPENAI_API_KEY or any secret in frontend code.
- Do not modify the official organizer files.
- Do not rewrite the backend unless an actual API mismatch prevents the frontend from working.

After implementation, inspect all changed files and summarize exactly what you changed.
```

### Prompt 3 — Make the Interview Workflow Robust

```text
Now audit and harden the existing interview workflow without replacing its architecture.

The project requirements are:

- The interview should contain at least 10 questions.
- Questions should cover at least 6 unique curriculum days.
- Questions must be grounded in the official curriculum.
- Follow-up questions should meaningfully depend on the candidate's previous answer.
- Questions should not be exact duplicates.
- The interview should maintain state across messages.
- The session should be resumable using its session_id.
- Once the interview is complete, it must not continue asking questions.
- Completion should produce structured feedback when the backend design supports it.

Inspect the existing LangGraph workflow and state model.

Fix only genuine issues you find.

Pay special attention to:

- question counting
- curriculum-day tracking
- duplicate questions
- follow-up generation
- session state persistence
- completed-session handling
- malformed candidate data
- missing fields
- LLM failures
- empty candidate answers
- invalid session IDs

Do not change the official curriculum or candidate data.

Do not hardcode secrets.

Do not remove PostgreSQL/session functionality.

After changes, explain:

- what was wrong
- what you fixed
- which files changed
- how the fixes satisfy the requirements
```

### Prompt 4 — Final Implementation Pass

```text
We are now in the FINAL IMPLEMENTATION PASS for the Vicodathon hackathon.

Do NOT spend time doing another broad audit or explaining what you could do. Make the remaining major changes directly and efficiently.

The backend workflow hardening is already complete and verified:

- pytest: 9 passed, 3 warnings, 0 failures
- session validation is implemented
- duplicate-question protection is implemented
- follow-up handling is implemented
- malformed-state handling is implemented
- completed-session protection is implemented

DO NOT rewrite that backend architecture unless you encounter an actual blocker.

Your job now is to finish the project end-to-end for a hackathon demo.

==================================================

1. COMPLETE THE FRONTEND
==================================================

Inspect the existing frontend and implement/fix the complete user journey:

Landing page
→ Candidate selection
→ Candidate details
→ Start interview
→ Interview chat
→ Submit answer
→ Follow-up question
→ Progress indicator
→ Continue until completion
→ Feedback/results
→ Start new interview

The UI must actually communicate with the existing FastAPI backend.

Use the REAL existing API contract. Inspect backend/app/routes/interview.py and related schemas/services before writing frontend API calls.

Do not invent endpoints.

The frontend must:

- load the official candidate catalog
- display candidate name, role, experience/education when available
- allow selecting a candidate
- create/start an interview session
- store the returned session_id
- send subsequent answers using that session_id
- display interviewer questions and candidate answers as a chat
- show question progress
- disable the submit button while waiting for the backend
- prevent accidental double submissions
- show useful errors if the backend is unavailable
- handle an already-completed session
- display final structured feedback when returned by the backend
- provide a "Start New Interview" action

==================================================
2. MAKE THE UI HACKATHON-READY
==================================================

Do not over-engineer the design.

Create a clean professional AI interview interface.

Use:

- clear visual hierarchy
- responsive layout
- polished cards
- clear primary CTA
- interview progress indicator
- chat bubbles
- loading state
- error state
- completion state
- candidate information panel
- accessible buttons and form controls

The application should look like a real interview product rather than a raw developer demo.

Do not add unnecessary animation libraries or dependencies.

Prefer the existing frontend stack and components.

==================================================
3. CONNECT FRONTEND AND BACKEND
==================================================

Verify the exact backend request/response schemas.

Do not assume field names.

If the backend returns fields such as:

- session_id
- question
- done
- feedback
- candidate

or equivalent existing names, use the actual names from the backend.

Create a small frontend API utility if appropriate so API communication is not duplicated across components.

Use an environment variable such as:

NEXT_PUBLIC_API_URL

with a sensible local default such as:

http://localhost:8000

Do NOT expose OPENAI_API_KEY or database credentials to the frontend.

==================================================
4. VERIFY THE INTERVIEW REQUIREMENTS
==================================================

The final application must preserve these requirements:

- minimum 10 questions
- minimum 6 unique curriculum days
- questions grounded in official curriculum
- follow-ups based on candidate answers
- avoid exact duplicate questions
- persistent session state
- completed sessions cannot continue
- structured feedback at completion

Do not implement interview logic independently in React/Next.js.

The backend remains the source of truth for interview progression.

==================================================
5. OFFICIAL DATA MUST REMAIN UNCHANGED
==================================================

DO NOT MODIFY:

docs/abtalks/curriculum.json
docs/abtalks/candidates.json
docs/abtalks/technical-spec.md

Use these as the source of truth.

If candidate data has nested fields such as member/missions, correctly adapt to that schema.

Do not create a fake candidate dataset.

==================================================
6. ENVIRONMENT / CONFIGURATION
==================================================

Verify:

- .env is gitignored
- .env.example contains placeholders only
- OPENAI_API_KEY is backend-only
- database credentials are backend-only
- frontend uses NEXT_PUBLIC_API_URL only
- no secrets appear in source code
- no real credentials are added

Do not create a real .env file.

==================================================
7. TESTS
==================================================

Do not spend excessive time writing dozens of tests.

Add only the highest-value missing tests.

Backend:

- existing 9 tests must continue passing
- add tests only if needed for a genuinely uncovered critical behavior

Frontend:

- ensure TypeScript/build/lint checks pass if configured

Run the available checks.

At minimum run:

cd backend
python -m pytest -q

Then from frontend run the appropriate existing commands, such as:

npm install
npm run build

or the project's existing test/lint commands if configured.

Do not invent commands that the project does not support.

==================================================
8. README
==================================================

Update the README only where necessary so a hackathon judge can run the project.

Include:

- project purpose
- architecture overview
- backend setup
- frontend setup
- environment variables
- PostgreSQL requirement if required
- how to run backend
- how to run frontend
- how to run tests
- basic interview flow

Do not claim functionality that doesn't actually exist.

==================================================
9. FINAL CLEANUP
==================================================

Before finishing:

- fix TypeScript errors
- fix Python syntax/import errors
- fix broken frontend API calls
- remove unused imports caused by your changes
- remove obvious dead code from your changes
- ensure loading/error states work
- ensure mobile layout is usable
- ensure no secret is exposed
- ensure official organizer files are untouched

Do NOT perform large stylistic refactors.

Do NOT replace working LangGraph/PostgreSQL architecture.

Do NOT introduce unnecessary dependencies.

==================================================
10. IMPORTANT: WORK EFFICIENTLY
==================================================

This is the final implementation pass.

Do not stop after giving me recommendations.

Actually edit the files and implement the required functionality.

Do not repeatedly ask me for confirmation.

Do not perform another lengthy audit before coding.

Make the major necessary changes now.

When finished, run the relevant verification commands.

Your final response must be concise and contain ONLY:

1. Major files changed
2. What was implemented
3. Test/build results
4. Any remaining blocker

Do not give me a long tutorial.
```

### Prompt 5 — Frontend Visual Polish

```text
Fix ONLY the frontend visual layout/alignment of the Pulse AI Interview Agent.

The application is working correctly now. DO NOT change:
- backend code
- API calls
- interview logic
- candidate data
- session handling
- functionality
- official organizer files

Current problem:
The page content is concentrated on the left side and there is a very large empty area on the right. The candidate cards are too narrow and the overall page does not use the available browser width.

Use the current screenshot as the visual reference.

Make the frontend look like a polished professional hackathon demo.

Requirements:

1. PAGE CONTAINER

- Use a responsive centered container.
- On desktop, use approximately 1100px–1250px max-width.
- Give the main content enough width to use the screen effectively.
- Keep reasonable left/right padding.
- Do not make the content stretch edge-to-edge.

2. HERO

- Make the "Pulse AI Interview Agent" hero span the main content width.
- Keep the title and subtitle aligned consistently.
- Keep the "Backend ready" status badge aligned to the right on desktop.
- On mobile, stack the badge below the title.

3. CANDIDATE SECTION

- Make the candidate selection section use the full available content width.
- Candidate cards should form a responsive grid rather than being confined to a narrow left column.
- Desktop: 3 candidate cards per row.
- Tablet: 2 cards per row.
- Mobile: 1 card per row.
- Cards should have equal width and equal height within each row.
- Use CSS grid rather than manually positioning cards.

4. CANDIDATE CARDS

- Make the cards visually balanced.
- Center candidate name, role, experience, and completed-days information.
- Give cards consistent padding.
- Add a subtle hover effect.
- Make the entire card clickable.
- Keep text readable and prevent awkward wrapping.
- Do not make cards excessively tall.

5. OVERALL SPACING

- Add consistent vertical spacing between:
  hero
  candidate section
  candidate grid
- Avoid huge unused whitespace.
- Keep the page visually balanced.

6. RESPONSIVENESS

Use CSS media queries so the layout works at:
- desktop
- laptop
- tablet
- mobile

7. IMPORTANT

Inspect the existing index.html, app.js, and styles.css before editing.

Prefer modifying styles.css and only make minimal HTML changes if necessary.

Do NOT introduce a CSS framework or new dependency.
Do NOT rewrite working JavaScript.
Do NOT change API behavior.

After making the changes:

- run the frontend/static server if necessary
- verify the page visually
- make sure all candidate cards appear in a proper responsive grid
- make sure there is no horizontal overflow
- make sure the existing candidate selection functionality still works

Do the implementation directly. Do not just tell me what CSS I should write.
```
## Person 3
## Gemini LLM Integration

### Prompt
Integrate a real LLM into the Pulse AI Interview Agent using Google Gemini through LangChain. Use the API key from environment variables and make the LLM generate contextual technical interview questions and follow-up questions based on the candidate's previous answer.

### Changes
- Added Gemini API configuration.
- Added `GOOGLE_API_KEY` environment variable.
- Added configurable `LLM_MODEL`.
- Integrated `ChatGoogleGenerativeAI`.
- Replaced rule-based/fallback interview generation with Gemini LLM generation.
- Updated the model from `gemini-2.5-flash-lite` to `gemini-2.5-flash` because the former was unavailable for new users.

## Frontend Cleanup

### Prompt
Remove the development/demo branding from the interview interface and present the application as the actual Pulse AI Interview Agent.

### Changes
- Removed "VICODATHON DEMO".
- Removed "Backend ready" status.
- Kept the main Pulse AI Interview Agent branding.