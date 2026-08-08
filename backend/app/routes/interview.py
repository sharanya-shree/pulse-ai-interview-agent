import json
from pathlib import Path

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.interview import InterviewRequest, InterviewResponse
from app.core.database import get_db
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/api", tags=["Interview"])
interview_service = InterviewService()


@router.get("/candidates")
def get_candidates() -> dict:
    """Expose the official ABTalks candidate catalog to the frontend."""
    candidate_file = Path(__file__).resolve().parents[3] / "docs" / "abtalks" / "candidates.json"
    with candidate_file.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return {"candidates": payload.get("candidates", [])}


@router.post(
    "/interview",
    response_model=InterviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Conduct Interview Turn",
    description="Primary HTTP endpoint for initial session start and subsequent interview message turns."
)
async def conduct_interview(
    payload: InterviewRequest,
    db: Session = Depends(get_db)
) -> InterviewResponse:
    """
    HTTP endpoint defined by Technical Specification:
    Accepts sessionId along with candidate info (initial turn) or message (subsequent turn).
    Routes state through LangGraph workflow and saves state in database.
    Returns reply, done flag, and feedback if done.
    """
    try:
        result = interview_service.conduct_interview_turn(
            session_id=payload.session_id,
            candidate_data=payload.candidate,
            message=payload.message,
            db=db
        )
        return InterviewResponse(
            reply=result["reply"],
            done=result["done"],
            feedback=result["feedback"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred executing interview turn: {str(e)}"
        )
