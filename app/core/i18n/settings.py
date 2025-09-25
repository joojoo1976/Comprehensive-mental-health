# إعدادات النظام الدولي

from typing import Dict, List, Optional
from pydantic import BaseSettings, Field
import os

class I18nSettings(BaseSettings):
    # اللغات المدعومة
    supported_locales: List[str] = [
        "ar",  # العربية
        "en",  # الإنجليزية
        "fr",  # الفرنسية
        "es",  # الإسبانية
        "de",  # الألمانية
        "zh",  # الصينية
        "ja",  # اليابانية
        "ko",  # الكورية
        "ru",  # الروسية
        "pt",  # البرتغالية
        "it",  # الإيطالية
        "hi",  # الهندية
        "tr",  # التركية
        "th",  # التايلاندية
        "vi",  # الفيتنامية
        "nl",  # الهولندية
        "sv",  # السويدية
        "da",  # الدنماركية
        "no",  # النرويجية
        "fi",  # الفنلندية
        "pl",  # البولندية
        "cs",  # التشيكية
        "hu",  # المجرية
        "ro",  # الرومانية
        "bg",  # البلغارية
        "hr",  # الكرواتية
        "sk",  # السلوفاكية
        "sl",  # السلوفينية
        "et",  # الإستونية
        "lv",  # اللاتفية
        "lt",  # الليتوانية
        "mt",  # المالطية
        "ga",  # الأيرلندية
        "cy",  # الويلزية
        "eu",  # الباسك
        "ca",  # الكتالونية
        "gl",  # الجاليكية
        "is",  # الآيسلندية
        "mk",  # المقدونية
        "sq",  # الألبانية
        "bs",  # البوسنية
        "sr",  # الصربية
        "me",  # الجبل الأسود
        "uk",  # الأوكرانية
        "be",  # البيلاروسية
        "kk",  # الكازاخية
        "ky",  # القيرغيزية
        "tg",  # الطاجيكية
        "az",  # الأذربيجانية
        "hy",  # الأرمينية
        "ka",  # الجورجية
        "he",  # العبرية
        "ur",  # الأردية
        "fa",  # الفارسية
        "ps",  # البشتو
        "am",  # الأمهرية
        "ne",  # النيبالية
        "si",  # السنهالية
        "bn",  # البنغالية
        "gu",  # الغوجاراتية
        "pa",  # البنجابية
        "mr",  # الماراتية
        "kn",  # الكنادية
        "ml",  # المالايالامية
        "ta",  # التاميلية
        "te",  # التيلوغوية
        "as",  # آسامية
        "or",  # الأورية
        "my",  # البورمية
        "km",  # الخميرية
        "lo",  # اللاووية
        "ka",  # الجورجية
        "jv",  # الجاوية
        "su",  # السundanese
        "mg",  # المالاغاسية
        "ny",  # النيانجا
        "ig",  # الإيجبو
        "yo",  # اليوروبا
        "ha",  # الهوسا
        "sw",  # السواحيلية
        "zu",  # الزولو
        "af",  # الأفريقانية
        "st",  # السسوتو
        "nso",  # الشمالية السوتو
        "tn",  # التسوانا
        "ss",  # السسواتي
        "xh",  # الخوسا
        "ve",  # الفenda
        "ff",  # الفولانية
        "ki",  # الكيكويو
        "rw",  # الكينيارواندا
        "rn",  # الكيرندي
        "lg",  # الجاندا
        "ak",  # الأكانتية
        "tw",  # التوي
        "ff",  # الفولانية
        "wo",  # الولوفية
        "bm",  # البامبارا
        "ki",  # الكيكويو
        "ga",  # الأيرلندية
        "gd",  # الأسكتلندية
        "gv",  # المانكس
        "br",  # البريتونية
        "kw",  # الكورنية
        "eo",  # الإسبرانتو
        "ia",  # الأنترلينغوا
        "tl",  # التاغالوغية
        "haw",  # هاواي
        "fj",  # فيجية
        "sm",  # الساموية
        "to",  # التونغية
        "mi",  # الماورية
        "ty",  # التاهيتية
        "qu",  # الكيتشوا
        "ay",  # الأymara
        "gn",  # الغواراني
        "ht",  # الهايتية
        "na",  # الناورو
        "ii",  # اليي
        "kj",  # الكوانياما
        "ng",  # الندمبو
        "nr",  # الجنوبية ndebele
        "om",  # الأمهرية
        "pi",  # البالي
        "sc",  # السardinian
        "ti",  # التجرينية
        "ts",  # التسونجا
        "uz",  # الأوزبكية
        "wa",  # والونية
        "yi",  # اليديشية
        "za",  # الزوانجية
        "an",  # الأراغونية
        "av",  # الأفارية
        "ce",  # الشيشينية
        "cv",  # الشواشية
        "dv",  # المالديفية
        "dz",  # البوتانية
        "ee",  # الإوي
        "fo",  # الفاروية
        "fy",  # الفريزية
        "gl",  # الجاليكية
        "haw",  # هاواي
        "ia",  # الأنترلينغوا
        "id",  # الإندونيسية
        "ie",  # الأنترلينغوا
        "io",  # الإيدو
        "iu",  # الإنكتيتوت
        "ka",  # الجورجية
        "kg",  # الكونغولية
        "ki",  # الكيكويو
        "kj",  # الكوانياما
        "kl",  # الكالاليست
        "kr",  # الكانوري
        "ks",  # الكشميرية
        "ku",  # الكردية
        "kum",  # الكوميكية
        "kv",  # الكومي
        "kw",  # الكورنية
        "kx",  # الكوانياما
        "ky",  # القيرغيزية
        "la",  # اللاتينية
        "lb",  # اللوكسمبورغية
        "lg",  # الجاندا
        "li",  # ليمبورغية
        "ln",  # لينغالا
        "lo",  # اللاووية
        "lt",  # الليتوانية
        "lv",  # اللاتفية
        "mg",  # المالاغاسية
        "mh",  # المارشالية
        "mi",  # الماورية
        "mk",  # المقدونية
        "ml",  # المالايالامية
        "mn",  # المنغولية
        "mo",  # المولدوفية
        "mr",  # الماراتية
        "ms",  # الملايو
        "mt",  # المالطية
        "my",  # البورمية
        "na",  # الناورو
        "nb",  # النرويجية بوكمال
        "nd",  # الشمالية ndebele
        "ne",  # النيبالية
        "ng",  # الندمبو
        "nl",  # الهولندية
        "nn",  # النرويجية نينorsk
        "no",  # النرويجية
        "nr",  # الجنوبية ndebele
        "nv",  # النافاجو
        "ny",  # النيانجا
        "oc",  # الأوكيتانية
        "oj",  # أوجيبوا
        "om",  # الأمهرية
        "or",  # الأورية
        "os",  # الأوسيتية
        "pa",  # البنجابية
        "pi",  # البالي
        "pl",  # البولندية
        "ps",  # البشتو
        "pt",  # البرتغالية
        "qu",  # الكيتشوا
        "rm",  # الرومانشية
        "rn",  # الكيرندي
        "ro",  # الرومانية
        "ru",  # الروسية
        "rw",  # الكينيارواندا
        "sa",  # السanskrit
        "sc",  # السardinian
        "sd",  # السindhية
        "se",  # الشمالية سامي
        "sg",  # Sangho
        "sh",  # Serbo-Croatian
        "si",  # السنهالية
        "sk",  # السلوفاكية
        "sl",  # السلوفينية
        "sm",  # الساموية
        "sn",  # الشونا
        "so",  # الصومالية
        "sq",  # الألبانية
        "sr",  # الصربية
        "ss",  # السسواتي
        "st",  # السسوتو
        "su",  # السundanese
        "sv",  # السويدية
        "sw",  # السواحيلية
        "ta",  # التاميلية
        "te",  # التيلوغوية
        "tg",  # الطاجيكية
        "th",  # التايلاندية
        "ti",  # التجرينية
        "tk",  # التركمنية
        "tl",  # التاغالوغية
        "tn",  # التسوانا
        "to",  # التونغية
        "tr",  # التركية
        "ts",  # التسونجا
        "tt",  # التتارية
        "tw",  # التوي
        "ty",  # التاهيتية
        "ug",  # الأويغورية
        "uk",  # الأوكرانية
        "ur",  # الأردية
        "uz",  # الأوزبكية
        "ve",  # الفenda
        "vi",  # الفيتنامية
        "vo",  # الفولابيك
        "wa",  # والونية
        "wo",  # الولوفية
        "xh",  # الخوسا
        "yi",  # اليديشية
        "yo",  # اليوروبا
        "za",  # الزوانجية
        "zh",  # الصينية
        "zu"   # الزولو
    ]

    # اللغة الافتراضية
    default_locale: str = "en"

    # اللغة الافتراضية للمنطقة العربية
    default_arabic_locale: str = "ar"

    # اللغة الافتراضية للآسياء
    default_asian_locale: str = "zh"

    # اللغة الافتراضية لأوروبا
    default_european_locale: str = "en"

    # اللغة الافتراضية لأمريكا اللاتينية
    default_latin_american_locale: str = "es"

    # اللغة الافتراضية لأفريقيا
    default_african_locale: str = "fr"

    # اللغة الافتراضية لأوقيانوسيا
    default_oceania_locale: str = "en"

    # اللغة الافتراضية لشمال أمريكا
    default_north_american_locale: str = "en"

    # اللغة الافتراضية لجنوب أمريكا
    default_south_american_locale: str = "es"

    # اللغة الافتراضية لآسيا الوسطى
    default_central_asian_locale: str = "ru"

    # اللغة الافتراضية للشرق الأوسط
    default_middle_east_locale: str = "ar"

    # اللغة الافتراضية لجنوب شرق آسيا
    default_southeast_asian_locale: str = "th"

    # اللغة الافتراضية لجنوب آسيا
    default_south_asian_locale: str = "hi"

    # اللغة الافتراضية لأوروبا الشرقية
    default_eastern_european_locale: str = "ru"

    # اللغة الافتراضية لأوروبا الغربية
    default_western_european_locale: str = "en"

    # اللغة الافتراضية لأوروبا الشمالية
    default_northern_european_locale: str = "sv"

    # اللغة الافتراضية لأوروبا الجنوبية
    default_southern_european_locale: str = "it"

    # اللغة الافتراضية لأوروبا الوسطى
    default_central_european_locale: str = "de"

    # اللغة الافتراضية للكاريبي
    default_caribbean_locale: str = "es"

    # اللغة الافتراضية لأمريكا الوسطى
    default_central_american_locale: str = "es"

    # اللغة الافتراضية للشرق الأقصى
    default_far_east_locale: str = "zh"

    # اللغة الافتراضية للشرق الأوسط وشمال أفريقيا
    default_mena_locale: str = "ar"

    # اللغة الافتراضية للمناطق النائية
    default_remote_locale: str = "en"

    # اللغة الافتراضية للمناطق الحضرية
    default_urban_locale: str = "en"

    # اللغة الافتراضية للمناطق الريفية
    default_rural_locale: str = "en"

    # اللغة الافتراضية للمناطق الساحلية
    default_coastal_locale: str = "en"

    # اللغة الافتراضية للمناطق الداخلية
    default_inland_locale: str = "en"

    # اللغة الافتراضية للمناطق الجبلية
    default_mountain_locale: str = "en"

    # اللغة الافتراضية للمناطق الصحراوية
    default_desert_locale: str = "ar"

    # اللغة الافتراضية للمناطق الاستوائية
    default_tropical_locale: str = "en"

    # اللغة الافتراضية للمناطق القارية
    default_continental_locale: str = "en"

    # اللغة الافتراضية للمناطق الجزرية
    default_island_locale: str = "en"

    # اللغة الافتراضية للمناطق القريبة من القطبين
    default_polar_locale: str = "en"

    # اللغة الافتراضية للمناطق الاستوائية
    default_subtropical_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه الاستوائية
    default_semitropical_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه القاحلة
    default_semi_arid_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه باردة
    default_semi_cold_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه حارة
    default_semi_hot_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه جافة
    default_semi_dry_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه رطبة
    default_semi_humid_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه جبلية
    default_semi_mountainous_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه صحراوية
    default_semi_desert_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه ساحلية
    default_semi_coastal_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه داخلية
    default_semi_inland_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه حضرية
    default_semi_urban_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه ريفية
    default_semi_rural_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه جزرية
    default_semi_island_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه قطبية
    default_semi_polar_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه استوائية
    default_semi_subtropical_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه قارية
    default_semi_continental_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه استوائية
    default_semi_tropical_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه قاحلة
    default_semi_arid_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه باردة
    default_semi_cold_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه حارة
    default_semi_hot_locale: str = "en"

    # اللغة الافتراضية للمناطق شبه جافة
    default_semi_dry_locale: str = "en"

    # إعدادات الوصول اللغوي
    language_access_enabled: bool = True
    language_access_required: bool = True
    language_access_timeout: int = 30  # بالثواني

    # إعدادات الموقع الجغرافي
    geo_location_enabled: bool = True
    geo_location_required: bool = True
    geo_location_timeout: int = 30  # بالثواني

    # إعدادات الاختيار التلقائي للغة
    auto_detect_language: bool = True
    auto_detect_region: bool = True

    # إعدادات الترجمة
    translation_enabled: bool = True
    translation_service: str = "google"  # google, azure, ibm, etc.
    translation_api_key: Optional[str] = None

    # إعدارات الخطوط
    font_arabic: str = "Tahoma"
    font_chinese: str = "SimSun"
    font_japanese: str = "MS Gothic"
    font_korean: str = "Malgun Gothic"
    font_russian: str = "Arial"
    font_default: str = "Arial"

    class Config:
        env_file = ".env"

# إنشاء كائن الإعدادات
i18n_settings = I18nSettings()
