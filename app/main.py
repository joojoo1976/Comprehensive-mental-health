# التطبيق الرئيسي لمنصة الصحة النفسية الشاملة

from app.core.locale_middleware import (
    LocaleMiddleware,
    LocaleConsentMiddleware,
    LocaleRedirectMiddleware,
)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import time
import uvicorn
import logging
from app.config import settings
from app.api.api_v1.api import api_router
from app.core import initial_data
from app.core.logging import setup_logging
from app.core.database import create_tables

# إعداد التسجيل
setup_logging()
logger = logging.getLogger(__name__)

# إنشاء تطبيق FastAPI
app = FastAPI(
    title=settings.app_name,
    openapi_url=f"{settings.api_prefix}/openapi.json"
)


@app.on_event("startup")
def on_startup():
    """
    يتم تنفيذ هذه الدالة عند بدء تشغيل التطبيق.
    """
    initial_data.create_initial_data()
    # Development fallback: create tables if enabled
    if settings.auto_create_db:
        create_tables()

# Middleware لتسجيل مدة معالجة الطلب


@app.middleware("http")
async def log_request_processing_time(request: Request, call_next):
    """
    يسجل هذا الـ middleware المدة التي يستغرقها كل طلب API للمعالجة.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # إضافة رأس مخصص للاستجابة يحتوي على مدة المعالجة
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    logger.info(
        'Request: "%s %s" processed in %.4f secs - Status: %s',
        request.method,
        request.url.path,
        process_time,
        response.status_code,
    )
    return response

# إضافة middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في الإنتاج، يجب تحديد Origins بدقة
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# إضافة middleware للغة

app.add_middleware(LocaleMiddleware)
app.add_middleware(LocaleConsentMiddleware)
app.add_middleware(LocaleRedirectMiddleware)

# إضافة المسارات الثابتة
import os
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# إضافة قوالب Jinja2
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "templates")
templates = Jinja2Templates(directory=templates_dir)

# تضمين المسارات الرئيسية


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# تضمين مسارات API
app.include_router(api_router, prefix=settings.api_prefix)

# معالجة الاستثناءات


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"حدث خطأ غير متوقع: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "حدث خطأ داخلي في الخادم"},
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="192.168.1.7",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
