
# نقاط نهاية API للتعامل مع الترجمات الافتراضية

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.default_translations import default_translations
from app.core.i18n import translator, i18n_settings
from app.core.translation_loader import translation_loader

from app.schemas.user import UserInDB
from app.core.security import verify_token

router = APIRouter()


@router.get("/load")
async def load_default_translations(
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    تحميل الترجمات الافتراضية

    Args:
        current_user: المستخدم الحالي

    Returns:
        نتيجة التحميل
    """
    # تحميل الترجمات الافتراضية
    for lang_code, translations in default_translations.items():
        if lang_code in i18n_settings.supported_locales:
            # استيراد الترجمات
            translation_loader.import_translation(lang_code, translations)

    return {
        "success": True,
        "message": "Default translations loaded successfully",
        "languages_loaded": len(default_translations)
    }


@router.get("/get")
async def get_default_translations(
    lang_code: str,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    الحصول على الترجمات الافتراضية للغة

    Args:
        lang_code: رمز اللغة
        current_user: المستخدم الحالي

    Returns:
        الترجمات الافتراضية
    """
    # التحقق من صحة اللغة
    if lang_code not in i18n_settings.supported_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language {lang_code} is not supported"
        )

    # الحصول على الترجمات الافتراضية
    translations = default_translations.get(lang_code, {})

    return {
        "language": lang_code,
        "translations": translations
    }


@router.get("/languages")
async def get_supported_languages(
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    الحصول على اللغات المدعومة

    Args:
        current_user: المستخدم الحالي

    Returns:
        قائمة اللغات المدعومة
    """
    # الحصول على اللغات المدعومة
    languages = {}

    for lang_code in i18n_settings.supported_locales:
        languages[lang_code] = {
            "name": default_translations.get(lang_code, {}).get("language_name", lang_code),
            "native_name": default_translations.get(lang_code, {}).get("language_native_name", lang_code),
            # اللغات التي تكتب من اليمين لليسار
            "rtl": lang_code in ["ar", "he", "fa", "ur", "ps", "yi"],
            "loaded": lang_code in default_translations
        }

    return {
        "languages": languages,
        "total_languages": len(i18n_settings.supported_locales),
        "loaded_languages": len(default_translations)
    }


@router.post("/update")
async def update_default_translations(
    lang_code: str,
    translations: Dict[str, Any],
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    تحديث الترجمات الافتراضية

    Args:
        lang_code: رمز اللغة
        translations: الترجمات الجديدة
        current_user: المستخدم الحالي

    Returns:
        نتيجة التحديث
    """
    # التحقق من صحة اللغة
    if lang_code not in i18n_settings.supported_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language {lang_code} is not supported"
        )

    # تحديث الترجمات
    default_translations[lang_code] = translations

    # استيراد الترجمات المحدثة
    translation_loader.import_translation(lang_code, translations)

    return {
        "success": True,
        "message": f"Default translations updated successfully for {lang_code}",
        "language": lang_code
    }


@router.get("/status")
async def get_default_translations_status(
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    الحصول على حالة الترجمات الافتراضية

    Args:
        current_user: المستخدم الحالي

    Returns:
        حالة الترجمات الافتراضية
    """
    # الحصول على حالة الترجمات
    status = {}

    for lang_code in i18n_settings.supported_locales:
        status[lang_code] = {
            "loaded": lang_code in default_translations,
            "translation_count": len(default_translations.get(lang_code, {})),
            "language_name": default_translations.get(lang_code, {}).get("language_name", lang_code),
            "language_native_name": default_translations.get(lang_code, {}).get("language_native_name", lang_code)
        }

    return {
        "status": status,
        "total_languages": len(i18n_settings.supported_locales),
        "loaded_languages": len(default_translations),
        "completion_percentage": round((len(default_translations) / len(i18n_settings.supported_locales)) * 100, 2)
    }
) * 100, 2)
    }
