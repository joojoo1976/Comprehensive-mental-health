# عمليات CRUD للمصادقة

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import auth as models
from app import schemas


def get_permission(db: Session, permission_id: int) -> Optional[models.Permission]:
    """
    الحصول على إذن حسب الـ ID
    """
    return db.query(models.Permission).filter(models.Permission.id == permission_id).first()


def get_permission_by_name(db: Session, name: str) -> Optional[models.Permission]:
    """
    الحصول على إذن حسب الاسم
    """
    return db.query(models.Permission).filter(models.Permission.name == name).first()


def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[models.Permission]:
    """
    الحصول على قائمة بالأذونات
    """
    return db.query(models.Permission).offset(skip).limit(limit).all()


def create_permission(db: Session, permission: schemas.PermissionCreate) -> models.Permission:
    """
    إنشاء إذن جديد
    """
    db_permission = models.Permission(**permission.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def get_role(db: Session, role_id: int) -> Optional[models.Role]:
    """
    الحصول على دور حسب الـ ID
    """
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_role_by_name(db: Session, name: str) -> Optional[models.Role]:
    """
    الحصول على دور حسب الاسم
    """
    return db.query(models.Role).filter(models.Role.name == name).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[models.Role]:
    """
    الحصول على قائمة بالأدوار
    """
    return db.query(models.Role).offset(skip).limit(limit).all()


def create_role(db: Session, role: schemas.RoleCreate) -> models.Role:
    """
    إنشاء دور جديد
    """
    db_role = models.Role(name=role.name, description=role.description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(db: Session, db_role: models.Role, role_in: schemas.RoleUpdate) -> models.Role:
    """
    تحديث دور
    """
    role_data = role_in.dict(exclude_unset=True)
    for field, value in role_data.items():
        setattr(db_role, field, value)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def add_permission_to_role(db: Session, role: models.Role, permission: models.Permission) -> models.Role:
    """
    إضافة إذن لدور
    """
    if permission not in role.permissions:
        role.permissions.append(permission)
        db.commit()
        db.refresh(role)
    return role


def remove_permission_from_role(db: Session, role: models.Role, permission: models.Permission) -> models.Role:
    """
    إزالة إذن من دور
    """
    if permission in role.permissions:
        role.permissions.remove(permission)
        db.commit()
        db.refresh(role)
    return role


def create_audit_log(
    db: Session, 
    user_id: int, 
    action: str, 
    resource_type: str, 
    resource_id: str = None,
    ip_address: str = None,
    user_agent: str = None,
    details: str = None
) -> models.AuditLog:
    """
    إنشاء سجل تدقيق
    """
    db_log = models.AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_audit_logs(
    db: Session, 
    user_id: int = None, 
    skip: int = 0, 
    limit: int = 100
) -> List[models.AuditLog]:
    """
    الحصول على سجلات التدقيق
    """
    query = db.query(models.AuditLog)
    if user_id:
        query = query.filter(models.AuditLog.user_id == user_id)
    return query.order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
