# نقاط نهاية المحتوى

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.security import get_current_user

router = APIRouter()


@router.get("/categories", response_model=List[schemas.ContentCategory])
def read_content_categories(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على قائمة فئات المحتوى
    """
    categories = crud.get_content_categories(db)
    return categories


@router.get("/articles", response_model=List[schemas.Article])
def read_articles(
    category_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على قائمة المقالات
    """
    articles = crud.get_articles(
        db, category_id=category_id, skip=skip, limit=limit)
    return articles


@router.get("/articles/{article_id}", response_model=schemas.Article)
def read_article(
    article_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على مقال معين
    """
    article = crud.get_article(db, article_id=article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المقال غير موجود"
        )
    return article


@router.post("/articles/{article_id}/bookmark")
def bookmark_article(
    article_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    إضافة المقال إلى المفضلة
    """
    success = crud.bookmark_article(
        db, article_id=article_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فشل إضافة المقال إلى المفضلة"
        )
    return {"msg": "تمت إضافة المقال إلى المفضلة بنجاح"}


@router.delete("/articles/{article_id}/bookmark")
def remove_bookmark_article(
    article_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    إزالة المقال من المفضلة
    """
    success = crud.remove_bookmark_article(
        db, article_id=article_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فشل إزالة المقال من المفضلة"
        )
    return {"msg": "تمت إزالة المقال من المفضلة بنجاح"}


@router.get("/meditations", response_model=List[schemas.Meditation])
def read_meditations(
    category_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على قائمة جلسات التأمل
    """
    meditations = crud.get_meditations(
        db, category_id=category_id, skip=skip, limit=limit)
    return meditations


@router.get("/meditations/{meditation_id}", response_model=schemas.Meditation)
def read_meditation(
    meditation_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على جلسة تأمل معينة
    """
    meditation = crud.get_meditation(db, meditation_id=meditation_id)
    if not meditation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="جلسة التأمل غير موجودة"
        )
    return meditation


@router.get("/exercises", response_model=List[schemas.Exercise])
def read_exercises(
    category_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على قائمة التمارين
    """
    exercises = crud.get_exercises(
        db, category_id=category_id, skip=skip, limit=limit)
    return exercises


@router.get("/exercises/{exercise_id}", response_model=schemas.Exercise)
def read_exercise(
    exercise_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على تمرين معين
    """
    exercise = crud.get_exercise(db, exercise_id=exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="التمرين غير موجود"
        )
    return exercise


@router.post("/exercises/{exercise_id}/complete")
def complete_exercise(
    exercise_id: int,
    completion_data: schemas.ExerciseCompletion,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    إكمال تمرين
    """
    completion = crud.complete_exercise(
        db, exercise_id=exercise_id, user_id=current_user.id, completion_data=completion_data
    )
    if not completion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فشل تسجيل إكمال التمرين"
        )
    return {"msg": "تم تسجيل إكمال التمرين بنجاح"}


@router.get("/programs", response_model=List[schemas.Program])
def read_programs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على قائمة البرامج
    """
    programs = crud.get_programs(db, skip=skip, limit=limit)
    return programs


@router.get("/programs/{program_id}", response_model=schemas.Program)
def read_program(
    program_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على برنامج معين
    """
    program = crud.get_program(db, program_id=program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="البرنامج غير موجود"
        )
    return program


@router.post("/programs/{program_id}/enroll")
def enroll_program(
    program_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    التسجيل في برنامج
    """
    enrollment = crud.enroll_program(
        db, program_id=program_id, user_id=current_user.id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فشل التسجيل في البرنامج"
        )
    return {"msg": "تم التسجيل في البرنامج بنجاح"}


@router.get("/groups", response_model=List[schemas.SupportGroup])
def read_support_groups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على قائمات المجموعات الدعم
    """
    groups = crud.get_support_groups(db, skip=skip, limit=limit)
    return groups


@router.get("/groups/{group_id}", response_model=schemas.SupportGroup)
def read_support_group(
    group_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على مجموعة دعم معينة
    """
    group = crud.get_support_group(db, group_id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المجموعة غير موجودة"
        )
    return group


@router.post("/groups/{group_id}/join")
def join_support_group(
    group_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الانضمام إلى مجموعة دعم
    """
    membership = crud.join_support_group(
        db, group_id=group_id, user_id=current_user.id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فشل الانضمام إلى المجموعة"
        )
    return {"msg": "تم الانضمام إلى المجموعة بنجاح"}


@router.post("/groups/{group_id}/leave")
def leave_support_group(
    group_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    المغادرة من مجموعة دعم
    """
    success = crud.leave_support_group(
        db, group_id=group_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فشل المغادرة من المجموعة"
        )
    return {"msg": "تمت المغادرة من المجموعة بنجاح"}
