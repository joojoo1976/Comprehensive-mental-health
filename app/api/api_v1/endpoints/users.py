# نقاط نهاية المستخدمين

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.security import get_current_user, get_password_hash, invalidate_user_cache

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على معلومات المستخدم الحالي
    """
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    تحديث معلومات المستخدم الحالي
    """
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)

    return user

@router.get("/profile", response_model=schemas.UserProfile)
def read_user_profile(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على ملف المستخدم الشخصي
    """
    profile = crud.get_user_profile(db, user_id=current_user.id)
    return profile

@router.put("/profile", response_model=schemas.UserProfile)
def update_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_in: schemas.UserProfileUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    تحديث ملف المستخدم الشخصي
    """
    profile = crud.update_user_profile(db, user_id=current_user.id, profile_in=profile_in)
    return profile

@router.get("/preferences", response_model=schemas.UserPreferences)
def read_user_preferences(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على تفضيلات المستخدم
    """
    preferences = crud.get_user_preferences(db, user_id=current_user.id)
    return preferences

@router.put("/preferences", response_model=schemas.UserPreferences)
def update_user_preferences(
    *,
    db: Session = Depends(deps.get_db),
    preferences_in: schemas.UserPreferencesUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    تحديث تفضيلات المستخدم
    """
    preferences = crud.update_user_preferences(db, user_id=current_user.id, preferences_in=preferences_in)
    return preferences

@router.get("/digital-biomarkers", response_model=List[schemas.DigitalBiomarker])
def read_user_digital_biomarkers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على مؤشرات المستخدم الحيوية الرقمية
    """
    biomarkers = crud.get_user_digital_biomarkers(db, user_id=current_user.id, skip=skip, limit=limit)
    return biomarkers

@router.get("/life-inflection-points", response_model=List[schemas.LifeInflectionPoint])
def read_user_life_inflection_points(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على نقاط الانعطاف الحياتية للمستخدم
    """
    inflection_points = crud.get_user_life_inflection_points(db, user_id=current_user.id, skip=skip, limit=limit)
    return inflection_points

@router.post("/life-inflection-points", response_model=schemas.LifeInflectionPoint)
def create_life_inflection_point(
    *,
    db: Session = Depends(deps.get_db),
    point_in: schemas.LifeInflectionPointCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    إنشاء نقطة انعطاف حياتية جديدة
    """
    point = crud.create_life_inflection_point(db, user_id=current_user.id, point_in=point_in)
    return point

@router.get("/wellness-suggestions", response_model=List[schemas.WellnessSuggestion])
def get_user_wellness_suggestions(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على اقتراحات العافة للمستخدم بناءً على حالته
    """
    suggestions = crud.get_user_wellness_suggestions(db, user_id=current_user.id)
    return suggestions
