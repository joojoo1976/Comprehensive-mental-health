# نظام التوطين والدولنة

from .translation_manager import translator
from .settings import I18nSettings


# إنشاء إعدادات النظام الدولي
i18n_settings = I18nSettings()

# دالة مساعدة للحصول على الترجمة
def _(key: str, locale: str = None) -> str:
    """
    دالة مساعدة للحصول على الترجمة

    Args:
        key: مفتاح النص المترجم
        locale: رمز اللغة (اختياري)

    Returns:
        النص المترجم
    """
    return translator.get_translation(key, locale)
