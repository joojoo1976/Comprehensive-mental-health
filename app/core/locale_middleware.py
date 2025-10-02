
# middleware للتعامل مع اللغة

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.i18n import translator, i18n_settings
from app.core.locale_session import locale_session_manager
from app.core.consent import consent_manager
from app.core.security import verify_token, get_current_user
from app.models.user import User as UserModel
from sqlalchemy.orm import Session
from app.core.database import get_db


class LocaleMiddleware(BaseHTTPMiddleware):
    """Middleware للتعامل مع اللغة"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        معالجة الطلب وتحديد اللغة المناسبة

        Args:
            request: كائن الطلب
            call_next: الدالة التالية في سلسلة الوسيط

        Returns:
            كائن الاستجابة
        """
        # الحصول على معرف المستخدم إذا كان مسجلاً
        user_id = None
        token = request.headers.get("Authorization")

        if token and token.startswith("Bearer "):
            token_value = token.split(" ")[1]
            # التحقق من الرمز
            user_id = verify_token(token_value)

        # الحصول على اللغة من الطلب
        locale = locale_session_manager.get_locale_from_request(
            request, user_id)

        # تعيين اللغة
        translator.set_locale(locale)

        # معالجة الطلب
        response = await call_next(request)

        # إذا كان المستخدم مسجلاً وحصل على موافقة للغة، قم بتحديث الجلسة
        if user_id:
            db: Session = next(get_db())
            consent_status = consent_manager.get_consent_status(db, user_id)
            db.close()
            if consent_status["consent_given"] and consent_status["preferred_locale"]:
                # تحديث الجلسة اللغوية
                session_id = request.cookies.get("locale_session")
                if session_id:
                    locale_session_manager.update_session_locale(
                        session_id, consent_status["preferred_locale"])

        return response


class LocaleConsentMiddleware(BaseHTTPMiddleware):
    """Middleware للتعامل مع موافقة اللغة"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        التحقق من موافقة اللغة للمستخدم

        Args:
            request: كائن الطلب
            call_next: الدالة التالية في سلسلة الوسيط

        Returns:
            كائن الاستجابة
        """
        # الحصول على المسار
        path = request.url.path

        # استثناء المسارات التي لا تتطلب موافقة اللغة
        if path.startswith("/api/v1/language/") or path == "/login" or path == "/register":
            return await call_next(request)

        # الحصول على معرف المستخدم إذا كان مسجلاً
        user_id = None
        token = request.headers.get("Authorization")

        if token and token.startswith("Bearer "):
            try:
                token_value = token.split(" ")[1]
                # التحقق من الرمز
                user_id = verify_token(token_value)
            except:
                pass

        # إذا كان المستخدم مسجلاً والتطبيق يتطلب موافقة اللغة
        if user_id:
            db: Session = next(get_db())
            consent_status = consent_manager.get_consent_status(db, user_id)
            db.close()

            # إذا لم يوافق المستخدم بعد، أعد توجيهه إلى صفحة الموافقة
            if not consent_status["consent_given"]:
                # في التطبيق الحقيقي، سيتم إعادة توجيه المستخدم إلى صفحة الموافقة
                # هنا سنضيف رأس HTTP لإعلام العميل
                response = await call_next(request)
                response.headers["X-Translation-Consent-Required"] = "true"
                return response

        # معالجة الطلب العادي
        return await call_next(request)


class LocaleRedirectMiddleware(BaseHTTPMiddleware):
    """Middleware لإعادة توجيه المستخدمين بناءً على لغتهم"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        إعادة توجيه المستخدمين بناءً على لغتهم

        Args:
            request: كائن الطلب
            call_next: الدالة التالية في سلسلة الوسيط

        Returns:
            كائن الاستجابة
        """
        # الحصول على المسار
        path = request.url.path

        # استثناء المسارات التي لا تتطلب إعادة التوجيه
        if path.startswith("/api/") or path == "/login" or path == "/register":
            return await call_next(request)

        # الحصول على معرف المستخدم إذا كان مسجلاً
        user_id = None
        token = request.headers.get("Authorization")

        if token and token.startswith("Bearer "):
            try:
                token_value = token.split(" ")[1]
                # التحقق من الرمز
                user_id = verify_token(token_value)
            except:
                pass

        # إذا كان المستخدم مسجلاً
        if user_id:
            db: Session = next(get_db())
            consent_status = consent_manager.get_consent_status(db, user_id)
            db.close()

            # إذا كان المستخدم قد وافق على لغة معينة
            if consent_status["consent_given"] and consent_status["preferred_locale"]:
                # إذا كانت اللغة الحالية مختلفة عن لغة المستخدم المفضلة
                if translator.current_locale != consent_status["preferred_locale"]:
                    # في التطبيق الحقيقي، سيتم إعادة توجيه المستخدم إلى نفس الصفحة باللغة المفضلة
                    # هنا سنضيف رأس HTTP لإعلام العميل
                    response = await call_next(request)
                    response.headers["X-Redirect-URL"] = f"/{consent_status['preferred_locale']}{path}"
                    response.headers["X-Redirect-Reason"] = "language_preference"
                    return response

        # معالجة الطلب العادي
        return await call_next(request)
