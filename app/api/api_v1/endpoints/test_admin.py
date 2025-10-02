import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import mock_open, MagicMock

from app.main import app
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserInDB
from app.schemas.auth import Role, Permission

client = TestClient(app)

# --- بيانات وهمية للاختبار ---

mock_perm_audit_read = Permission(
    id=1, name="audit:read", description="Read audit logs")
mock_perm_roles_read = Permission(
    id=2, name="roles:read", description="Read roles")

mock_role_admin = Role(
    id=1,
    name="admin",
    description="Admin role",
    permissions=[mock_perm_audit_read, mock_perm_roles_read]
)

mock_role_user = Role(
    id=2,
    name="user",
    description="User role",
    permissions=[]
)

mock_admin_user = UserInDB(
    id=1,
    email="admin@example.com",
    full_name="Admin User",
    is_active=True,
    email_verified=True,
    role=mock_role_admin,
    hashed_password="fake_password",
    created_at="2023-01-01T00:00:00"
)

mock_regular_user = UserInDB(
    id=2,
    email="user@example.com",
    full_name="Regular User",
    is_active=True,
    email_verified=True,
    role=mock_role_user,
    hashed_password="fake_password",
    created_at="2023-01-01T00:00:00"
)

# --- إعدادات الاختبار (Fixtures) ---


@pytest.fixture
def db_session(mocker) -> Session:
    """إنشاء جلسة قاعدة بيانات وهمية."""
    return mocker.MagicMock(spec=Session)


def override_get_db():
    """تجاوز تبعية قاعدة البيانات."""
    yield MagicMock(spec=Session)


def setup_user_dependency(user: UserInDB):
    """إعداد تبعية المستخدم الحالي."""
    def override_get_current_user():
        return user
    app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture(autouse=True)
def setup_default_dependencies():
    """إعداد التبعيات الافتراضية وتنظيفها."""
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides = original_overrides

# --- حالات الاختبار ---


def test_read_audit_logs_success(mocker):
    """
    اختبار قراءة سجلات التدقيق بنجاح من قبل مسؤول.
    """
    setup_user_dependency(mock_admin_user)

    log_content = (
        "2023-10-27 10:00:00,123 - some.module - INFO - Some other log\n"
        "2023-10-27 10:05:15,456 - app.core.security - WARNING - ACCESS DENIED: User 'test@user.com' (ID: 2) with role 'user' from IP 127.0.0.1 tried to access 'POST /api/v1/admin/roles'. Missing permissions: roles:create\n"
        "2023-10-27 10:10:00,789 - app.main - INFO - Request processed\n"
    )

    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data=log_content))

    response = client.get("/api/v1/admin/audit-logs")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_email"] == "test@user.com"
    assert data[0]["path"] == "/api/v1/admin/roles"
    assert data[0]["missing_permissions"] == "roles:create"


def test_read_audit_logs_permission_denied(mocker):
    """
    اختبار منع الوصول لمستخدم عادي يحاول قراءة سجلات التدقيق.
    """
    setup_user_dependency(mock_regular_user)

    response = client.get("/api/v1/admin/audit-logs")

    assert response.status_code == 403
    assert "don't have permission" in response.json()["detail"]


def test_read_audit_logs_no_file(mocker):
    """
    اختبار الحالة التي لا يوجد فيها ملف سجل.
    """
    setup_user_dependency(mock_admin_user)

    mocker.patch("pathlib.Path.exists", return_value=False)

    response = client.get("/api/v1/admin/audit-logs")

    assert response.status_code == 200
    assert response.json() == []


def test_read_audit_logs_empty_or_no_match(mocker):
    """
    اختبار الحالة التي يكون فيها ملف السجل فارغًا أو لا يحتوي على إدخالات مطابقة.
    """
    setup_user_dependency(mock_admin_user)

    log_content = (
        "2023-10-27 10:00:00,123 - app.core.security - INFO - Some other log\n"
        "2023-10-27 10:10:00,789 - app.main - INFO - Request processed\n"
    )

    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data=log_content))

    response = client.get("/api/v1/admin/audit-logs")

    assert response.status_code == 200
    assert response.json() == []
