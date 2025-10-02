from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class LanguageOptionDetail(BaseModel):
    """
    تفاصيل خيار لغة واحد.
    """
    name: str
    native_name: str
    rtl: bool


class ConsentStatus(BaseModel):
    """
    نموذج يمثل حالة الموافقة.
    """
    consent_given: bool
    preferred_locale: Optional[str] = None
    locale_source: Optional[str] = None
    consent_data: Optional[Dict[str, Any]] = None


class LanguageConsentStatusResponse(ConsentStatus):
    """
    نموذج الاستجابة لنقطة نهاية الحصول على حالة موافقة اللغة.
    """
    language_options: Dict[str, LanguageOptionDetail]
    suggested_locale: str
    current_locale: str
    message: str
    description: str


class LanguageConsentRecordResponse(BaseModel):
    """
    نموذج الاستجابة لنقطة نهاية تسجيل موافقة اللغة.
    """
    success: bool
    message: str
    consent_status: ConsentStatus


class LocaleDetectionResponse(BaseModel):
    """
    نموذج الاستجابة لنقطة نهاية الكشف عن اللغة.
    """
    detected_locale: str
    source: str
    all_options: Dict[str, Optional[str]]
    message: Optional[str] = None


class LanguageOptionsResponse(BaseModel):
    """
    نموذج الاستجابة لنقطة نهاية الحصول على خيارات اللغة.
    """
    language_options: Dict[str, LanguageOptionDetail]
    current_locale: str
    default_locale: str
    supported_locales: List[str]


class SetLocaleRequest(BaseModel):
    """
    نموذج الطلب لنقطة نهاية تعيين اللغة.
    """
    locale: str = Field(...,
                        description="رمز اللغة المراد تعيينه (e.g., 'ar', 'en').")


class SetLocaleResponse(BaseModel):
    """
    نموذج الاستجابة لنقطة نهاية تعيين اللغة.
    """
    success: bool
    message: str
    current_locale: str
    consent_status: ConsentStatus
