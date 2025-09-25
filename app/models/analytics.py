# نماذج التحليلات

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood_score = Column(Integer, nullable=False)  # 1-10
    emotion = Column(String, nullable=True)  # فرح، حزن، غضب، قلق، إلخ
    notes = Column(Text, nullable=True)
    triggers = Column(String, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    user = relationship("User", back_populates="mood_entries")

class SleepEntry(Base):
    __tablename__ = "sleep_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sleep_duration = Column(Float, nullable=False)  # بالساعات
    sleep_quality = Column(Integer, nullable=False)  # 1-10
    bedtime = Column(DateTime(timezone=True), nullable=True)
    wake_time = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    user = relationship("User", back_populates="sleep_entries")

class ActivityEntry(Base):
    __tablename__ = "activity_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # بالدقائق
    intensity = Column(Integer, nullable=False)  # 1-10
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    user = relationship("User", back_populates="activity_entries")

class DigitalBiomarker(Base):
    __tablename__ = "digital_biomarkers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    biomarker_type = Column(String, nullable=False)  # typing_speed, sleep_pattern, activity_pattern, إلخ
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(String, nullable=True)  # JSON

    # العلاقات
    user = relationship("User", back_populates="digital_biomarkers")

class LifeInflectionPoint(Base):
    __tablename__ = "life_inflection_points"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False)  # job_loss, relationship_end, relocation, إلخ
    event_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=True)
    impact_level = Column(Integer, nullable=False)  # 1-10
    coping_strategies = Column(String, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    user = relationship("User", back_populates="life_inflection_points")

class WellnessScore(Base):
    __tablename__ = "wellness_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Float, nullable=False)  # 0-100
    components = Column(String, nullable=True)  # JSON
    date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    user = relationship("User")

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    insight_type = Column(String, nullable=False)  # pattern, recommendation, milestone, إلخ
    confidence_level = Column(Integer, nullable=False)  # 1-10
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    user = relationship("User")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    recommendation_type = Column(String, nullable=False)  # activity, content, session, إلخ
    target_id = Column(Integer, nullable=True)  # ID للهدف (مقال، تمرين، إلخ)
    priority = Column(Integer, nullable=False)  # 1-10
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # العلاقات
    user = relationship("User")

class ProgressReport(Base):
    __tablename__ = "progress_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    period_type = Column(String, nullable=False)  # day, week, month, year
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    mood_trend = Column(String, nullable=True)  # improving, stable, declining
    sleep_quality_trend = Column(String, nullable=True)  # improving, stable, declining
    activity_level_trend = Column(String, nullable=True)  # increasing, stable, decreasing
    achievements = Column(String, nullable=True)  # JSON
    challenges = Column(String, nullable=True)  # JSON
    recommendations = Column(String, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    user = relationship("User")

class GlobalMentalHealthInsights(Base):
    __tablename__ = "global_mental_health_insights"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, nullable=True)
    insight_type = Column(String, nullable=False)  # trend, statistic, pattern, إلخ
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    data_source = Column(String, nullable=True)
    confidence_level = Column(Integer, nullable=False)  # 1-10
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    users = relationship("User")
