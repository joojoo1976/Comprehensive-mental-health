
# نقاط نهاية API للغة

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.i18n import translator, i18n_settings, _
from app.core.consent import consent_manager
from app.core.geolocation import geolocation_service
from app.models.user import User
from app.schemas import language as language_schemas
from app.schemas.user import UserInDB
from app.core.security import get_current_user, PermissionChecker

router = APIRouter()


@router.get(
    "/consent",
    response_model=language_schemas.LanguageConsentStatusResponse,
    summary="الحصول على حالة موافقة اللغة",
    description="يسترجع حالة موافقة اللغة الحالية للمستخدم، بالإضافة إلى خيارات اللغة المتاحة واللغة المقترحة.",
)
async def get_language_consent(
    request: Request,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    الحصول على حالة موافقة اللغة للمستخدم

    Args:
        request: كائن الطلب
        current_user: المستخدم الحالي
        db: جلسة قاعدة البيانات

    Returns:
        قاموس يحتوي على حالة موافقة اللغة
    """
    # الحصول على حالة الموافقة
    consent_status = consent_manager.get_consent_status(db, current_user.id)

    # الحصول على خيارات اللغة المتاحة
    language_options = consent_manager.get_locale_options()

    # الحصول على اللغة المقترحة بناءً على الموقع الجغرافي
    client_ip = geolocation_service.get_client_ip(request)
    suggested_locale_from_ip = geolocation_service.get_locale_by_ip(client_ip)
    
    # إذا فشل تحديد الموقع، اقترح لغة المتصفح أو اللغة الافتراضية
    suggested_locale = suggested_locale_from_ip if suggested_locale_from_ip != i18n_settings.default_locale else translator.get_user_locale_from_browser(request) or i18n_settings.default_locale

    return {
        "consent_given": consent_status["consent_given"],
        "preferred_locale": consent_status["preferred_locale"],
        "locale_source": consent_status["locale_source"],
        "language_options": language_options,
        "suggested_locale": suggested_locale,
        "current_locale": translator.current_locale,
        "message": _("translation_consent_required"),
        "description": _("translation_consent_description")
    }


@router.post(
    "/consent",
    response_model=language_schemas.LanguageConsentRecordResponse,
    summary="تسجيل موافقة اللغة",
    description="يسجل قرار المستخدم بشأن موافقة اللغة.",
)
async def give_language_consent(
    consent_data: language_schemas.ConsentStatus,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    منح موافقة اللغة للمستخدم

    Args:
        request: كائن الطلب
        consent_data: بيانات الموافقة
        current_user: المستخدم الحالي
        db: جلسة قاعدة البيانات

    Returns:
        قاموس يحتوي على نتيجة الموافقة
    """
    consent_data_dict = consent_data.dict()
    # تسجيل الموافقة
    consent_result = consent_manager.record_consent(
        db=db,
        user_id=current_user.id,
        consent_given=consent_data.consent_given,
        preferred_locale=consent_data.preferred_locale,
        locale_source=consent_data.locale_source or "manual",
        consent_data=consent_data_dict
    )

    # إذا وافق المستخدم على اللغة، قم بتعيينها
    if consent_result["consent_given"] and consent_result["preferred_locale"]:
        translator.set_locale(consent_result["preferred_locale"])

    return {
        "success": True,
        "message": _("translation_consent_recorded"),
        "consent_status": consent_result
    }


@router.get(
    "/detect",
    response_model=language_schemas.LocaleDetectionResponse,
    summary="الكشف عن اللغة المناسبة",
    description="يكشف تلقائيًا عن أفضل لغة للمستخدم بناءً على تفضيلاته المحفوظة، والمتصفح، والموقع الجغرافي.",
)
async def detect_locale(
    request: Request,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    الكشف عن اللغة المناسبة للمستخدم

    Args:
        request: كائن الطلب
        current_user: المستخدم الحالي
        db: جلسة قاعدة البيانات

    Returns:
        قاموس يحتوي على اللغة المكتشفة
    """
    # الحصول على عنوان IP
    client_ip = geolocation_service.get_client_ip(request)

    # الحصول على اللغة بناءً على عنوان IP
    ip_locale = geolocation_service.get_locale_by_ip(client_ip)

    # الحصول على اللغة من المتصفح
    browser_locale = translator.get_user_locale_from_browser(request)

    # الحصول على لغة الجهاز
    device_locale = translator.get_locale_by_device_language()

    # الحصول على اللغة المفضلة للمستخدم إذا كان قد حددها
    consent_status = consent_manager.get_consent_status(db, current_user.id)
    user_locale = consent_status["preferred_locale"] if consent_status["consent_given"] else None

    # ترتيب اللغات حسب الأولوية
    locales = [
        ("manual", user_locale),
        ("browser", browser_locale),
        ("ip", ip_locale),
        ("device", device_locale),
        ("default", i18n_settings.default_locale)
    ]

    # اختيار اللغة المناسبة
    for source, locale in locales:
        if locale and locale in i18n_settings.supported_locales:
            return {
                "detected_locale": locale,
                "source": source,
                "all_options": dict(locales),
                "message": _("locale_detected", locale)
            }

    # إذا لم يتم العثور على أي لغة مدعومة
    return {
        "detected_locale": i18n_settings.default_locale,
        "source": "default",
        "all_options": dict(locales)
    }

@router.get(
    "/options",
    response_model=language_schemas.LanguageOptionsResponse,
    summary="الحصول على خيارات اللغة المتاحة",
    description="يُرجع قائمة بجميع اللغات المدعومة من قبل النظام.",
)
async def get_language_options(
    current_user: UserInDB = Depends(get_current_user)
) -> Any:
    """
    الحصول على خيارات اللغة المتاحة

    Args:
        current_user: المستخدم الحالي

    Returns:
        قاموس يحتوي على خيارات اللغة
    """
    language_options = consent_manager.get_locale_options()

    return {
        "language_options": language_options,
        "current_locale": translator.current_locale,
        "default_locale": i18n_settings.default_locale,
        "supported_locales": i18n_settings.supported_locales
    }


@router.post(
    "/set",
    response_model=language_schemas.SetLocaleResponse,
    summary="تعيين لغة المستخدم",
    description="يعين ويسجل اللغة المفضلة للمستخدم.",
)
async def set_locale(
    locale_data: language_schemas.SetLocaleRequest,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    تعيين اللغة للمستخدم

    Args:
        locale_data: بيانات اللغة
        current_user: المستخدم الحالي
        db: جلسة قاعدة البيانات

    Returns:
        قاموس يحتوي على نتيجة الإعداد
    """
    locale = locale_data.locale

    # التحقق مما إذا كانت اللغة مدعومة
    if locale not in i18n_settings.supported_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Locale {locale} is not supported"
        )

    # تعيين اللغة
    translator.set_locale(locale)

    # تسجيل اللغة المفضلة للمستخدم
    consent_result = consent_manager.record_consent(
        db=db,
        user_id=current_user.id,
        consent_given=True,
        preferred_locale=locale,
        locale_source="manual",
        consent_data=locale_data.dict()
    )

    return {
        "success": True,
        "message": _("locale_set", locale),
        "current_locale": translator.current_locale,
        "consent_status": consent_result
    }


@router.post(
    "/reload-translations",
    summary="[Admin] إعادة تحميل ملفات الترجمة",
    description="يقوم بإعادة تحميل جميع ملفات الترجمة من القرص. هذه العملية مخصصة للمسؤولين فقط.",
    dependencies=[Depends(PermissionChecker(["translations:reload"]))],
)
async def reload_translations(
    current_user: UserInDB = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    إعادة تحميل ملفات الترجمة (للمسؤولين فقط).
    """
    try:
        translator.load_all_translations()
        return {"success": True, "message": "Translation files reloaded successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload translations: {str(e)}"
        )
