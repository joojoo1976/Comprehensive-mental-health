import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app import crud, schemas
from app.config import settings
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


def create_initial_data():
    """
    إنشاء البيانات الأولية: المستخدم المسؤول، الأدوار، والصلاحيات.
    """
    # استخدام SessionLocal لضمان إدارة الجلسة بشكل صحيح
    with SessionLocal() as db:
        try:
            # استخدام معاملة واحدة لجميع العمليات لضمان التناسق
            with db.begin():
                # قائمة الصلاحيات الأساسية اللازمة لإدارة النظام
                permissions_to_create = [
                    schemas.auth.PermissionCreate(
                        name="permissions:create", description="إنشاء صلاحيات جديدة"),
                    schemas.auth.PermissionCreate(
                        name="permissions:read", description="قراءة الصلاحيات"),
                    schemas.auth.PermissionCreate(
                        name="roles:create", description="إنشاء أدوار جديدة"),
                    schemas.auth.PermissionCreate(
                        name="roles:read", description="قراءة الأدوار"),
                    schemas.auth.PermissionCreate(
                        name="roles:update", description="تحديث الأدوار (إضافة/إزالة صلاحيات)"),
                    schemas.auth.PermissionCreate(
                        name="translations:reload", description="إعادة تحميل ملفات الترجمة"),
                    schemas.auth.PermissionCreate(
                        name="audit:read", description="قراءة سجلات التدقيق الأمني"),
                ]

                created_permissions = []
                for permission_in in permissions_to_create:
                    permission = crud.crud_auth.get_permission_by_name(
                        db, name=permission_in.name)
                    if not permission:
                        permission = crud.crud_auth.create_permission(
                            db, permission=permission_in)
                        logger.info(f"Permission '{permission.name}' created.")
                    created_permissions.append(permission)

                # إنشاء دور المسؤول
                admin_role = crud.crud_auth.get_role_by_name(db, name="admin")
                if not admin_role:
                    role_in = schemas.auth.RoleCreate(
                        name="admin", description="دور المسؤول الأعلى")
                    admin_role = crud.crud_auth.create_role(db, role=role_in)
                    logger.info(f"Role '{admin_role.name}' created.")
                    # إضافة جميع الصلاحيات إلى دور المسؤول
                    for p in created_permissions:
                        crud.crud_auth.add_permission_to_role(
                            db, role=admin_role, permission=p)
                    logger.info(
                        f"All base permissions assigned to role '{admin_role.name}'.")

                # التأكد من وجود دور المسؤول قبل إنشاء المستخدم
                if not admin_role:
                    logger.error(
                        "Admin role not found or created. Cannot create superuser.")
                    return

                # إنشاء المستخدم المسؤول
                superuser = crud.user.get_by_email(
                    db, email=settings.first_superuser_email)
                if not superuser:
                    user_in = schemas.user.UserCreate(
                        email=settings.first_superuser_email,
                        password=settings.first_superuser_password,
                        full_name="Super Admin",
                        role_id=admin_role.id  # تمرير معرّف الدور مباشرة
                    )
                    superuser = crud.user.create(db, user_in=user_in)
                    logger.info(
                        f"Superuser '{superuser.email}' created with role 'admin'.")

        except IntegrityError as e:
            logger.warning(
                f"A database integrity error occurred, likely because data already exists: {e}")
        except Exception as e:
            logger.error(
                f"An error occurred during initial data creation: {e}", exc_info=True)
            db.rollback()  # التراجع عن المعاملة في حالة حدوث أي خطأ آخر

        logger.info("Initial data check/creation process finished.")
