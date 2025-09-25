
# نقاط نهاية WebSocket للترجمة التلقائية في الوقت الفعلي

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.i18n import translator, i18n_settings
from app.core.auto_translator import auto_translator
from app.core.consent import consent_manager
from app.core.geolocation import geolocation_service
from app.models.user import User as UserModel
from app.schemas.user import UserInDB
from app.core.security import get_current_user, verify_token

router = APIRouter()

class ConnectionManager:
    """مدير اتصالات WebSocket"""

    def __init__(self):
        """تهيئة المدير"""
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """اتصال عميل جديد"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        """قطع اتصال عميل"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        """إرسال رسالة شخصية للمستخدم"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)

    async def broadcast(self, message: str):
        """بث رسالة لجميع العملاء"""
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                await connection.send_text(message)

# إنشاء مثيل من مدير الاتصالات
manager = ConnectionManager()

@router.websocket("/translate")
async def websocket_translate(websocket: WebSocket, current_user: UserInDB = Depends(get_current_user)):
    """نقطة نهاية WebSocket للترجمة التلقائية"""
    if not current_user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        return
    await manager.connect(websocket, current_user.id)

    try:
        while True:
            # استلام رسالة من العميل
            data = await websocket.receive_text()

            try:
                # تحليل البيانات
                import json
                request = json.loads(data)

                # التحقق من صحة الطلب
                if "text" not in request or "target_language" not in request:
                    await websocket.send_text(json.dumps({
                        "error": "Invalid request format"
                    }))
                    continue

                # استخراج البيانات
                text = request["text"]
                target_language = request["target_language"]
                source_language = request.get("source_language")

                # التحقق من صحة لغة الهدف
                if target_language not in i18n_settings.supported_locales:
                    await websocket.send_text(json.dumps({
                        "error": f"Target language {target_language} is not supported"
                    }))
                    continue

                # التحقق من صحة لغة المصدر إذا تم توفيرها
                if source_language and (source_language not in i18n_settings.supported_locales):
                    await websocket.send_text(json.dumps({
                        "error": f"Source language {source_language} is not supported"
                    }))
                    continue

                # ترجمة النص
                translated_text = auto_translator.translate_text(text, target_language, source_language)

                # إرسال النتيجة
                if translated_text:
                    await websocket.send_text(json.dumps({
                        "original_text": text,
                        "translated_text": translated_text,
                        "source_language": source_language,
                        "target_language": target_language,
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
        manager.disconnect(websocket, current_user.id)

@router.websocket("/detect-language")
async def websocket_detect_language(websocket: WebSocket, token: str):
    """نقطة نهاية WebSocket لكشف اللغة"""
    # التحقق من المصادقة
    user_id = None
    try:
        user_id = verify_token(token)
    except:
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # الاتصال بالعميل
    await manager.connect(websocket, user_id)

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
                detected_language = auto_translator.detect_language(text)

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
        manager.disconnect(websocket, user_id)
