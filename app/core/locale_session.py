
# إدارة الجلسات اللغوية

from typing import Optional, Dict, Any
from fastapi import Request, Response
from datetime import datetime, timedelta
import uuid
import json
from app.core.i18n import translator, i18n_settings
from app.core.consent import consent_manager


class LocaleSessionManager:
    """مدير الجلسات اللغوية"""

    def __init__(self):
        """تهيئة مدير الجلسات اللغوية"""
        self.sessions = {}
        self.session_lifetime = timedelta(hours=24)  # مدة صلاحية الجلسة

    def create_session(self, user_id: int, locale: str = None) -> str:
        """
        إنشاء جلسة لغوية جديدة

        Args:
            user_id: معرف المستخدم
            locale: اللغة المطلبة (اختياري)

        Returns:
            معرف الجلسة
        """
        # التحقق من صحة اللغة
        if locale and locale not in i18n_settings.supported_locales:
            locale = i18n_settings.default_locale

        # إنشاء معرف الجلسة
        session_id = str(uuid.uuid4())

        # إنشاء بيانات الجلسة
        session_data = {
            "user_id": user_id,
            "locale": locale or translator.current_locale,
            "created_at": datetime.utcnow(),
            "last_used": datetime.utcnow()
        }

        # حفظ الجلسة
        self.sessions[session_id] = session_data

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        الحصول على بيانات الجلسة

        Args:
            session_id: معرف الجلسة

        Returns:
            بيانات الجلسة أو None إذا لم توجد
        """
        # التحقق مما إذا كانت الجلسة موجودة
        if session_id not in self.sessions:
            return None

        # تحقق من صلاحية الجلسة
        session_data = self.sessions[session_id]
        if datetime.utcnow() - session_data["last_used"] > self.session_lifetime:
            del self.sessions[session_id]
            return None

        # تحديث وقت استخدام الجلسة
        session_data["last_used"] = datetime.utcnow()
        self.sessions[session_id] = session_data

        return session_data

    def update_session_locale(self, session_id: str, locale: str) -> bool:
        """
        تحديث اللغة في الجلسة

        Args:
            session_id: معرف الجلسة
            locale: اللغة الجديدة

        Returns:
            True إذا نجحت العملية، False إذا لم تكن الجلسة صالحة
        """
        # الحصول على الجلسة
        session_data = self.get_session(session_id)
        if not session_data:
            return False

        # التحقق من صحة اللغة
        if locale not in i18n_settings.supported_locales:
            return False

        # تحديث اللغة
        session_data["locale"] = locale
        self.sessions[session_id] = session_data

        # تحديث اللغة العامة
        translator.set_locale(locale)

        return True

    def delete_session(self, session_id: str) -> bool:
        """
        حذف جلسة

        Args:
            session_id: معرف الجلسة

        Returns:
            True إذا نجحت العملية، False إذا لم تكن الجلسة موجودة
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def get_locale_from_request(self, request: Request, user_id: int = None) -> str:
        """
        الحصول على اللغة من الطلب

        Args:
            request: كائن الطلب
            user_id: معرف المستخدم (اختياري)

        Returns:
            رمز اللغة
        """
        # التحقق من وجود ملف تعريف ارتباط الجلسة
        session_id = request.cookies.get("locale_session")
        if session_id:
            session_data = self.get_session(session_id)
            if session_data:
                return session_data["locale"]

        # التحقق من وجود اللغة في رؤوس الطلب
        locale = request.headers.get("X-Locale")
        if locale and locale in i18n_settings.supported_locales:
            return locale

        # التحقق من وجود اللغة في معاملات الطلب
        locale = request.query_params.get("locale")
        if locale and locale in i18n_settings.supported_locales:
            return locale

        # الحصول على اللغة من المتصفح
        locale = translator.get_user_locale_from_browser(request)
        if locale and locale in i18n_settings.supported_locales:
            return locale

        # الحصول على اللغة من جهاز المستخدم
        locale = translator.get_locale_by_device_language()
        if locale and locale in i18n_settings.supported_locales:
            return locale

        # إذا كان المستخدم مسجلاً، تحقق من موافقته للغة
        if user_id:
            consent_status = consent_manager.get_consent_status(user_id)
            if consent_status["consent_given"] and consent_status["preferred_locale"]:
                return consent_status["preferred_locale"]

        # العودة إلى اللغة الافتراضية
        return i18n_settings.default_locale

    def set_locale_cookie(self, response: Response, locale: str) -> Response:
        """
        تعيين ملف تعريف ارتباط اللغة

        Args:
            response: كائن الاستجابة
            locale: اللغة

        Returns:
            كائن الاستجابة المحدث
        """
        # تعيين ملف تعريف ارتباط اللغة
        response.set_cookie(
            key="locale",
            value=locale,
            httponly=False,
            max_age=86400,  # 24 ساعة
            expires=datetime.utcnow() + timedelta(hours=24),
            samesite="lax",
            secure=True  # في الإنتاج، يجب أن يكون True
        )

        return response

    def create_locale_session(self, request: Request, response: Response, user_id: int = None) -> str:
        """
        إنشاء جلسة لغوية جديدة

        Args:
            request: كائن الطلب
            response: كائن الاستجابة
            user_id: معرف المستخدم (اختياري)

        Returns:
            معرف الجلسة
        """
        # الحصول على اللغة المناسبة
        locale = self.get_locale_from_request(request, user_id)

        # إنشاء الجلسة
        session_id = self.create_session(user_id or 0, locale)

        # تعيين ملف تعريف ارتباط الجلسة
        response.set_cookie(
            key="locale_session",
            value=session_id,
            httponly=True,
            max_age=86400,  # 24 ساعة
            expires=datetime.utcnow() + timedelta(hours=24),
            samesite="lax",
            secure=True  # في الإنتاج، يجب أن يكون True
        )

        # تعيين ملف تعريف ارتباط اللغة
        self.set_locale_cookie(response, locale)

        return session_id


# إنشاء مثيل من مدير الجلسات اللغوية
locale_session_manager = LocaleSessionManager()
