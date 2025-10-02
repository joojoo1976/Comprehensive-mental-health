# عمليات CRUD للمستخدمين

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import user as models
from app import schemas


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    الحصول على مستخدم حسب الـ ID
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    الحصول على مستخدم حسب البريد الإلكتروني
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_multi_by_role(db: Session, role_id: int, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    الحصول على عدة مستخدمين حسب الدور
    """
    return db.query(models.User).filter(models.User.role_id == role_id).offset(skip).limit(limit).all()


def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[models.User]:
    """
    الحصول على قائمة بال مستخدمين مع دعم البحث والتصفية
    """
    query = db.query(models.User)

    # البحث في البريد الإلكتروني أو الاسم الكامل
    if search:
        query = query.filter(
            or_(
                models.User.email.contains(search),
                models.User.full_name.contains(search)
            )
        )

    # التصفية حسب الدور
    if role:
        query = query.filter(models.User.role == role)

    # التصفية حسب حالة النشاط
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)

    return query.offset(skip).limit(limit).all()


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    """
    إنشاء مستخدم جديد
    """
    db_user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, 
    db_user: models.User, 
    user_in: schemas.UserUpdate
) -> models.User:
    """
    تحديث بيانات مستخدم
    """
    user_data = user_in.dict(exclude_unset=True)
    for field, value in user_data.items():
        setattr(db_user, field, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    حذف مستخدم
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


def is_user_active(user: models.User) -> bool:
    """
    التحقق من أن المستخدم نشط
    """
    return user.is_active


def activate_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    تفعيل حساب المستخدم
    """
    db_user = get_user(db, user_id)
    if db_user:
        db_user.is_active = True
        db.commit()
        db.refresh(db_user)
    return db_user


def deactivate_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    تعطيل حساب المستخدم
    """
    db_user = get_user(db, user_id)
    if db_user:
        db_user.is_active = False
        db.commit()
        db.refresh(db_user)
    return db_user


def change_user_role(db: Session, user_id: int, new_role: str) -> Optional[models.User]:
    """
    تغيير دور المستخدم
    """
    db_user = get_user(db, user_id)
    if db_user:
        db_user.role = new_role
        db.commit()
        db.refresh(db_user)
    return db_user
