# مسارات API الإصدار الأول

from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, sessions, content, analytics, language, translations, auto_translate, websocket_translate, default_translations

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["المصادقة"])
api_router.include_router(users.router, prefix="/users", tags=["المستخدمون"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["الجلسات"])
api_router.include_router(content.router, prefix="/content", tags=["المحتوى"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["التحليلات"])
api_router.include_router(language.router, prefix="/language", tags=["اللغة"])
api_router.include_router(translations.router, prefix="/translations", tags=["الترجمات"])
api_router.include_router(auto_translate.router, prefix="/auto-translate", tags=["الترجمة التلقائية"])
api_router.include_router(websocket_translate.router, prefix="/websocket", tags=["WebSocket"])
api_router.include_router(default_translations.router, prefix="/default-translations", tags=["الترجمات الافتراضية"])
