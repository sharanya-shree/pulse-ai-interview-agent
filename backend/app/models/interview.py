from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator


class CandidateData(BaseModel):
    """Candidate profile and learning journey data."""
    id: Optional[str] = None
    name: Optional[str] = None
    experience_level: Optional[str] = Field(default=None, alias="experienceLevel")
    skills: Optional[List[str]] = Field(default_factory=list)
    completed_days: Optional[List[int]] = Field(default_factory=list, alias="completedDays")
    learning_goals: Optional[List[str]] = Field(default_factory=list, alias="learningGoals")
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }


class InterviewFeedback(BaseModel):
    """Structured actionable feedback produced at interview end."""
    summary: str
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    next: List[str] = Field(default_factory=list)


class InterviewRequest(BaseModel):
    """
    API payload for POST /api/interview
    Supports initial request (with candidate data) and subsequent requests (with message answer).
    """
    session_id: str = Field(..., alias="sessionId")
    candidate: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("A non-empty session_id is required.")
        return value

    @model_validator(mode="after")
    def validate_payload(self):
        if not self.candidate and not self.message:
            raise ValueError("Request must contain either 'candidate' data or a 'message'.")
        return self

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "sessionId": "abc-123",
                "candidate": {
                    "id": "cand-01",
                    "name": "Jane Doe",
                    "experienceLevel": "Intermediate",
                    "completedDays": [1, 2, 3, 5, 8]
                }
            }
        }
    }


class InterviewResponse(BaseModel):
    """
    API response for POST /api/interview
    Returns reply text, done flag, and feedback if completed.
    """
    reply: str
    done: bool = False
    feedback: Optional[InterviewFeedback] = None

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "reply": "Welcome to the technical interview! Let's start with your experience in Day 1 topics.",
                "done": False,
                "feedback": None
            }
        }
    }
