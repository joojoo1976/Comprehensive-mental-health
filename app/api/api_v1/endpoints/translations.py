
# نقاط نهاية API لإدارة الترجمات

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.i18n import translator, i18n_settings
from app.core.translation_loader import translation_loader
from app.core.consent import consent_manager
from app.core.auto_translator import auto_translator
from app.core.geolocation import geolocation_service

from app.schemas.user import UserInDB
from app.core.security import verify_token

router = APIRouter()


@router.get("/list")
async def list_translations(
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    الحصول على قائمة اللغات المتاحة

    Args:
        current_user: المستخدم الحالي

    Returns:
        قائمة باللغات المتاحة
    """
    # الحصول على اللغات المدعومة
    languages = {}

    for lang_code in i18n_settings.supported_locales:
        languages[lang_code] = {
            "name": translation_loader.get_translation(f"language_name.{lang_code}", lang_code),
            "native_name": translation_loader.get_translation(f"language_native_name.{lang_code}", lang_code),
            # اللغات التي تكتب من اليمين لليسار
            "rtl": lang_code in ["ar", "he", "fa", "ur", "ps", "yi"],
            "status": translation_loader.get_translation_stats(lang_code)
        }

    return {
        "languages": languages,
        "default_language": i18n_settings.default_locale,
        "current_language": translator.current_locale
    }


@router.get("/stats")
async def get_translation_stats(
    lang_code: str,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    الحصول على إحصائيات الترجمة للغة

    Args:
        lang_code: رمز اللغة
        current_user: المستخدم الحالي

    Returns:
        إحصائيات الترجمة
    """
    # التحقق من صحة اللغة
    if lang_code not in i18n_settings.supported_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language {lang_code} is not supported"
        )

    # الحصول على إحصائيات الترجمة
    stats = translation_loader.get_translation_stats(lang_code)

    return {
        "language": lang_code,
        "stats": stats
    }


@router.get("/keys")
async def get_translation_keys(
    lang_code: str,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    الحصول على مفاتيح الترجمة للغة

    Args:
        lang_code: رمز اللغة
        current_user: المستخدم الحالي

    Returns:
        قائمة مفاتيح الترجمة
    """
    # التحقق من صحة اللغة
    if lang_code not in i18n_settings.supported_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language {lang_code} is not supported"
        )

    # الحصول على مفاتيح الترجمة
    keys = translation_loader.get_translation_keys(lang_code)

    return {
        "language": lang_code,
        "keys": keys
    }


@router.get("/translate")
async def translate_text(
    text: str,
    target_language: str,
    source_language: str = None,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    ترجمة نص

    Args:
        text: النص المطلوب ترجمته
        target_language: اللغة الهدف
        source_language: اللغة المصدر (اختياري)
        current_user: المستخدم الحالي

    Returns:
        النص المترجم
    """
    # التحقق من صحة اللغات
    if target_language not in i18n_settings.supported_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target language {target_language} is not supported"
        )

    if source_language and source_language not in i18n_settings.supported_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source language {source_language} is not supported"
        )

    # ترجمة النص
    translated_text = auto_translator.translate_text(
        text, target_language, source_language)

    if translated_text is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation failed"
        )

    return {
        "original_text": text,
        "translated_text": translated_text,
        "source_language": source_language,
        "target_language": target_language
    }


@router.get("/detect")
async def detect_language(
    text: str,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    الكشف عن لغة النص

    Args:
        text: النص المطلوب الكشف عن لغته
        current_user: المستخدم الحالي

    Returns:
        اللغة المكتشفة
    """
    # الكشف عن اللغة
    detected_language = auto_translator.detect_language(text)

    if detected_language is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Language detection failed"
        )

    return {
        "text": text,
        "detected_language": detected_language,
        "language_name": translation_loader.get_translation(f"language_name.{detected_language}", detected_language)
    }


@router.post("/import")
async def import_translations(
    lang_code: str,
    translation_data: Dict[str, Any],
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    استيراد ترجمات

    Args:
        lang_code: رمز اللغة
        translation_data: بيانات الترجمة
        current_user: المستخدم الحالي

    Returns:
        نتيجة الاستيراد
    """
    # التحقق من صحة اللغة
    if lang_code not in i18n_settings.supported_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language {lang_code} is not supported"
        )

    # استيراد الترجمات
    success = translation_loader.import_translation(
        lang_code, translation_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Import failed"
        )

    return {
        "success": True,
        "message": f"Translations imported successfully for {lang_code}",
        "language": lang_code
    }


@router.get("/export")
async def export_translations(
    lang_code: str,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    تصدير ترجمات

    Args:
        lang_code: رمز اللغة
        current_user: المستخدم الحالي

    Returns:
        بيانات الترجمة
    """
    # التحقق من صحة اللغة
    if lang_code not in i18n_settings.supported_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language {lang_code} is not supported"
        )

    # تصدير الترجمات
    translation_data = translation_loader.export_translation(lang_code)

    if translation_data is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export failed"
        )

    return {
        "language": lang_code,
        "translations": translation_data
    }


@router.post("/set")
async def set_translation(
    key: str,
    value: str,
    lang_code: str,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    تعيين ترجمة

    Args:
        key: مفتاح الترجمة
        value: قيمة الترجمة
        lang_code: رمز اللغة
        current_user: المستخدم الحالي

    Returns:
        نتيجة التعيين
    """
    # التحقق من صحة اللغة
    if lang_code not in i18n_settings.supported_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language {lang_code} is not supported"
        )

    # تعيين الترجمة
    success = translation_loader.set_translation(key, value, lang_code)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation set failed"
        )

    return {
        "success": True,
        "message": f"Translation set successfully for {lang_code}",
        "key": key,
        "value": value,
        "language": lang_code
    }


@router.get("/status")
async def get_translation_status(
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    الحصول على حالة الترجمة

    Args:
        current_user: المستخدم الحالي

    Returns:
        حالة الترجمة
    """
    # الحصول على حالة الترجمة
    status = translation_loader.get_translation_status()

    return {
        "status": status,
        "total_languages": len(i18n_settings.supported_locales),
        "default_language": i18n_settings.default_locale
    }
cale
    }
}
