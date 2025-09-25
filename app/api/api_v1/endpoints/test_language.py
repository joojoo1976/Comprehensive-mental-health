import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.main import app  # افترض أن هذا هو ملف التطبيق الرئيسي
from app.core.database import get_db
from app.core.security import verify_token
from app.schemas.user import UserInDB

# إنشاء عميل اختبار
client = TestClient(app)

# بيانات مستخدم وهمية للاختبار
mock_user = UserInDB(
    id=1,
    email="test@example.com",
    full_name="Test User",
    is_active=True,
    email_verified=True,
    role="user",
    hashed_password="fakehashedpassword",
    created_at="2023-01-01T00:00:00"
)


@pytest.fixture
def db_session(mocker) -> Session:
    """
    إنشاء جلسة قاعدة بيانات وهمية.
    """
    return mocker.MagicMock(spec=Session)


@pytest.fixture(autouse=True)
def override_dependencies(db_session: Session):
    """
    تجاوز التبعيات (get_db, verify_token) لجميع الاختبارات في هذا الملف.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_verify_token():
        return mock_user.id

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_token] = override_verify_token
    yield
    # تنظيف التجاوزات بعد انتهاء الاختبارات
    app.dependency_overrides = {}


def test_get_language_consent(mocker):
    """
    اختبار نقطة النهاية للحصول على حالة موافقة اللغة.
    """
    # محاكاة الدوال الخارجية
    mocker.patch("app.core.consent.consent_manager.get_consent_status", return_value={
        "consent_given": False, "preferred_locale": None, "locale_source": None
    })
    mocker.patch("app.core.consent.consent_manager.get_locale_options", return_value={
        "en": {"name": "English", "native_name": "English", "rtl": False}
    })
    mocker.patch("app.core.geolocation.geolocation_service.get_client_ip", return_value="8.8.8.8")
    mocker.patch("app.core.geolocation.geolocation_service.get_locale_by_ip", return_value="en")
    mocker.patch("app.core.i18n.translator.get_user_locale_from_browser", return_value="fr")

    # إجراء الطلب
    response = client.get("/api/v1/language/consent")

    # التحقق من النتائج
    assert response.status_code == 200
    data = response.json()
    assert data["consent_given"] is False
    assert data["suggested_locale"] == "en"
    assert "language_options" in data
    assert data["language_options"]["en"]["name"] == "English"


def test_give_language_consent(mocker, db_session):
    """
    اختبار نقطة النهاية لتسجيل موافقة اللغة.
    """
    # إعداد المحاكاة
    mock_consent_result = {
        "consent_given": True,
        "preferred_locale": "ar",
        "locale_source": "manual",
        "consent_data": {"consent_given": True, "preferred_locale": "ar"}
    }
    mocker.patch("app.core.consent.consent_manager.record_consent", return_value=mock_consent_result)
    mock_set_locale = mocker.patch("app.core.i18n.translator.set_locale")

    # بيانات الطلب
    request_data = {"consent_given": True, "preferred_locale": "ar"}

    # إجراء الطلب
    response = client.post("/api/v1/language/consent", json=request_data)

    # التحقق من النتائج
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["consent_status"]["consent_given"] is True
    assert data["consent_status"]["preferred_locale"] == "ar"
    
    # التحقق من أن دالة تعيين اللغة قد تم استدعاؤها
    mock_set_locale.assert_called_once_with("ar")


def test_detect_locale_with_user_preference(mocker, db_session):
    """
    اختبار الكشف عن اللغة عندما يكون لدى المستخدم تفضيل محفوظ.
    """
    # إعداد المحاكاة
    mocker.patch("app.core.consent.consent_manager.get_consent_status", return_value={
        "consent_given": True, "preferred_locale": "fr", "locale_source": "manual"
    })

    # إجراء الطلب
    response = client.get("/api/v1/language/detect")

    # التحقق من النتائج
    assert response.status_code == 200
    data = response.json()
    assert data["detected_locale"] == "fr"
    assert data["source"] == "manual"


def test_detect_locale_with_browser_preference(mocker, db_session):
    """
    اختبار الكشف عن اللغة بناءً على لغة المتصفح.
    """
    # إعداد المحاكاة
    mocker.patch("app.core.consent.consent_manager.get_consent_status", return_value={
        "consent_given": False, "preferred_locale": None
    })
    mocker.patch("app.core.i18n.translator.get_user_locale_from_browser", return_value="de")
    mocker.patch("app.core.geolocation.geolocation_service.get_locale_by_ip", return_value="en")

    # إجراء الطلب
    response = client.get("/api/v1/language/detect")

    # التحقق من النتائج
    assert response.status_code == 200
    data = response.json()
    assert data["detected_locale"] == "de"
    assert data["source"] == "browser"


def test_set_locale_success(mocker, db_session):
    """
    اختبار تعيين لغة المستخدم بنجاح.
    """
    # إعداد المحاكاة
    mock_consent_result = {
        "consent_given": True, "preferred_locale": "es", "locale_source": "manual"
    }
    mocker.patch("app.core.consent.consent_manager.record_consent", return_value=mock_consent_result)
    mock_set_locale = mocker.patch("app.core.i18n.translator.set_locale")

    # إجراء الطلب
    response = client.post("/api/v1/language/set", json={"locale": "es"})

    # التحقق من النتائج
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["current_locale"] == "es"
    assert data["consent_status"]["preferred_locale"] == "es"
    mock_set_locale.assert_called_once_with("es")


def test_set_locale_unsupported(mocker, db_session):
    """
    اختبار تعيين لغة غير مدعومة.
    """
    # إجراء الطلب
    response = client.post("/api/v1/language/set", json={"locale": "xx"})

    # التحقق من النتائج
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]


def test_get_language_options(mocker):
    """
    اختبار نقطة النهاية للحصول على خيارات اللغة.
    """
    # إعداد المحاكاة
    mocker.patch("app.core.consent.consent_manager.get_locale_options", return_value={
        "en": {"name": "English", "native_name": "English", "rtl": False},
        "ar": {"name": "Arabic", "native_name": "العربية", "rtl": True}
    })

    # إجراء الطلب
    response = client.get("/api/v1/language/options")

    # التحقق من النتائج
    assert response.status_code == 200
    data = response.json()
    assert "language_options" in data
    assert "en" in data["language_options"]
    assert "ar" in data["language_options"]
    assert "supported_locales" in data