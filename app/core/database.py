
# إعدادات قاعدة البيانات

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.core.events import setup_cache_invalidation_listeners

# إنشاء محرك قاعدة البيانات
engine = create_engine(settings.database_url)

# إنشاء جلسة قاعدة البيانات
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# إنشاء Base لنماذج SQLAlchemy
Base = declarative_base()

# تبعية للوصول إلى جلسة قاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# إعداد مستمعي الأحداث لإبطال ذاكرة التخزين المؤقت
setup_cache_invalidation_listeners(SessionLocal)
