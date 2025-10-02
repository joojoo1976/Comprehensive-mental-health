
# نماذج العيادات والمستشفيات

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ClinicType(enum.Enum):
    MENTAL_HEALTH_CENTER = "mental_health_center"
    PSYCHIATRY_CLINIC = "psychiatry_clinic"
    PSYCHOLOGY_CLINIC = "psychology_clinic"
    HOSPITAL = "hospital"
    COMMUNITY_HEALTH_CENTER = "community_health_center"
    SPECIALIZED_CENTER = "specialized_center"


class ClinicStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_MAINTENANCE = "under_maintenance"


class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_ar = Column(String, nullable=True)  # الاسم باللغة العربية
    name_en = Column(String, nullable=True)  # الاسم باللغة الإنجليزية
    name_fr = Column(String, nullable=True)  # الاسم باللغة الفرنسية
    type = Column(Enum(ClinicType), nullable=False)
    status = Column(Enum(ClinicStatus), default=ClinicStatus.ACTIVE)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)  # الوصف باللغة العربية
    description_en = Column(Text, nullable=True)  # الوصف باللغة الإنجليزية
    description_fr = Column(Text, nullable=True)  # الوصف باللغة الفرنسية

    # الموقع الجغرافي
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    address_ar = Column(String, nullable=True)  # العنوان باللغة العربية
    address_en = Column(String, nullable=True)  # العنوان باللغة الإنجليزية
    address_fr = Column(String, nullable=True)  # العنوان باللغة الفرنسية
    city = Column(String, nullable=False)
    city_ar = Column(String, nullable=True)  # المدينة باللغة العربية
    city_en = Column(String, nullable=True)  # المدينة باللغة الإنجليزية
    city_fr = Column(String, nullable=True)  # المدينة باللغة الفرنسية
    country = Column(String, nullable=False)
    country_ar = Column(String, nullable=True)  # الدولة باللغة العربية
    country_en = Column(String, nullable=True)  # الدولة باللغة الإنجليزية
    country_fr = Column(String, nullable=True)  # الدولة باللغة الفرنسية
    postal_code = Column(String, nullable=True)

    # معلومات الاتصال
    phone = Column(String, nullable=True)
    phone_alternative = Column(String, nullable=True)
    email = Column(String, nullable=True)
    website = Column(String, nullable=True)

    # معلومات التشغيل
    opening_hours = Column(String, nullable=True)  # JSON
    emergency_services = Column(Boolean, default=False)
    insurance_accepted = Column(String, nullable=True)  # JSON

    # التقييمات
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)

    # الصور
    images = Column(String, nullable=True)  # JSON

    # وسائل التواصل الاجتماعي
    social_media = Column(String, nullable=True)  # JSON

    # المعلومات الإضافية
    specialties = Column(String, nullable=True)  # JSON
    languages_spoken = Column(String, nullable=True)  # JSON

    # التسجيل
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    name = Column(String, nullable=False)
    name_ar = Column(String, nullable=True)  # الاسم باللغة العربية
    name_en = Column(String, nullable=True)  # الاسم باللغة الإنجليزية
    name_fr = Column(String, nullable=True)  # الاسم باللغة الفرنسية

    # المعلومات الشخصية
    title = Column(String, nullable=True)
    title_ar = Column(String, nullable=True)  # اللقب باللغة العربية
    title_en = Column(String, nullable=True)  # اللقب باللغة الإنجليزية
    title_fr = Column(String, nullable=True)  # اللقب باللغة الفرنسية
    bio = Column(Text, nullable=True)
    bio_ar = Column(Text, nullable=True)  # السيرة الذاتية باللغة العربية
    bio_en = Column(Text, nullable=True)  # السيرة الذاتية باللغة الإنجليزية
    bio_fr = Column(Text, nullable=True)  # السيرة الذاتية باللغة الفرنسية

    # التخصصات
    specialties = Column(String, nullable=True)  # JSON

    # معلومات الاتصال
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    # معلومات التشغيل
    working_days = Column(String, nullable=True)  # JSON
    working_hours = Column(String, nullable=True)  # JSON
    consultation_fee = Column(Float, nullable=True)
    consultation_fee_currency = Column(String, default="USD")

    # التقييمات
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)

    # الصور
    image = Column(String, nullable=True)

    # وسائل التواصل الاجتماعي
    social_media = Column(String, nullable=True)  # JSON

    # اللغات التي يتحدثها
    languages = Column(String, nullable=True)  # JSON

    # التسجيل
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ClinicReview(Base):
    __tablename__ = "clinic_reviews"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    comment_ar = Column(Text, nullable=True)  # التعليق باللغة العربية
    comment_en = Column(Text, nullable=True)  # التعليق باللغة الإنجليزية
    comment_fr = Column(Text, nullable=True)  # التعليق باللغة الفرنسية

    # التسجيل
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DoctorReview(Base):
    __tablename__ = "doctor_reviews"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    comment_ar = Column(Text, nullable=True)  # التعليق باللغة العربية
    comment_en = Column(Text, nullable=True)  # التعليق باللغة الإنجليزية
    comment_fr = Column(Text, nullable=True)  # التعليق باللغة الفرنسية

    # التسجيل
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ClinicFavorite(Base):
    __tablename__ = "clinic_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DoctorFavorite(Base):
    __tablename__ = "doctor_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ClinicService(Base):
    __tablename__ = "clinic_services"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    name = Column(String, nullable=False)
    name_ar = Column(String, nullable=True)  # الاسم باللغة العربية
    name_en = Column(String, nullable=True)  # الاسم باللغة الإنجليزية
    name_fr = Column(String, nullable=True)  # الاسم باللغة الفرنسية
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)  # الوصف باللغة العربية
    description_en = Column(Text, nullable=True)  # الوصف باللغة الإنجليزية
    description_fr = Column(Text, nullable=True)  # الوصف باللغة الفرنسية
    price = Column(Float, nullable=True)
    price_currency = Column(String, default="USD")
    duration = Column(Integer, nullable=True)  # بالدقائق
    is_available = Column(Boolean, default=True)

    # التسجيل
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# العلاقات
Clinic.doctors = relationship("Doctor", back_populates="clinic")
Clinic.reviews = relationship("ClinicReview", back_populates="clinic")
Clinic.favorites = relationship("ClinicFavorite", back_populates="clinic")
Clinic.services = relationship("ClinicService", back_populates="clinic")

Doctor.clinic = relationship("Clinic", back_populates="doctors")
Doctor.reviews = relationship("DoctorReview", back_populates="doctor")
Doctor.favorites = relationship("DoctorFavorite", back_populates="doctor")

ClinicReview.clinic = relationship("Clinic", back_populates="reviews")
ClinicReview.user = relationship("User")

DoctorReview.doctor = relationship("Doctor", back_populates="reviews")
DoctorReview.user = relationship("User")

ClinicFavorite.clinic = relationship("Clinic", back_populates="favorites")
ClinicFavorite.user = relationship("User")

DoctorFavorite.doctor = relationship("Doctor", back_populates="favorites")
DoctorFavorite.user = relationship("User")

ClinicService.clinic = relationship("Clinic", back_populates="services")
