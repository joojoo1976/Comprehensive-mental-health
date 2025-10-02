# نماذج الجلسات (Schemas)

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.models.session import SessionType, SessionStatus

# Base schemas


class SessionBase(BaseModel):
    session_type: SessionType
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_time: datetime
    duration: int  # بالدقائق


class SessionCreate(SessionBase):
    therapist_id: Optional[int] = None


class SessionUpdate(BaseModel):
    status: Optional[SessionStatus] = None
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    duration: Optional[int] = None


class SessionInDBBase(SessionBase):
    id: int
    user_id: int
    therapist_id: Optional[int] = None
    status: SessionStatus
    recording_url: Optional[str] = None
    recording_available: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Session(SessionInDBBase):
    pass


class SessionParticipantBase(BaseModel):
    session_id: int
    user_id: int


class SessionParticipantCreate(SessionParticipantBase):
    pass


class SessionParticipantInDBBase(SessionParticipantBase):
    id: int
    joined_at: datetime
    left_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SessionParticipant(SessionParticipantInDBBase):
    pass


class SessionFeedbackBase(BaseModel):
    session_id: int
    rating: int  # 1-5
    comment: Optional[str] = None


class SessionFeedbackCreate(SessionFeedbackBase):
    pass


class SessionFeedbackInDBBase(SessionFeedbackBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class SessionFeedback(SessionFeedbackInDBBase):
    pass


class SessionAnalysisBase(BaseModel):
    session_id: int
    emotional_analysis: Optional[str] = None  # JSON
    voice_analysis: Optional[str] = None  # JSON
    content_analysis: Optional[str] = None  # JSON
    summary: Optional[str] = None
    recommendations: Optional[str] = None  # JSON


class SessionAnalysisCreate(SessionAnalysisBase):
    pass


class SessionAnalysisInDBBase(SessionAnalysisBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class SessionAnalysis(SessionAnalysisInDBBase):
    pass
