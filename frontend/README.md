# Pulse AI Interview Agent — Frontend

This directory is designated for the Next.js frontend web application for **Pulse AI Interview Agent**.

## Tech Stack (Locked)

- **Framework**: Next.js (App Router, React, TypeScript)
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui

## Backend API Integration

The frontend connects to the backend FastAPI endpoint:

- **Endpoint**: `POST http://localhost:8000/api/interview`

### Request Examples

```typescript
// Initial turn
const res = await fetch("http://localhost:8000/api/interview", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    sessionId: "session-123",
    candidate: candidateProfileData,
  }),
});

// Subsequent turns
const res = await fetch("http://localhost:8000/api/interview", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    sessionId: "session-123",
    message: candidateAnswer,
  }),
});
```

> **Note**: Full Next.js client interface and interactive components will be implemented in subsequent project phases.
