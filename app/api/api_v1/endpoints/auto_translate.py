
# نقاط نهاية API للترجمة التلقائية للمحتوى

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.i18n import translator, i18n_settings
from app.core.translation_loader import translation_loader
from app.core.auto_translator import auto_translator
from app.core.consent import consent_manager
from app.core.geolocation import geolocation_service
from app.models.user import User
from app.schemas.user import UserInDB
from app.core.security import verify_token

router = APIRouter()

@router.post("/content")
async def translate_content(
    content: Dict[str, Any],
    target_language: str,
    source_language: str = None,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    ترجمة محتوى

    Args:
        content: المحتوى المطلوب ترجمته
        target_language: اللغة الهدف
        source_language: اللغة المصدر (اختياري)
        current_user: المستخدم الحالي

    Returns:
        المحتوى المترجم
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

    # ترجمة المحتوى
    translated_content = auto_translator.translate_content(content, target_language, source_language)

    if translated_content is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content translation failed"
        )

    return {
        "original_content": content,
        "translated_content": translated_content,
        "source_language": source_language,
        "target_language": target_language
    }

@router.post("/batch")
async def batch_translate(
    texts: List[str],
    target_language: str,
    source_language: str = None,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    ترجمة دفعة من النصوص

    Args:
        texts: قائمة النصوص المطلوب ترجمتها
        target_language: اللغة الهدف
        source_language: اللغة المصدر (اختياري)
        current_user: المستخدم الحالي

    Returns:
        قائمة النصوص المترجمة
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

    # ترجمة النصوص
    translated_texts = auto_translator.batch_translate(texts, target_language, source_language)

    # التحقق من نجاح الترجمة
    if all(t is None for t in translated_texts):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch translation failed"
        )

    return {
        "original_texts": texts,
        "translated_texts": translated_texts,
        "source_language": source_language,
        "target_language": target_language,
        "success_count": sum(1 for t in translated_texts if t is not None),
        "failure_count": sum(1 for t in translated_texts if t is None)
    }

@router.get("/languages")
async def get_available_translation_languages(
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    الحصول على اللغات المتاحة للترجمة

    Args:
        current_user: المستخدم الحالي

    Returns:
        قائمة اللغات المتاحة
    """
    # الحصول على اللغات المتاحة
    available_languages = auto_translator.get_available_translations({})

    return {
        "languages": available_languages,
        "count": len(available_languages)
    }

@router.post("/suggest")
async def suggest_translation(
    text: str,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    اقتراح ترجمة نص

    Args:
        text: النص المطلوب اقتراح ترجمته
        current_user: المستخدم الحالي

    Returns:
        اقتراحات الترجمة
    """
    # الكشف عن لغة النص
    detected_language = auto_translator.detect_language(text)

    if detected_language is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Language detection failed"
        )

    # الحصول على اللغات المقترحة للترجمة
    suggested_languages = []

    # إضافة اللغات الشائعة
    common_languages = ["en", "es", "fr", "de", "zh", "ar", "ru", "ja", "ko", "pt"]

    for lang in common_languages:
        if lang != detected_language and lang in i18n_settings.supported_locales:
            suggested_languages.append({
                "language": lang,
                "language_name": translation_loader.get_translation(f"language_name.{lang}", lang),
                "language_native_name": translation_loader.get_translation(f"language_native_name.{lang}", lang),
                "confidence": 0.8  # في التطبيق الحقيقي، سيتم حساب الثقة بناءً على عوامل متعددة
            })

    return {
        "text": text,
        "detected_language": detected_language,
        "detected_language_name": translation_loader.get_translation(f"language_name.{detected_language}", detected_language),
        "suggested_languages": suggested_languages
    }

@router.post("/content-type")
async def translate_content_type(
    content_type: str,
    content_id: int,
    target_language: str,
    source_language: str = None,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    ترجمة محتوى بنوع معين

    Args:
        content_type: نوع المحتوى (مثل "article", "exercise", "program")
        content_id: معرف المحتوى
        target_language: اللغة الهدف
        source_language: اللغة المصدر (اختياري)
        current_user: المستخدم الحالي

    Returns:
        المحتوى المترجم
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

    # في التطبيق الحقيقي، سيتم الحصول على المحتوى من قاعدة البيانات
    # هنا سنقوم بإنشاء محتوى وهمي
    content = {
        "id": content_id,
        "type": content_type,
        "title": f"Sample {content_type.title()}",
        "description": f"This is a sample {content_type} for translation.",
        "content": f"This is the content of the sample {content_type}."
    }

    # ترجمة المحتوى
    translated_content = auto_translator.translate_content(content, target_language, source_language)

    if translated_content is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content translation failed"
        )

    return {
        "content_type": content_type,
        "content_id": content_id,
        "original_content": content,
        "translated_content": translated_content,
        "source_language": source_language,
        "target_language": target_language
    }

@router.get("/progress")
async def get_translation_progress(
    content_id: int,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    الحصول على تقدم الترجمة للمحتوى

    Args:
        content_id: معرف المحتوى
        current_user: المستخدم الحالي

    Returns:
        تقدم الترجمة
    """
    # في التطبيق الحقيقي، سيتم الحصول على التقدم من قاعدة البيانات
    # هنا سنقوم بإرجاع بيانات وهمية
    progress = {
        "content_id": content_id,
        "total_languages": len(i18n_settings.supported_locales),
        "translated_languages": 15,
        "translation_percentage": 58.3,
        "languages": [
            {"language": "en", "translated": True},
            {"language": "ar", "translated": True},
            {"language": "fr", "translated": False},
            {"language": "es", "translated": True},
            {"language": "de", "translated": False},
            {"language": "zh", "translated": True},
            {"language": "ja", "translated": False},
            {"language": "ko", "translated": True},
            {"language": "ru", "translated": False},
            {"language": "pt", "translated": True}
        ]
    }

    return progress
