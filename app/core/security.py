
# إعدادات الأمان

from datetime import datetime, timedelta
import logging
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app import crud  # استيراد crud للوصول إلى قاعدة البيانات
# استيراد خدمة ذاكرة التخزين المؤقت الجديدة
from app.core.cache import cache_service
from app.core.database import get_db
from app.config import settings
from app.schemas.user import UserInDB
from app.models import user

logger = logging.getLogger(__name__)

# إعداد سياسة تشفير كلمات المرور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# دالة لتشفير كلمة المرور


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# دالة للتحقق من كلمة المرور


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# دالة لإنشاء رمز JWT


def create_access_token(subject: int, expires_delta: Optional[timedelta] = None):
    to_encode = {"sub": str(subject)}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

# دالة للتحقق من رمز JWT


def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")), db: Session = Depends(get_db)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key,
                             algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # الخطوة 1: التحقق من ذاكرة التخزين المؤقت أولاً
        cached_user = cache_service.get_user(int(user_id))
        if cached_user:
            return cached_user

        # استخدام joinedload لتحميل الأدوار والصلاحيات المرتبطة في استعلام واحد
        user = db.query(crud.User).options(
            joinedload(crud.User.role).joinedload(crud.Role.permissions)
        ).filter(crud.User.id == int(user_id)).first()

        if user is None:
            raise credentials_exception

        user_data = UserInDB.from_orm(user)

        # الخطوة 2: تخزين بيانات المستخدم في ذاكرة التخزين المؤقت
        cache_service.set_user(user_data)

        return user_data
    except JWTError:
        raise credentials_exception


def verify_token(token: str) -> Optional[int]:
    """
    يفك تشفير رمز JWT ويعيد معرّف المستخدم.
    يعيد None إذا كان الرمز غير صالح أو منتهي الصلاحية.
    """
    try:
        payload = jwt.decode(token, settings.secret_key,
                             algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except (JWTError, ValueError):
        # إذا فشل فك التشفير أو تحويل المعرّف إلى رقم
        return None


def invalidate_user_cache(user_id: int):
    """إبطال صلاحية ذاكرة التخزين المؤقت لمستخدم معين."""
    cache_service.invalidate_user(user_id)


class PermissionChecker:
    """
    تبعية للتحقق من صلاحيات المستخدم.
    تتحقق مما إذا كان لدى المستخدم جميع الصلاحيات المطلوبة.
    """

    def __init__(self, required_permissions: List[str]):
        self.required_permissions = set(required_permissions)

    def __call__(self, request: Request, current_user: UserInDB = Depends(get_current_user)):
        """
        يتم استدعاء هذه الدالة عند استخدام التبعية.
        """
        # استخراج صلاحيات المستخدم من دوره
        # نفترض أن `current_user` يحتوي الآن على `role` و `role.permissions` بفضل `joinedload`
        user_permissions = {
            p.name for p in current_user.role.permissions} if current_user.role and current_user.role.permissions else set()

        # التحقق مما إذا كان المستخدم يمتلك جميع الصلاحيات المطلوبة
        if not self.required_permissions.issubset(user_permissions):
            # تسجيل محاولة الوصول غير المصرح بها لأغراض التدقيق الأمني
            missing_permissions = self.required_permissions - user_permissions
            logger.warning(
                f"ACCESS DENIED: User '{current_user.email}' (ID: {current_user.id}) "
                f"with role '{current_user.role.name if current_user.role else 'None'}' "
                f"from IP {request.client.host} tried to access '{request.method} {request.url.path}'. "
                f"Missing permissions: {', '.join(missing_permissions)}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource."
            )

# ملاحظة: يجب التأكد من أن نموذج المستخدم `User` في `models/user.py` مرتبط بنموذج `Role`
# وأن نماذج `Role` و `Permission` وجدول الربط بينهما موجودة في قاعدة البيانات.
