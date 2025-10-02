# إعدادات التطبيق

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # إعدادات التطبيق الأساسية
    app_name: str = os.getenv("APP_NAME", "منصة الصحة النفسية الشاملة")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")

    # إعدادات قاعدة البيانات
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/mental_health_db")

    # إعدادات Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # إعدادات المصادقة
    secret_key: str = os.getenv("SECRET_KEY", os.urandom(32).hex())
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # إعدادات المستخدم المسؤول الأول
    first_superuser_email: str = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@example.com")
    first_superuser_password: str = os.getenv("FIRST_SUPERUSER_PASSWORD", None)

    # إعدادات الذكاء الاصطناعي
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    model_name: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    # إعدادات WebRTC
    webrtc_server_url: str = os.getenv("WEBRTC_SERVER_URL", "https://webrtc.example.com")

    # إعدادات البريد الإلكتروني
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")

    # إعدادات الملفات
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    # Development helper: when True, the app will auto-create DB
    # tables on startup
    auto_create_db: bool = os.getenv("AUTO_CREATE_DB", "True").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = False


# إنشاء كائن الإعدادات
settings = Settings()
