# نماذج المستخدمين

from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class UserRole(enum.Enum):
    USER = "user"
    THERAPIST = "therapist"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    role = relationship("Role", back_populates="users")
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    preferences = relationship(
        "UserPreferences", back_populates="user", uselist=False)
    sessions = relationship("Session", back_populates="user")
    mood_entries = relationship("MoodEntry", back_populates="user")
    sleep_entries = relationship("SleepEntry", back_populates="user")
    activity_entries = relationship("ActivityEntry", back_populates="user")
    bookmarks = relationship("ArticleBookmark", back_populates="user")
    program_enrollments = relationship(
        "ProgramEnrollment", back_populates="user")
    group_memberships = relationship("GroupMembership", back_populates="user")
    digital_biomarkers = relationship(
        "DigitalBiomarker", back_populates="user")
    life_inflection_points = relationship(
        "LifeInflectionPoint", back_populates="user")
    session_feedbacks = relationship("SessionFeedback", back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    birth_date = Column(DateTime(timezone=True), nullable=True)
    gender = Column(String, nullable=True)
    location = Column(String, nullable=True)
    language = Column(String, default="ar")
    notification_preferences = Column(String, nullable=True)
    privacy_settings = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    user = relationship("User", back_populates="profile")


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meditation_reminders = Column(Boolean, default=True)
    sleep_reminders = Column(Boolean, default=True)
    activity_reminders = Column(Boolean, default=True)
    mood_check_ins = Column(Boolean, default=True)
    preferred_meditation_length = Column(Integer, default=10)  # بالدقائق
    preferred_sleep_reminder_time = Column(String, default="22:00")
    preferred_activity_reminder_time = Column(String, default="09:00")
    preferred_mood_check_in_time = Column(String, default="20:00")
    content_categories = Column(String, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    user = relationship("User", back_populates="preferences")
