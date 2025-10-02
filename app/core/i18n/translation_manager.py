
# مدير الترجمة للنظام متعدد اللغات

import json
import locale
from typing import Dict, Optional, List, Any
from pathlib import Path
from app.core.i18n.settings import I18nSettings

# إنشاء إعدادات النظام الدولي
i18n_settings = I18nSettings()

# تحديد مسار الملفات اللغوية
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOCALES_DIR = BASE_DIR / "locales"


class TranslationManager:
    """مدير الترجمة للتعامل مع اللغات المختلفة"""

    # قاموس لربط رموز الدول (ISO 3166-1 alpha-2) باللغة الإقليمية الافتراضية
    # هذا يجعل الدالة get_locale_by_region أكثر قابلية للصيانة
    REGION_TO_LOCALE_MAP = {
        i18n_settings.default_middle_east_locale: [
            "sa", "ae", "eg", "jo", "lb", "sy", "iq", "ye", "om", "qa", "bh", "kw", "ps", "tr", "cy", "az", "ge", "am", "il"
        ],
        i18n_settings.default_far_east_locale: [
            "cn", "hk", "mo", "tw"
        ],
        i18n_settings.default_south_asian_locale: [
            "in", "pk", "bd", "np", "lk", "mv", "bt"
        ],
        i18n_settings.default_african_locale: [
            "fr", "mc", "cd", "ci", "mg", "ne", "bj", "bf", "sn", "tg", "ga", "ml", "mu"
        ],
        i18n_settings.default_central_european_locale: [
            "de", "at", "li", "nl"
        ],
        i18n_settings.default_latin_american_locale: [
            "es", "mx", "ar", "co", "pe", "ve", "gt", "cr", "pa", "ec", "bo", "py", "sv", "hn", "ni", "do", "pr", "cu"
        ],
        i18n_settings.default_western_european_locale: [
            "gb", "ie", "us", "ca", "au", "nz", "za", "zw", "ng", "ke", "gh", "tz", "ug", "zm", "bw", "na", "sz", "mw", "ls"
        ],
        i18n_settings.default_eastern_european_locale: [
            "ru", "ua", "by", "kz", "kg", "tm", "uz", "pl", "cz", "sk", "hu", "ro", "bg", "hr", "rs", "me", "ba", "al", "mk", "gr"
        ],
        i18n_settings.default_south_american_locale: [
            "pt", "br", "ao", "mz", "cv", "gw", "st", "tl", "gq", "gm"
        ],
        i18n_settings.default_southern_european_locale: ["it", "va", "sm", "mt", "si"],
        i18n_settings.default_northern_european_locale: ["fi", "se", "no", "dk", "fo", "is", "ax"],
        i18n_settings.default_asian_locale: ["jp", "kr", "kp"],
        i18n_settings.default_southeast_asian_locale: ["th", "kh", "la", "vn", "mm", "id", "ph", "sg", "my", "bn"],
    }

    def __init__(self):
        """تهيئة مدير الترجمة"""
        self.translations = {}
        self.current_locale: str = i18n_settings.default_locale
        self.load_all_translations()

    def load_all_translations(self):
        """تحميل جميع ملفات الترجمة"""
        # التأكد من وجود مجلد اللغات
        if not LOCALES_DIR.exists():
            LOCALES_DIR.mkdir(parents=True, exist_ok=True)

        # تحميل ملفات الترجمة لكل اللغات المدعومة
        for lang_code in i18n_settings.supported_locales:
            self.load_translation(lang_code)

    def load_translation(self, lang_code: str):
        """تحميل ملف ترجمة محدد"""
        translation_file = LOCALES_DIR / f"{lang_code}.json"

        if translation_file.exists():
            try:
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            except json.JSONDecodeError as e:
                print(
                    f"Error loading translation file {translation_file}: {e}")
                self.translations[lang_code] = {}
        else:
            # إذا لم يوجد ملف ترجمة، قم بإنشاء ملف فارغ
            self.translations[lang_code] = {}
            self.save_translation(lang_code)

    def save_translation(self, lang_code: str) -> bool:
        """حفظ ملف ترجمة محدد"""
        translation_file = LOCALES_DIR / f"{lang_code}.json"

        try:
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations.get(lang_code, {}),
                          f, ensure_ascii=False, indent=2)
            return True
        except (IOError, TypeError) as e:
            print(f"Error saving translation file {translation_file}: {e}")
            return False

    def get_translation(self, key: str, lang_code: Optional[str] = None) -> str:
        """الحصول على نص مترجم بناءً على المفتاح"""
        lang = lang_code or self.current_locale

        # التحقق مما إذا كانت اللغة مدعومة
        if lang not in i18n_settings.supported_locales:
            lang = i18n_settings.default_locale

        # البحث عن الترجمة
        translation = self._get_nested_value(
            self.translations.get(lang, {}), key.split('.'))

        # إذا لم يتم العثور على الترجمة، استخدم اللغة الافتراضية
        if translation is None:
            translation = self._get_nested_value(
                self.translations.get(i18n_settings.default_locale, {}), key)

        # إذا لم يتم العثور على الترجمة في اللغة الافتراضية، أعد المفتاح
        return translation if translation is not None else key

    def _get_nested_value(self, data: dict, keys: List[str]) -> Optional[Any]:
        """الحصول على قيمة متداخلة في القاموس باستخدام مفتاح بنقطي"""
        value = data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value if not isinstance(value, dict) else None

    def set_locale(self, locale: str):
        """تعيين اللغة الحالية"""
        if locale in i18n_settings.supported_locales:
            self.current_locale = locale
            return True
        return False

    def get_user_locale_from_browser(self, request) -> Optional[str]:
        """الحصول على اللغة من المتصفح"""
        # الحصول من رأس Accept-Language
        accept_language = request.headers.get("Accept-Language")
        if accept_language:
            # تحليل رؤوس Accept-Language
            languages = []
            for lang_range in accept_language.split(","):
                parts = lang_range.split(";")
                lang = parts[0].strip()
                quality = 1.0

                if len(parts) > 1 and parts[1].strip().startswith("q="):
                    try:
                        quality = float(parts[1].strip()[2:])
                    except ValueError:
                        quality = 1.0

                languages.append((lang, quality))

            # ترتيب اللغات حسب الجودة
            languages.sort(key=lambda x: x[1], reverse=True)

            # البحث عن أول لغة مدعومة
            for lang, _ in languages:
                # التحقق من الرموز الكاملة (مثل en-US) والرموز المختصرة (مثل en)
                for supported in [lang.split('-')[0], lang]:
                    if supported in i18n_settings.supported_locales:
                        return supported

        return None

    def get_locale_by_region(self, region: str) -> str:
        """الحصول على اللغة المناسبة للمنطقة الجغرافية"""
        if not region:
            return i18n_settings.default_locale

        region_code = region.lower()

        # البحث في القاموس عن اللغة المناسبة
        for locale, countries in self.REGION_TO_LOCALE_MAP.items():
            if region_code in countries:
                return locale

        # إذا لم يتم العثور على تطابق، أعد اللغة الافتراضية
        return i18n_settings.default_locale

    def get_locale_by_timezone(self, timezone: str) -> str:
        """الحصول على اللغة بناءً على المنطقة الزمنية"""
        # تحديد المنطقة من المنطقة الزمنية
        region = timezone.split('/')[-1].split(':')[0].lower()

        # بعض التعديلات الخاصة للمناطق الزمنية
        if timezone.startswith("America/"):
            return i18n_settings.default_north_american_locale
        elif timezone.startswith("Europe/"):
            return i18n_settings.default_western_european_locale
        elif timezone.startswith("Asia/"):
            return i18n_settings.default_asian_locale
        elif timezone.startswith("Africa/"):
            return i18n_settings.default_african_locale
        elif timezone.startswith("Pacific/"):
            return i18n_settings.default_oceania_locale
        elif timezone.startswith("Indian/"):
            return i18n_settings.default_south_asian_locale
        elif timezone.startswith("Atlantic/"):
            return i18n_settings.default_western_european_locale
        elif timezone.startswith("Australia/"):
            return i18n_settings.default_oceania_locale
        elif timezone.startswith("Antarctica/"):
            return i18n_settings.default_remote_locale
        else:
            return i18n_settings.default_locale

    def get_locale_by_ip(self, ip_address: str) -> str:
        """الحصول على اللغة بناءً على عنوان IP"""
        # في تطبيق حقيقي، سيتم استخدام خدمة مثل IPinfo أو MaxMind
        # هنا نستخدم منطقة افتراضية بناءً على البادئة
        if ip_address.startswith("192.168.") or ip_address.startswith("10.") or ip_address.startswith("172."):
            # عناوين IP الخاصة
            return i18n_settings.default_locale

        # في الواقع، سيتم استدعاء خدمة تحديد الموقع الجغرافي هنا
        # هذا مثال مبسط
        return i18n_settings.default_locale

    def get_locale_by_device_language(self) -> str:
        """الحصول على لغة الجهاز"""
        try:
            # محاولة الحصول على لغة النظام
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                # تحويل إلى رمز اللغة (مثل 'en_US' إلى 'en')
                lang_code = system_locale.split('_')[0]
                if lang_code in i18n_settings.supported_locales:
                    return lang_code
        except:
            pass

        # العودة إلى اللغة الافتراضية
        return i18n_settings.default_locale

    def get_available_translations(self) -> Dict[str, str]:
        """الحصول على قائمة اللغات المتاحة مع أسمائها"""
        available_langs = {}
        # المرور على جميع اللغات المدعومة
        for lang_code in i18n_settings.supported_locales:
            # الحصول على اسم اللغة من ملف الترجمة الخاص بها
            # على سبيل المثال، للحصول على اسم اللغة العربية، نبحث عن مفتاح "language_native_name.ar" في ملف "ar.json"
            lang_name = self.get_translation(
                f"language_native_name.{lang_code}", lang_code=lang_code)

            # إذا لم يتم العثور على الترجمة، استخدم رمز اللغة كقيمة افتراضية
            if lang_name == f"language_native_name.{lang_code}":
                lang_name = lang_code

            available_langs[lang_code] = lang_name

        return available_langs


# إنشاء مثيل من مدير الترجمة
translator = TranslationManager()
