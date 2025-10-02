# نقاط نهاية المصادقة

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from app import crud, schemas
from app.core import security
from app.core.config import settings
from app.api import deps
from app.utils import send_verification_email, send_password_reset_email

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    المصادقة باستخدام اسم المستخدم وكلمة المرور
    """
    user = crud.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="بيانات الاعتماد غير صحيحة",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud.is_user_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="الحساب غير نشط",
        )

    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.User.from_orm(user)
    }


@router.post("/register", response_model=schemas.User)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate
) -> Any:
    """
    إنشاء حساب مستخدم جديد
    """
    user = crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="هذا البريد الإلكتروني مسجل بالفعل",
        )

    user = crud.create_user(db=db, user_in=user_in)

    # إرسال بريد إلكتروني للتحقق
    send_verification_email(email=user_in.email, token=user.verification_token)

    return user


@router.post("/verify-email")
def verify_email(
    token: str,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    التحقق من البريد الإلكتروني
    """
    user = crud.verify_user_email(db, token=token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز التحقق غير صالح أو منتهي الصلاحية",
        )

    return {"msg": "تم التحقق من البريد الإلكتروني بنجاح"}


@router.post("/password-recovery", response_model=schemas.Msg)
def password_recovery(
    email: str,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    إرسال رابط لإعادة تعيين كلمة المرور
    """
    user = crud.get_user_by_email(db, email=email)
    if user:
        password_reset_token = crud.generate_password_reset_token(user)
        send_password_reset_email(
            email=email, token=password_reset_token
        )
    return {"msg": "إذا كان البريد الإلكتروني مسجلاً، سيتم إرسال رابط لإعادة تعيين كلمة المرور"}


@router.post("/reset-password", response_model=schemas.Msg)
def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    إعادة تعيين كلمة المرور باستخدام الرمز
    """
    hashed_password = security.get_password_hash(new_password)
    reset_success = crud.reset_password(
        db, token=token, new_password=hashed_password)
    if not reset_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فشل إعادة تعيين كلمة المرور",
        )
    return {"msg": "تمت إعادة تعيين كلمة المرور بنجاح"}
