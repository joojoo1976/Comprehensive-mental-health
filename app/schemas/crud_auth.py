from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import user as models
from app.schemas import auth as schemas

# --- Permission CRUD ---


def get_permission(db: Session, permission_id: int) -> Optional[models.Permission]:
    return db.query(models.Permission).filter(models.Permission.id == permission_id).first()


def get_permission_by_name(db: Session, name: str) -> Optional[models.Permission]:
    return db.query(models.Permission).filter(models.Permission.name == name).first()


def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[models.Permission]:
    return db.query(models.Permission).offset(skip).limit(limit).all()


def create_permission(db: Session, permission: schemas.PermissionCreate) -> models.Permission:
    db_permission = models.Permission(**permission.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

# --- Role CRUD ---


def get_role(db: Session, role_id: int) -> Optional[models.Role]:
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_role_by_name(db: Session, name: str) -> Optional[models.Role]:
    return db.query(models.Role).filter(models.Role.name == name).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[models.Role]:
    return db.query(models.Role).offset(skip).limit(limit).all()


def create_role(db: Session, role: schemas.RoleCreate) -> models.Role:
    db_role = models.Role(name=role.name, description=role.description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(db: Session, db_role: models.Role, role_in: schemas.RoleUpdate) -> models.Role:
    role_data = role_in.dict(exclude_unset=True)
    for field, value in role_data.items():
        setattr(db_role, field, value)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def add_permission_to_role(db: Session, role: models.Role, permission: models.Permission) -> models.Role:
    if permission not in role.permissions:
        role.permissions.append(permission)
        db.commit()
        db.refresh(role)
    return role


def remove_permission_from_role(db: Session, role: models.Role, permission: models.Permission) -> models.Role:
    if permission in role.permissions:
        role.permissions.remove(permission)
        db.commit()
        db.refresh(role)
    return role
