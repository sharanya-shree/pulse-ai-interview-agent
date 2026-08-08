import re
from sqlalchemy.orm import Session
from app.models.db import InterviewSessionModel, InterviewStatus
from app.services.workflow import compiled_graph
from typing import Dict, Any, Optional

class InterviewService:
    """Service to coordinate DB states and execute LangGraph state turns."""

    @staticmethod
    def _normalize_session_id(session_id: Optional[str]) -> str:
        normalized = (session_id or "").strip()
        if not normalized:
            raise ValueError("A non-empty session_id is required.")
        if len(normalized) > 255:
            raise ValueError("session_id is too long.")
        return normalized

    @staticmethod
    def _normalize_candidate_data(candidate_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if candidate_data is None:
            return None
        if not isinstance(candidate_data, dict):
            raise ValueError("candidate data must be a JSON object.")

        normalized = dict(candidate_data)
        for key in ["id", "name", "experienceLevel", "experience_level", "jobRole", "job_role", "education"]:
            if key in normalized and normalized[key] is not None:
                normalized[key] = str(normalized[key]).strip()

        completed_days = normalized.get("completedDays", normalized.get("completed_days", []))
        if isinstance(completed_days, list):
            normalized["completedDays"] = [int(day) for day in completed_days if str(day).strip().isdigit()]
        else:
            normalized["completedDays"] = []

        return normalized

    @staticmethod
    def _normalize_message(message: Optional[str]) -> Optional[str]:
        if message is None:
            return None
        normalized = re.sub(r"\s+", " ", message).strip()
        return normalized or None
    
    def conduct_interview_turn(
        self,
        session_id: str,
        candidate_data: Optional[Dict[str, Any]],
        message: Optional[str],
        db: Session
    ) -> Dict[str, Any]:
        session_id = self._normalize_session_id(session_id)
        normalized_message = self._normalize_message(message)

        # 1. Fetch existing session model
        model = db.query(InterviewSessionModel).filter(
            InterviewSessionModel.session_id == session_id
        ).first()

        # 2. Handle initial session configuration
        if candidate_data is not None:
            normalized_candidate = self._normalize_candidate_data(candidate_data)
            if normalized_candidate is None:
                raise ValueError("candidate data must be provided for a new interview session.")
            if model and model.status == InterviewStatus.COMPLETED:
                model.conversation_history = []
                model.questions_asked = []
                model.curriculum_days_covered = []
                model.current_topic = None
                model.status = InterviewStatus.IN_PROGRESS
                model.feedback = None
            if model:
                # Reset existing session to start fresh
                model.candidate_data = normalized_candidate
                model.conversation_history = []
                model.questions_asked = []
                model.curriculum_days_covered = []
                model.current_topic = None
                model.status = InterviewStatus.IN_PROGRESS
                model.feedback = None
            else:
                # Create a new session row
                model = InterviewSessionModel(
                    session_id=session_id,
                    candidate_data=normalized_candidate,
                    conversation_history=[],
                    questions_asked=[],
                    curriculum_days_covered=[],
                    current_topic=None,
                    status=InterviewStatus.IN_PROGRESS,
                    feedback=None
                )
                db.add(model)

            db.commit()
            db.refresh(model)
            # Initial setup carries no candidate reply yet
            normalized_message = None

        if not model:
            raise ValueError(
                f"Session '{session_id}' not found. Please initialize session with candidate profile data first."
            )

        if model.status == InterviewStatus.COMPLETED and normalized_message is not None:
            raise ValueError("This interview session has already been completed.")

        if normalized_message is None and candidate_data is None:
            normalized_message = None
            if model:
                # Reset existing session to start fresh
                model.candidate_data = candidate_data
                model.conversation_history = []
                model.questions_asked = []
                model.curriculum_days_covered = []
                model.current_topic = None
                model.status = InterviewStatus.IN_PROGRESS
                model.feedback = None
            else:
                # Create a new session row
                model = InterviewSessionModel(
                    session_id=session_id,
                    candidate_data=candidate_data,
                    conversation_history=[],
                    questions_asked=[],
                    curriculum_days_covered=[],
                    current_topic=None,
                    status=InterviewStatus.IN_PROGRESS,
                    feedback=None
                )
                db.add(model)
            
            db.commit()
            db.refresh(model)
            # Initial setup carries no candidate reply yet
            message = None

        if not model:
            raise ValueError(
                f"Session '{session_id}' not found. Please initialize session with candidate profile data first."
            )

        # 3. Build initial LangGraph workflow state dict
        candidate = model.candidate_data or {}
        # Keep evaluation history nested inside candidate_data JSON to preserve database columns
        collected_evals = candidate.get("_collected_info", {})

        initial_state = {
            "session_id": model.session_id,
            "candidate_data": candidate,
            "conversation_history": model.conversation_history or [],
            "completed_curriculum_days": candidate.get("completedDays", []),
            "questions_asked": model.questions_asked or [],
            "curriculum_days_covered": model.curriculum_days_covered or [],
            "number_of_questions_asked": len(model.questions_asked or []),
            "current_question": model.questions_asked[-1] if model.questions_asked else "",
            "current_topic": model.current_topic or "",
            "is_completed": model.status == InterviewStatus.COMPLETED,
            "collected_information": collected_evals,
            "feedback": model.feedback,
            "last_message": normalized_message
        }

        # 4. Invoke compiled LangGraph state machine
        final_state = compiled_graph.invoke(initial_state)

        # 5. Persist workflow results back to database model
        model.conversation_history = final_state["conversation_history"]
        model.questions_asked = final_state["questions_asked"]
        model.curriculum_days_covered = final_state["curriculum_days_covered"]
        model.current_topic = final_state["current_topic"]
        
        if final_state["is_completed"]:
            model.status = InterviewStatus.COMPLETED
            model.feedback = final_state["feedback"]
        else:
            model.status = InterviewStatus.IN_PROGRESS
            model.feedback = None

        # Nested save of internal evaluation logs
        updated_candidate = dict(candidate)
        updated_candidate["_collected_info"] = final_state["collected_information"]
        model.candidate_data = updated_candidate

        db.commit()
        db.refresh(model)

        # Find the last reply message text generated by the assistant
        reply = ""
        for msg in reversed(model.conversation_history):
            if msg.get("role") == "assistant":
                reply = msg.get("content", "")
                break

        return {
            "reply": reply,
            "done": model.status == InterviewStatus.COMPLETED,
            "feedback": model.feedback
        }
