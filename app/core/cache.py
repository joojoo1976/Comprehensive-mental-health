# خدمة ذاكرة التخزين المؤقت للتطبيق

import time
import pickle
from typing import Any, Optional
from threading import Lock


class SimpleCacheService:
    """
    خدمة ذاكرة تخزين مؤقت بسيطة باستخدام قاموس
    في التطبيقات الحقيقية، سيتم استخدام Redis أو خدمة مماثلة
    """

    def __init__(self, default_timeout: int = 300):
        """
        تهيئة خدمة ذاكرة التخزين المؤقت

        Args:
            default_timeout: وقت انتهاء الصلاحية الافتراضي بالثواني (5 دقائق)
        """
        self.cache = {}
        self.timeouts = {}
        self.lock = Lock()
        self.default_timeout = default_timeout

    def get(self, key: str) -> Optional[Any]:
        """
        الحصول على قيمة من ذاكرة التخزين المؤقت

        Args:
            key: مفتاح القيمة المطلوبة

        Returns:
            القيمة إذا كانت موجودة وغير منتهية الصلاحية، أو None
        """
        with self.lock:
            # التحقق من وجود المفتاح
            if key not in self.cache:
                return None

            # التحقق من انتهاء الصلاحية
            if key in self.timeouts:
                if time.time() > self.timeouts[key]:
                    # انتهت صلاحية التخزين، حذف القيمة
                    del self.cache[key]
                    del self.timeouts[key]
                    return None

            return self.cache[key]

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        حفظ قيمة في ذاكرة التخزين المؤقت

        Args:
            key: مفتاح القيمة
            value: القيمة المحفوظة
            timeout: وقت انتهاء الصلاحية بالثواني (استخدم القيمة الافتراضية إذا كان None)

        Returns:
            True إذا تم الحفظ بنجاح
        """
        if timeout is None:
            timeout = self.default_timeout

        with self.lock:
            try:
                self.cache[key] = value
                self.timeouts[key] = time.time() + timeout
                return True
            except Exception:
                return False

    def delete(self, key: str) -> bool:
        """
        حذف قيمة من ذاكرة التخزين المؤقت

        Args:
            key: مفتاح القيمة المحذوفة

        Returns:
            True إذا تم الحذف بنجاح، أو False إذا لم يكن المفتاح موجوداً
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.timeouts:
                    del self.timeouts[key]
                return True
            return False

    def clear(self) -> bool:
        """
        مسح جميع القيم من ذاكرة التخزين المؤقت

        Returns:
            True إذا تم المسح بنجاح
        """
        with self.lock:
            self.cache.clear()
            self.timeouts.clear()
            return True

    def get_user(self, user_id: int) -> Optional[Any]:
        """
        الحصول على مستخدم من ذاكرة التخزين المؤقت

        Args:
            user_id: معرف المستخدم

        Returns:
            بيانات المستخدم إذا كانت موجودة وغير منتهية الصلاحية، أو None
        """
        return self.get(f"user:{user_id}")

    def set_user(self, user_data: Any, timeout: Optional[int] = None) -> bool:
        """
        حفظ بيانات المستخدم في ذاكرة التخزين المؤقت

        Args:
            user_data: بيانات المستخدم
            timeout: وقت انتهاء الصلاحية بالثواني (استخدم القيمة الافتراضية إذا كان None)

        Returns:
            True إذا تم الحفظ بنجاح
        """
        # استخدام معرف المستخدم كمفتاح
        user_id = getattr(user_data, 'id', None)
        if not user_id:
            return False

        return self.set(f"user:{user_id}", user_data, timeout)

    def invalidate_user(self, user_id: int) -> bool:
        """
        إبطال صلاحية ذاكرة التخزين المؤقت لمستخدم معين

        Args:
            user_id: معرف المستخدم

        Returns:
            True إذا تم الإبطال بنجاح
        """
        return self.delete(f"user:{user_id}")


# إنشاء مثيل واحد عالمي لخدمة ذاكرة التخزين المؤقت
cache_service = SimpleCacheService()
