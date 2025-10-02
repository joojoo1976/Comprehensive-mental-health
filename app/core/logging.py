
# إعداد التسجيل (Logging)

import logging
import logging.handlers
import os
from pathlib import Path
from app.config import settings


def setup_logging():
    """إعداد نظام التسجيل للتطبيق"""
    # إنشاء مجلد السجلات إذا لم يكن موجودًا
    log_dir = Path("logs")
    if not log_dir.exists():
        os.makedirs(log_dir)

    # تحديد مستوى التسجيل
    log_level = logging.DEBUG if settings.debug else logging.INFO

    # إنشاء منسق السجلات
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # إنشاء مسجل الجذر
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # إضافة معالج السجل للملف
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    root_logger.addHandler(file_handler)

    # إضافة معالج السجل للوحدة الطرفية
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # تسجيل رسالة تأكيد الإعداد
    logging.info("تم إعداد نظام التسجيل بنجاح")
