from datetime import datetime, timezone
from sqlalchemy import Column, String, JSON, DateTime, Enum as SQLEnum
import enum
from app.core.database import Base


class InterviewStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class InterviewSessionModel(Base):
    """
    SQLAlchemy database model for interview session state persistence in PostgreSQL.
    """
    __tablename__ = "interview_sessions"

    session_id = Column(String(255), primary_key=True, index=True)
    candidate_data = Column(JSON, nullable=True)
    conversation_history = Column(JSON, default=list, nullable=False)
    questions_asked = Column(JSON, default=list, nullable=False)
    curriculum_days_covered = Column(JSON, default=list, nullable=False)
    current_topic = Column(String(255), nullable=True)
    status = Column(SQLEnum(InterviewStatus), default=InterviewStatus.IN_PROGRESS, nullable=False)
    feedback = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
