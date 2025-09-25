
# نظام تحديد الموقع الجغرافي

import logging
import ipaddress
import requests
from cachetools import TTLCache
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from app.core.i18n import translator

logger = logging.getLogger(__name__)

class GeolocationService:
    """خدمة تحديد الموقع الجغرافي بناءً على عنوان IP"""

    # مهلة زمنية للطلبات الخارجية بالثواني
    REQUEST_TIMEOUT = 5

    # قائمة بمقدمي خدمات تحديد الموقع الجغرافي
    PROVIDERS = [
        {
            "name": "ipinfo.io",
            "url": "https://ipinfo.io/{ip_address}/json",
            # دالة لتحويل استجابة الواجهة البرمجية إلى تنسيق موحد
            "parser": lambda data: {
                "country": data.get("country"),
                "timezone": data.get("timezone"),
            }
        },
        {
            "name": "ip-api.com",
            "url": "http://ip-api.com/json/{ip_address}",
            "parser": lambda data: {
                "country": data.get("countryCode"), # لاحظ أن اسم الحقل مختلف
                "timezone": data.get("timezone"),
            } if data.get("status") == "success" else None
        }
    ]

    def __init__(self):
        """تهيئة خدمة تحديد الموقع الجغرافي"""
        # استخدام ذاكرة تخزين مؤقت بحجم أقصى 1024 عنصرًا
        # ومدة صلاحية 24 ساعة (86400 ثانية) لكل عنصر.
        # سيتم حذف أقدم العناصر تلقائيًا عند امتلاء الذاكرة
        # أو عند انتهاء صلاحيتها.
        self.cache: TTLCache = TTLCache(maxsize=1024, ttl=86400)

    def get_location_by_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        الحصول على معلومات الموقع الجغرافي بناءً على عنوان IP

        Args:
            ip_address: عنوان IP

        Returns:
            قاموس يحتوي على معلومات الموقع الجغرافي
        """
        # التحقق مما إذا كان عنوان IP صالحًا وعامًا
        try:
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private or ip.is_loopback or ip.is_reserved:
                logger.debug(f"Skipping geolocation for private/reserved IP: {ip_address}")
                return None
        except ValueError:
            logger.warning(f"Invalid IP address for geolocation: {ip_address}")
            return None

        # التحقق من ذاكرة التخزين المؤقت
        if ip_address in self.cache:
            return self.cache[ip_address]

        # المرور على مقدمي الخدمات ومحاولة الحصول على البيانات
        for provider in self.PROVIDERS:
            try:
                url = provider["url"].format(ip_address=ip_address)
                response = requests.get(url, timeout=self.REQUEST_TIMEOUT)
                response.raise_for_status()  # يثير استثناءً لأكواد الحالة 4xx/5xx

                raw_data = response.json()
                # تحليل البيانات باستخدام الدالة المخصصة للمزود
                parsed_data = provider["parser"](raw_data)

                if parsed_data and parsed_data.get("country"):
                    logger.debug(f"Geolocation data for {ip_address} retrieved from {provider['name']}")
                    # تخزين النتائج الموحدة في ذاكرة التخزين المؤقت
                    self.cache[ip_address] = parsed_data
                    return parsed_data

            except requests.exceptions.RequestException as e:
                # في حالة حدوث خطأ في الشبكة أو خطأ HTTP، انتقل إلى المزود التالي
                logger.warning(f"Geolocation provider {provider['name']} failed for IP {ip_address}: {e}")
                continue
            except (ValueError, TypeError) as e: # JSONDecodeError or parsing error
                logger.warning(f"Failed to parse response from {provider['name']} for IP {ip_address}: {e}")
                continue

        logger.error(f"All geolocation providers failed for IP {ip_address}")
        return None

    def get_timezone_by_ip(self, ip_address: str) -> str:
        """
        الحصول على المنطقة الزمنية بناءً على عنوان IP

        Args:
            ip_address: عنوان IP

        Returns:
            المنطقة الزمنية
        """
        location = self.get_location_by_ip(ip_address)
        if location and "timezone" in location:
            return location["timezone"]
        return "UTC"  # قيمة افتراضية آمنة

    def get_locale_by_ip(self, ip_address: str) -> str:
        """
        الحصول على اللغة المناسبة بناءً على عنوان IP

        Args:
            ip_address: عنوان IP

        Returns:
            رمز اللغة
        """
        location = self.get_location_by_ip(ip_address)
        if location and "country" in location:
            country_code = location["country"]
            # الحصول على اللغة بناءً على رمز الدولة
            return translator.get_locale_by_region(country_code)
        
        return translator.current_locale # العودة إلى اللغة الحالية أو الافتراضية

    def get_client_ip(self, request: Request) -> str:
        """
        الحصول على عنوان IP العميل

        Args:
            request: كائن الطلب

        Returns:
            عنوان IP العميل
        """
        # الحصول على عنوان IP من الطلب
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # في حالة وجود X-Forwarded-For، استخدم أول عنوان IP
            ip = x_forwarded_for.split(",")[0]
        else:
            # خلاف ذلك، استخدم عنوان IP المباشر
            ip = request.client.host

        # التحقق مما إذا كان عنوان IP صالحاً
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            # في حالة عنوان IP غير صالح، استخدم عنوان IP الافتراضي
            ip = "127.0.0.1"

        return ip

# إنشاء مثيل من خدمة تحديد الموقع الجغرافي
geolocation_service = GeolocationService()
