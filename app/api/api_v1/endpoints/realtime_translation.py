
# نقاط نهاية API للترجمة التلقائية في الوقت الفعلي

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.i18n import translator, i18n_settings, _
from app.core.auto_translator import auto_translator
from app.core.consent import consent_manager
from app.core.geolocation import geolocation_service

from app.schemas.user import UserInDB
from app.core.security import verify_token
from fastapi import WebSocket, WebSocketDisconnect

router = APIRouter()


class RealtimeTranslationManager:
    """مدير الترجمة في الوقت الفعلي"""

    def __init__(self):
        """تهيئة المدير"""
        self.active_connections: Dict[int, WebSocket] = {}
        self.user_languages: Dict[int, str] = {}

    async def connect(self, websocket: WebSocket, user_id: int, db: Session):
        """اتصال عميل جديد"""
        await websocket.accept()
        self.active_connections[user_id] = websocket

        # الحصول على لغة المستخدم
        consent_status = consent_manager.get_consent_status(db, user_id)
        if consent_status["consent_given"] and consent_status["preferred_locale"]:
            self.user_languages[user_id] = consent_status["preferred_locale"]
        else:
            self.user_languages[user_id] = i18n_settings.default_locale

    def disconnect(self, user_id: int):
        """قطع اتصال عميل"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_languages:
            del self.user_languages[user_id]

    async def translate_text(self, user_id: int, text: str) -> Optional[str]:
        """ترجمة نص"""
        if user_id not in self.user_languages:
            return None

        # الحصول على لغة المستخدم
        target_language = self.user_languages[user_id]

        # ترجمة النص
        return auto_translator.translate_text(text, target_language)

    async def detect_language(self, text: str) -> Optional[str]:
        """كشف لغة النص"""
        return auto_translator.detect_language(text)

    async def broadcast_translation(self, message: str):
        """بث رسالة لجميع العملاء"""
        for connection in self.active_connections.values():
            await connection.send_text(message)


# إنشاء مثيل من المدير
realtime_translation_manager = RealtimeTranslationManager()


@router.websocket("/translate")
async def websocket_translate(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """نقطة نهاية WebSocket للترجمة التلقائية"""
    # التحقق من المصادقة
    user_id = None
    try:
        user_id = verify_token(token)
    except:
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # الاتصال بالعميل
    await realtime_translation_manager.connect(websocket, user_id, db)

    try:
        while True:
            # استلام رسالة من العميل
            data = await websocket.receive_text()

            try:
                # تحليل البيانات
                import json
                request = json.loads(data)

                # التحقق من صحة الطلب
                if "text" not in request:
                    await websocket.send_text(json.dumps({
                        "error": "Invalid request format"
                    }))
                    continue

                # استخراج البيانات
                text = request["text"]

                # ترجمة النص
                translated_text = await realtime_translation_manager.translate_text(user_id, text)

                # إرسال النتيجة
                if translated_text:
                    await websocket.send_text(json.dumps({
                        "original_text": text,
                        "translated_text": translated_text,
                        "target_language": realtime_translation_manager.user_languages.get(user_id),
                        "status": "success"
                    }))
                else:
                    await websocket.send_text(json.dumps({
                        "error": "Translation failed",
                        "status": "error"
                    }))

            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "error": "Invalid JSON format"
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "error": str(e),
                    "status": "error"
                }))

    except WebSocketDisconnect:
        realtime_translation_manager.disconnect(user_id)


@router.websocket("/detect-language")
async def websocket_detect_language(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """نقطة نهاية WebSocket لكشف اللغة"""
    # التحقق من المصادقة
    user_id = None
    try:
        user_id = verify_token(token)
    except:
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # الاتصال بالعميل
    await realtime_translation_manager.connect(websocket, user_id, db)

    try:
        while True:
            # استلام رسالة من العميل
            data = await websocket.receive_text()

            try:
                # تحليل البيانات
                import json
                request = json.loads(data)

                # التحقق من صحة الطلب
                if "text" not in request:
                    await websocket.send_text(json.dumps({
                        "error": "Invalid request format"
                    }))
                    continue

                # استخراج البيانات
                text = request["text"]

                # كشف اللغة
                detected_language = await realtime_translation_manager.detect_language(text)

                # إرسال النتيجة
                if detected_language:
                    await websocket.send_text(json.dumps({
                        "text": text,
                        "detected_language": detected_language,
                        "language_name": translator.get_translation(f"language_name.{detected_language}", detected_language),
                        "status": "success"
                    }))
                else:
                    await websocket.send_text(json.dumps({
                        "error": "Language detection failed",
                        "status": "error"
                    }))

            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "error": "Invalid JSON format"
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "error": str(e),
                    "status": "error"
                }))

    except WebSocketDisconnect:
        realtime_translation_manager.disconnect(user_id)


@router.get("/user-language")
async def get_user_language(
    user_id: int,
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    الحصول على لغة المستخدم

    Args:
        user_id: معرف المستخدم
        current_user: المستخدم الحالي

    Returns:
        لغة المستخدم
    """
    # التحقق من صحة المستخدم
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

    # الحصول على لغة المستخدم
    if user_id in realtime_translation_manager.user_languages:
        return {
            "user_id": user_id,
            "language": realtime_translation_manager.user_languages[user_id],
            "language_name": translator.get_translation(
                f"language_name.{realtime_translation_manager.user_languages[user_id]}",
                realtime_translation_manager.user_languages[user_id]
            )
        }
    else:
        return {
            "user_id": user_id,
            "language": i18n_settings.default_locale,
            "language_name": translator.get_translation(
                f"language_name.{i18n_settings.default_locale}",
                i18n_settings.default_locale
            )
        }


@router.post("/set-user-language")
async def set_user_language(
    user_id: int,
    language: str,
    current_user: UserInDB = Depends(verify_token),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    تعيين لغة المستخدم

    Args:
        user_id: معرف المستخدم
        language: اللغة الجديدة
        current_user: المستخدم الحالي

    Returns:
        نتيجة التعيين
    """
    # التحقق من صحة المستخدم
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

    # التحقق من صحة اللغة
    if language not in i18n_settings.supported_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language {language} is not supported"
        )

    # تعيين اللغة
    realtime_translation_manager.user_languages[user_id] = language

    # تسجيل الموافقة
    consent_manager.record_consent(
        db=db,
        user_id=user_id,
        consent_given=True,
        preferred_locale=language,
        locale_source="manual",
        consent_data={"language": language}
    )

    return {
        "success": True,
        "message": f"Language set to {language}",
        "user_id": user_id,
        "language": language
    }


@router.get("/active-users")
async def get_active_users(
    current_user: UserInDB = Depends(verify_token)
) -> Dict[str, Any]:
    """
    الحصول على المستخدمين النشطين

    Args:
        current_user: المستخدم الحالي

    Returns:
        قائمة المستخدمين النشطين
    """
    # الحصول على المستخدمين النشطين
    active_users = []

    for user_id in realtime_translation_manager.active_connections.keys():
        active_users.append({
            "user_id": user_id,
            "language": realtime_translation_manager.user_languages.get(user_id, i18n_settings.default_locale)
        })

    return {
        "active_users": active_users,
        "count": len(active_users)
    }
": len(active_users)
    }
