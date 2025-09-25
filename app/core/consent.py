
# نظام موافقة المستخدم للغة

import json
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.i18n.translation_manager import translator
from app.core.geolocation import geolocation_service

class LanguageConsent(Base):
    """نموذج موافقة المستخدم على اللغة"""
    __tablename__ = "language_consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consent_given = Column(Boolean, default=False)
    preferred_locale = Column(String, nullable=True)
    locale_source = Column(String, nullable=True)  # manual, browser, ip, device
    consent_data = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    user = relationship("User")

class LanguageConsentManager:
    """مدير موافقة المستخدم على اللغة"""

    def __init__(self):
        """تهيئة مدير موافقة المستخدم"""
        pass

    def get_consent_status(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        الحصول على حالة موافقة المستخدم

        Args:
            db: جلسة قاعدة البيانات
            user_id: معرف المستخدم

        Returns:
            قاموس يحتوي على حالة الموافقة
        """
        consent = db.query(LanguageConsent).filter(LanguageConsent.user_id == user_id).first()

        if consent:
            return {
                "consent_given": consent.consent_given,
                "preferred_locale": consent.preferred_locale,
                "locale_source": consent.locale_source,
                "consent_data": json.loads(consent.consent_data) if consent.consent_data else None
            }
        else:
            return {
                "consent_given": False,
                "preferred_locale": None,
                "locale_source": None,
                "consent_data": None
            }

    def record_consent(self, db: Session, user_id: int, consent_given: bool,
                      preferred_locale: Optional[str] = None,
                      locale_source: Optional[str] = None,
                      consent_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        تسجيل موافقة المستخدم

        Args:
            db: جلسة قاعدة البيانات
            user_id: معرف المستخدم
            consent_given: ما إذا كان المستخدم قد وافق أم لا
            preferred_locale: اللغة المفضلة للمستخدم
            locale_source: مصدر اللغة (manual, browser, ip, device)
            consent_data: بيانات إضافية حول الموافقة

        Returns:
            قاموس يحتوي على حالة الموافقة بعد التسجيل
        """
        # البحث عن سجل موافقة حالي
        consent = db.query(LanguageConsent).filter(LanguageConsent.user_id == user_id).first()

        if not consent:
            # إنشاء سجل جديد إذا لم يكن موجودًا
            consent = LanguageConsent(user_id=user_id)
            db.add(consent)

        # تحديث البيانات
        consent.consent_given = consent_given
        consent.preferred_locale = preferred_locale
        consent.locale_source = locale_source
        consent.consent_data = json.dumps(consent_data) if consent_data else None

        db.commit()
        db.refresh(consent)

        response_data = {
            "consent_given": consent_given,
            "preferred_locale": preferred_locale,
            "locale_source": locale_source,
            "consent_data": consent_data
        }
        return response_data

    def get_locale_with_consent(self, db: Session, user_id: int, request = None, ip_address: str = None) -> str:
        """
        الحصول على اللغة المناسبة للمستخدم مع مراعاة موافقته

        Args:
            user_id: معرف المستخدم
            request: كائن الطلب (اختياري)
            ip_address: عنوان IP (اختياري)

        Returns:
            رمز اللغة المناسبة
        """
        # الحصول على حالة الموافقة
        consent_status = self.get_consent_status(db, user_id)

        # إذا كان المستخدم قد وافق على استخدام لغة معينة، استخدمها
        if consent_status["consent_given"] and consent_status["preferred_locale"]:
            return consent_status["preferred_locale"]

        # إذا لم يوافق المستخدم بعد، اطلب الموافقة
        if not consent_status["consent_given"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "translation_consent_required",
                    "description": "translation_consent_description"
                }
            )

        # إذا لم يحدد المستخدم لغة، استخدم اللغة الافتراضية للنظام
        return translator.current_locale

    def get_locale_options(self) -> Dict[str, Dict[str, str]]:
        """
        الحصول على خيارات اللغة المتاحة

        Returns:
            قاموس يحتوي على خيارات اللغة
        """
        locales = {}

        # الحصول على اللغات المدعومة
        for locale_code in translator.translations.keys():
            locales[locale_code] = {
                "name": translator.get_translation(f"language_name.{locale_code}", locale_code),
                "native_name": translator.get_translation(f"language_native_name.{locale_code}", locale_code),
                # قراءة خاصية RTL ديناميكيًا من ملف الترجمة
                # القيمة الافتراضية هي False إذا لم يتم العثور على المفتاح
                "rtl": translator.get_translation("is_rtl", lang_code=locale_code) is True
            }

        return locales

# إنشاء مثيل من مدير موافقة المستخدم
consent_manager = LanguageConsentManager()
