# نقاط نهاية الجلسات

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.security import get_current_user

router = APIRouter()


@router.get("/", response_model=List[schemas.Session])
def read_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على قائمة جلسات المستخدم
    """
    sessions = crud.get_user_sessions(
        db, user_id=current_user.id, skip=skip, limit=limit)
    return sessions


@router.get("/{session_id}", response_model=schemas.Session)
def read_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على جلسة معينة
    """
    session = crud.get_session(db, session_id=session_id)
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مصرح لك بالوصول إلى هذه الجلسة"
        )
    return session


@router.post("/", response_model=schemas.Session)
def create_session(
    *,
    db: Session = Depends(deps.get_db),
    session_in: schemas.SessionCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    إنشاء جلسة جديدة
    """
    session = crud.create_session(
        db, user_id=current_user.id, session_in=session_in)
    return session


@router.post("/{session_id}/join", response_model=schemas.Session)
def join_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الانضمام إلى جلسة موجودة
    """
    session = crud.join_session(
        db, session_id=session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الجلسة غير موجودة أو غير متاحة"
        )
    return session


@router.post("/{session_id}/leave")
def leave_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    المغادرة من جلسة
    """
    success = crud.leave_session(
        db, session_id=session_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لم تكن في هذه الجلسة أو لم تتمكن من المغادرة"
        )
    return {"msg": "تمت المغادرة من الجلسة بنجاح"}


@router.post("/{session_id}/feedback", response_model=schemas.SessionFeedback)
def create_session_feedback(
    *,
    db: Session = Depends(deps.get_db),
    feedback_in: schemas.SessionFeedbackCreate,
    session_id: int,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    إضافة تغذية راجعة لجلسة
    """
    session = crud.get_session(db, session_id=session_id)
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مصرح لك بإضافة تغذية راجعة لهذه الجلسة"
        )

    feedback = crud.create_session_feedback(
        db, session_id=session_id, feedback_in=feedback_in)
    return feedback


@router.get("/{session_id}/recording")
def get_session_recording(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على تسجيل جلسة
    """
    session = crud.get_session(db, session_id=session_id)
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مصرح لك بالوصول إلى تسجيل هذه الجلسة"
        )

    # هنا يتم إرجاع رابط التسجيل أو التسجيل نفسه
    return {"recording_url": f"/api/v1/sessions/{session_id}/recording.mp4"}


@router.get("/{session_id}/analysis")
def get_session_analysis(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على تحليل الجلسة باستخدام الذكاء الاصطناعي
    """
    session = crud.get_session(db, session_id=session_id)
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مصرح لك بالوصول إلى تحليل هذه الجلسة"
        )

    # هنا يتم إرجاع تحليل الجلسة الذي تم إنشاؤه بواسطة الذكاء الاصطناعي
    return {
        "session_id": session_id,
        "emotional_analysis": {
            "dominant_emotion": "القلق",
            "emotion_trend": "تحسن",
            "key_moments": [
                {"time": "00:05:23", "emotion": "حزن",
                    "description": "ذكر المستخدم بتجربة سابقة"},
                {"time": "00:12:45", "emotion": "توتر",
                    "description": "مناقشة موضوع محفوف بالمخاطر"}
            ]
        },
        "voice_analysis": {
            "tone": "متذبذب",
            "pace": "سريع في البداية، بطيئ في النهاية",
            "energy": "مرتفع ثم منخفض"
        },
        "summary": "تمت مناقشة تحديات المستخدم في العمل وكيفية التكيف مع الضغوط اليومية.",
        "recommendations": [
            "ممارسة تمارين التنفس العميق يومياً",
            "تطبيق تقنيات إدارة التوتر في المواقف الصعبة",
            "الحفاظ على جدول نوم منتظم"
        ]
    }
