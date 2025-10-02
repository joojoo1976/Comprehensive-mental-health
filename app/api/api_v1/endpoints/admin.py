from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import re
from pathlib import Path
from sqlalchemy.orm import Session

from app import schemas
from app import crud
from app.core.database import get_db
from app.core.security import get_current_user, PermissionChecker, invalidate_user_cache

router = APIRouter()

# --- Permissions Endpoints ---


@router.post(
    "/permissions",
    response_model=schemas.auth.Permission,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker(["permissions:create"]))],
    summary="إنشاء صلاحية جديدة"
)
def create_permission(
    permission_in: schemas.auth.PermissionCreate,
    db: Session = Depends(get_db),
):
    """
    إنشاء صلاحية جديدة في النظام.
    - **name**: اسم الصلاحية (مثال: `users:read`).
    """
    db_permission = crud.crud_auth.get_permission_by_name(
        db, name=permission_in.name)
    if db_permission:
        raise HTTPException(
            status_code=400, detail="Permission already exists.")
    return crud.crud_auth.create_permission(db=db, permission=permission_in)


@router.get(
    "/permissions",
    response_model=List[schemas.auth.Permission],
    dependencies=[Depends(PermissionChecker(["permissions:read"]))],
    summary="قراءة جميع الصلاحيات"
)
def read_permissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    استرجاع قائمة بجميع الصلاحيات المتاحة في النظام.
    """
    permissions = crud.crud_auth.get_permissions(db, skip=skip, limit=limit)
    return permissions

# --- Roles Endpoints ---


@router.post(
    "/roles",
    response_model=schemas.auth.Role,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker(["roles:create"]))],
    summary="إنشاء دور جديد"
)
def create_role(
    role_in: schemas.auth.RoleCreate,
    db: Session = Depends(get_db),
):
    """
    إنشاء دور جديد للمستخدمين.
    """
    db_role = crud.crud_auth.get_role_by_name(db, name=role_in.name)
    if db_role:
        raise HTTPException(status_code=400, detail="Role already exists.")
    return crud.crud_auth.create_role(db=db, role=role_in)


@router.get(
    "/roles",
    response_model=List[schemas.auth.Role],
    dependencies=[Depends(PermissionChecker(["roles:read"]))],
    summary="قراءة جميع الأدوار"
)
def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    استرجاع قائمة بجميع الأدوار مع صلاحياتها.
    """
    roles = crud.crud_auth.get_roles(db, skip=skip, limit=limit)
    return roles


@router.post(
    "/roles/{role_id}/permissions/{permission_id}",
    response_model=schemas.auth.Role,
    dependencies=[Depends(PermissionChecker(["roles:update"]))],
    summary="إضافة صلاحية إلى دور"
)
def add_permission_to_role(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
):
    """
    ربط صلاحية موجودة بدور معين.
    """
    role = crud.crud_auth.get_role(db, role_id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    permission = crud.crud_auth.get_permission(db, permission_id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    updated_role = crud.crud_auth.add_permission_to_role(
        db, role=role, permission=permission)

    return updated_role

# --- Audit Log Endpoint ---


LOG_FILE_PATH = Path("logs/app.log")
AUDIT_LOG_REGEX = re.compile(
    r"^(?P<timestamp>[\d\- :,\.]+) - .*? - WARNING - "
    r"ACCESS DENIED: User '(?P<user_email>.*?)' \(ID: (?P<user_id>\d+)\) "
    r"with role '(?P<role>.*?)' "
    r"from IP (?P<ip_address>[\d\.:a-fA-F]+) tried to access '(?P<method>\w+) (?P<path>.*?)'. "
    r"Missing permissions: (?P<missing_permissions>.*)$"
)


@router.get(
    "/audit-logs",
    response_model=List[schemas.auth.AuditLogEntry],
    dependencies=[Depends(PermissionChecker(["audit:read"]))],
    summary="[Admin] قراءة سجلات التدقيق الأمني"
)
def read_audit_logs(limit: int = 100):
    """
    استرجاع سجلات محاولات الوصول غير المصرح بها من ملف السجل.

    - **limit**: الحد الأقصى لعدد السجلات المراد إرجاعها (الأحدث أولاً).
    """
    if not LOG_FILE_PATH.exists():
        return []

    audit_logs = []
    try:
        # قراءة الملف بشكل عكسي بكفاءة لعرض أحدث السجلات أولاً
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            # استخدام deque لقراءة السطور بكفاءة من النهاية
            from collections import deque
            # نقرأ بحد أقصى (limit * 5) لتجنب قراءة الملف كله إذا كانت سجلات التدقيق نادرة
            # هذا الرقم يمكن تعديله حسب كثافة السجلات المتوقعة
            lines_to_check = deque(f, maxlen=limit * 5)

            # الآن نعكس الـ deque الذي يحتوي على آخر الأسطر فقط
            for line in reversed(lines_to_check):
                if len(audit_logs) >= limit:
                    break  # توقف عند الوصول إلى الحد المطلوب

                if "ACCESS DENIED" in line:
                    match = AUDIT_LOG_REGEX.match(line.strip())
                    if match:
                        log_data = match.groupdict()
                        audit_logs.append(
                            schemas.auth.AuditLogEntry(**log_data))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not read or parse log file: {e}")

    return audit_logs


@router.delete(
    "/roles/{role_id}/permissions/{permission_id}",
    response_model=schemas.auth.Role,
    dependencies=[Depends(PermissionChecker(["roles:update"]))],
    summary="إزالة صلاحية من دور"
)
def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
):
    """
    إزالة صلاحية من دور معين.
    """
    role = crud.crud_auth.get_role(db, role_id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    permission = crud.crud_auth.get_permission(db, permission_id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    updated_role = crud.crud_auth.remove_permission_from_role(
        db, role=role, permission=permission)

    return updated_role
