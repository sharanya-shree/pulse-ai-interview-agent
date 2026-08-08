from fastapi import APIRouter, status, HTTPException
from app.models.interview import InterviewRequest, InterviewResponse, InterviewFeedback

router = APIRouter(prefix="/api", tags=["Interview"])


@router.post(
    "/interview",
    response_model=InterviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Conduct Interview Turn",
    description="Primary HTTP endpoint for initial session start and subsequent interview message turns."
)
async def conduct_interview(payload: InterviewRequest) -> InterviewResponse:
    """
    HTTP endpoint defined by Technical Specification:
    Accepts sessionId along with candidate info (initial turn) or message (subsequent turn).
    Returns reply, done flag, and feedback if done.
    """
    if payload.candidate is not None:
        # Initial interview session initiation turn
        candidate_name = payload.candidate.get("name", "Candidate")
        reply_msg = (
            f"Hello {candidate_name}! Welcome to your technical interview session ({payload.session_id}). "
            "I'm ready to begin our multi-turn conversation based on your learning journey."
        )
        return InterviewResponse(
            reply=reply_msg,
            done=False,
            feedback=None
        )
    elif payload.message is not None:
        # Subsequent candidate message turn
        reply_msg = (
            f"Received response for session {payload.session_id}: '{payload.message}'. "
            "Foundation endpoint is reachable. Ready for Person 2 AI Agent state workflow execution."
        )
        return InterviewResponse(
            reply=reply_msg,
            done=False,
            feedback=None
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload must include candidate data for session init or a candidate message answer."
        )
