# نماذج الجلسات

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class SessionType(enum.Enum):
    VIDEO = "video"
    TEXT = "text"
    AUDIO = "audio"
    GROUP = "group"


class SessionStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    therapist_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_type = Column(Enum(SessionType), nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Integer, nullable=False)  # بالدقائق
    recording_url = Column(String, nullable=True)
    recording_available = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    user = relationship("User", foreign_keys=[
                        user_id], back_populates="sessions")
    therapist = relationship("User", foreign_keys=[therapist_id])
    participants = relationship("SessionParticipant", back_populates="session")
    feedbacks = relationship("SessionFeedback", back_populates="session")
    analyses = relationship("SessionAnalysis", back_populates="session")


class SessionParticipant(Base):
    __tablename__ = "session_participants"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)

    # العلاقات
    session = relationship("Session", back_populates="participants")
    user = relationship("User")


class SessionFeedback(Base):
    __tablename__ = "session_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    session = relationship("Session", back_populates="feedbacks")
    user = relationship("User", back_populates="session_feedbacks")


class SessionAnalysis(Base):
    __tablename__ = "session_analyses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    emotional_analysis = Column(Text, nullable=True)  # JSON
    voice_analysis = Column(Text, nullable=True)  # JSON
    content_analysis = Column(Text, nullable=True)  # JSON
    summary = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    session = relationship("Session", back_populates="analyses")
