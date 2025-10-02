# التبعيات المشتركة للAPI

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import verify_token
from app import crud, schemas

# إعداد OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_db() -> Generator:
    """
    الحصول على جلسة قاعدة البيانات
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> schemas.User:
    """
    الحصول على المستخدم الحالي من خلال التوكن
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="لا يمكن التحقق من الهوية",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = verify_token(token, credentials_exception)
        user_id = token_data.get("sub")
        if user_id is None:
            raise credentials_exception
        user = crud.get_user(db, user_id=int(user_id))
        if user is None:
            raise credentials_exception
        return user
    except Exception:
        raise credentials_exception


def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user),
) -> schemas.User:
    """
    الحصول على المستخدم النشط الحالي
    """
    if not crud.is_user_active(current_user):
        raise HTTPException(status_code=400, detail="الحساب غير نشط")
    return current_user


def get_current_admin_user(
    current_user: schemas.User = Depends(get_current_user),
) -> schemas.User:
    """
    الحصول على المستخدم المسؤول الحالي
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مصرح به",
        )
    return current_user
