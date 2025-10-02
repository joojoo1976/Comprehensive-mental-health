# نقاط نهاية التحليلات

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app import crud, models, schemas
from app.api import deps
from app.core.security import get_current_user

router = APIRouter()


@router.get("/wellness-score", response_model=schemas.WellnessScore)
def get_wellness_score(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
    date: Optional[datetime] = None,
) -> Any:
    """
    الحصول على درجة العافية للمستخدم
    """
    score = crud.get_wellness_score(db, user_id=current_user.id, date=date)
    return score


@router.get("/mood-tracker", response_model=List[schemas.MoodEntry])
def get_mood_tracker(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على سجل المزاج للمستخدم
    """
    mood_entries = crud.get_mood_entries(
        db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )
    return mood_entries


@router.post("/mood-tracker", response_model=schemas.MoodEntry)
def create_mood_entry(
    *,
    db: Session = Depends(deps.get_db),
    mood_in: schemas.MoodEntryCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    إنشاء مدخل مزاج جديد
    """
    mood_entry = crud.create_mood_entry(
        db, user_id=current_user.id, mood_in=mood_in)
    return mood_entry


@router.get("/sleep-tracker", response_model=List[schemas.SleepEntry])
def get_sleep_tracker(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على سجل النوم للمستخدم
    """
    sleep_entries = crud.get_sleep_entries(
        db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )
    return sleep_entries


@router.post("/sleep-tracker", response_model=schemas.SleepEntry)
def create_sleep_entry(
    *,
    db: Session = Depends(deps.get_db),
    sleep_in: schemas.SleepEntryCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    إنشاء مدخل نوم جديد
    """
    sleep_entry = crud.create_sleep_entry(
        db, user_id=current_user.id, sleep_in=sleep_in)
    return sleep_entry


@router.get("/activity-tracker", response_model=List[schemas.ActivityEntry])
def get_activity_tracker(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على سجل النشاط للمستخدم
    """
    activity_entries = crud.get_activity_entries(
        db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )
    return activity_entries


@router.post("/activity-tracker", response_model=schemas.ActivityEntry)
def create_activity_entry(
    *,
    db: Session = Depends(deps.get_db),
    activity_in: schemas.ActivityEntryCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    إنشاء مدخل نشاط جديد
    """
    activity_entry = crud.create_activity_entry(
        db, user_id=current_user.id, activity_in=activity_in)
    return activity_entry


@router.get("/insights", response_model=List[schemas.Insight])
def get_insights(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على رؤى المستخدم بناءً على بياناته
    """
    insights = crud.get_user_insights(db, user_id=current_user.id)
    return insights


@router.get("/recommendations", response_model=List[schemas.Recommendation])
def get_recommendations(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على توصيات مخصصة للمستخدم
    """
    recommendations = crud.get_user_recommendations(
        db, user_id=current_user.id)
    return recommendations


@router.get("/progress", response_model=schemas.ProgressReport)
def get_progress_report(
    period: str = Query(
        "week", description="فترة التقرير: day, week, month, year"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على تقرير تقدم للمستخدم
    """
    progress_report = crud.get_progress_report(
        db, user_id=current_user.id, period=period)
    return progress_report


@router.get("/digital-biomarkers-analysis", response_model=schemas.DigitalBiomarkersAnalysis)
def get_digital_biomarkers_analysis(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على تحليل المؤشرات الحيوية الرقمية للمستخدم
    """
    analysis = crud.get_digital_biomarkers_analysis(
        db, user_id=current_user.id)
    return analysis


@router.post("/digital-biomarkers-upload")
def upload_digital_biomarkers(
    *,
    db: Session = Depends(deps.get_db),
    biomarkers_data: schemas.DigitalBiomarkersData,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    رفع المؤشرات الحيوية الرقمية
    """
    biomarkers = crud.upload_digital_biomarkers(
        db, user_id=current_user.id, biomarkers_data=biomarkers_data
    )
    return biomarkers


@router.get("/global-mental-health-insights", response_model=schemas.GlobalMentalHealthInsights)
def get_global_mental_health_insights(
    region: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    الحصول على رؤى عالمية في الصحة النفسية
    """
    insights = crud.get_global_mental_health_insights(db, region=region)
    return insights
