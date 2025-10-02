# أدوات مساعدة للتطبيق

import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from typing import Optional
from fastapi import HTTPException, status
from jinja2 import Environment, FileSystemLoader
import os

# إعداد بيئة Jinja2 للقوالب
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "templates")
env = Environment(loader=FileSystemLoader(template_dir))


def generate_verification_token(length: int = 32) -> str:
    """
    إنشاء رمز تحقق عشوائي
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_verification_email(email: str, token: str) -> None:
    """
    إرسال بريد إلكتروني للتحقق
    """
    # في التطبيق الفعلي، سيتم استخدام إعدادات SMTP الفعلية
    from app.core.config import settings

    # إنشاء رابط التحقق
    verification_url = f"{settings.app_url}/verify?token={token}"

    # إنشاء محتوى البريد الإلكتروني
    subject = "تفعيل حسابك في منصة الصحة النفسية"

    # تحميل قالب البريد الإلكتروني
    template = env.get_template("verification_email.html")
    html_content = template.render(
        user_name=email,
        verification_url=verification_url,
        app_name=settings.app_name
    )

    # إرسال البريد الإلكتروني
    _send_email(
        to_email=email,
        subject=subject,
        html_content=html_content
    )


def send_password_reset_email(email: str, token: str) -> None:
    """
    إرسال بريد إلكتروني لإعادة تعيين كلمة المرور
    """
    # في التطبيق الفعلي، سيتم استخدام إعدادات SMTP الفعلية
    from app.core.config import settings

    # إنشاء رابط إعادة تعيين كلمة المرور
    reset_url = f"{settings.app_url}/reset-password?token={token}"

    # إنشاء محتوى البريد الإلكتروني
    subject = "إعادة تعيين كلمة المرور في منصة الصحة النفسية"

    # تحميل قالب البريد الإلكتروني
    template = env.get_template("password_reset_email.html")
    html_content = template.render(
        user_name=email,
        reset_url=reset_url,
        app_name=settings.app_name
    )

    # إرسال البريد الإلكتروني
    _send_email(
        to_email=email,
        subject=subject,
        html_content=html_content
    )


def _send_email(to_email: str, subject: str, html_content: str) -> None:
    """
    إرسال بريد إلكتروني باستخدام إعدادات SMTP
    """
    from app.core.config import settings

    # إنشاء رسالة البريد الإلكتروني
    msg = MIMEMultipart()
    msg['From'] = settings.smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject

    # إضافة المحتوى
    msg.attach(MIMEText(html_content, 'html'))

    # الاتصال بخادم SMTP وإرسال البريد
    try:
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
    except Exception as e:
        # في الإنتاج، يجب تسجيل الخطأ بدلاً من تجاهله
        print(f"فشل إرسال البريد الإلكتروني: {e}")
