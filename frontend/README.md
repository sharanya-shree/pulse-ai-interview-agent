# Pulse AI Interview Agent — Frontend

This directory contains the static demo frontend for the hackathon interview experience.

## What it does

- Loads the official candidate catalog from the backend.
- Lets a user pick a candidate and start a live interview.
- Sends each answer back to the existing FastAPI interview endpoint.
- Shows progress, chat messages, and final structured feedback.

## Run locally

1. Start the backend:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. Serve the frontend from this directory:
   ```bash
   cd frontend
   python -m http.server 8080
   ```

3. Open http://localhost:8080 in a browser.

## Configuration

The frontend uses the `NEXT_PUBLIC_API_URL` value by default, falling back to `http://localhost:8000`.
