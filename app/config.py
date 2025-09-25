# إعدادات التطبيق

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # إعدادات التطبيق الأساسية
    app_name: str = "منصة الصحة النفسية الشاملة"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # إعدادات قاعدة البيانات
    database_url: str = "postgresql://user:password@localhost/mental_health_db"

    # إعدادات Redis
    redis_url: str = "redis://localhost:6379"

    # إعدادات المصادقة
    secret_key: str = "your-super-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # إعدادات المستخدم المسؤول الأول
    first_superuser_email: str = "admin@example.com"
    first_superuser_password: str = "changethis"

    # إعدانات الذكاء الاصطناعي
    openai_api_key: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"

    # إعدانات WebRTC
    webrtc_server_url: str = "https://webrtc.example.com"

    # إعدانات البريد الإلكتروني
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

    # إعدانات الملفات
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"
        case_sensitive = False

# إنشاء كائن الإعدادات
settings = Settings()
