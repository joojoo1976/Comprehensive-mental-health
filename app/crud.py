# عمليات CRUD الأساسية

from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import user
from app import schemas
from app.core.security import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> Optional[user.User]:
    """
    الحصول على مستخدم حسب الـ ID
    """
    return db.query(user.User).filter(user.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[user.User]:
    """
    الحصول على مستخدم حسب البريد الإلكتروني
    """
    return db.query(user.User).filter(user.User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[user.User]:
    """
    التحقق من مصداقية المستخدم
    """
    user_obj = get_user_by_email(db, email)
    if not user_obj:
        return None
    if not verify_password(password, user_obj.hashed_password):
        return None
    return user_obj


def is_user_active(user: user.User) -> bool:
    """
    التحقق من أن المستخدم نشط
    """
    return user.is_active


def create_user(db: Session, user_in: schemas.UserCreate) -> user.User:
    """
    إنشاء مستخدم جديد
    """
    hashed_password = get_password_hash(user_in.password)
    db_user = user.User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def verify_user_email(db: Session, token: str) -> Optional[user.User]:
    """
    التحقق من بريد المستخدم الإلكتروني
    """
    user_obj = db.query(user.User).filter(user.User.verification_token == token).first()
    if user_obj:
        user_obj.email_verified = True
        user_obj.verification_token = None
        db.commit()
        db.refresh(user_obj)
    return user_obj


def generate_password_reset_token(user: user.User) -> str:
    """
    إنشاء رمز لإعادة تعيين كلمة المرور
    """
    # في التطبيق الفعلي، سيتم استخدام آلية آمنة لتوليد الرموز
    return f"reset_token_{user.id}_{user.email}"


def reset_password(db: Session, token: str, new_password: str) -> bool:
    """
    إعادة تعيين كلمة المرور باستخدام الرمز
    """
    # في التطبيق الفعلي، سيتم التحقق من الرمز بشكل صحيح
    user_obj = db.query(user.User).filter(user.User.verification_token == token).first()
    if user_obj:
        user_obj.hashed_password = get_password_hash(new_password)
        user_obj.verification_token = None
        db.commit()
        db.refresh(user_obj)
        return True
    return False
