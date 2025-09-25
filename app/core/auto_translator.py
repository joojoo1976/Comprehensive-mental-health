
# الترجمة التلقائية للمحتوى

import openai
from typing import Dict, List, Optional, Any
from app.core.i18n import translator, i18n_settings
from app.config import settings

class AutoTranslator:
    """مترجم آلي للمحتوى"""

    def __init__(self):
        """تهيئة المترجم الآلي"""
        self.client = None
        if settings.openai_api_key:
            self.client = openai.OpenAI(api_key=settings.openai_api_key)

    def translate_text(self, text: str, target_locale: str, source_locale: str = None) -> Optional[str]:
        """
        ترجمة نص

        Args:
            text: النص المطلوب ترجمته
            target_locale: اللغة الهدف
            source_locale: اللغة المصدر (اختياري، سيتم الكشف تلقائياً إذا لم يتم تحديدها)

        Returns:
            النص المترجم أو None في حالة الفشل
        """
        # التحقق من وجود عميل OpenAI
        if not self.client:
            return None

        # التحقق من صحة اللغات
        if target_locale not in i18n_settings.supported_locales:
            return None

        # إذا لم يتم تحديد اللغة المصدر، قم بالكشف عنها
        if source_locale is None:
            source_locale = self.detect_language(text)

        # إذا لم يتمكن من الكشف عن اللغة المصدر، استخدم اللغة الافتراضية
        if source_locale is None or source_locale not in i18n_settings.supported_locales:
            source_locale = i18n_settings.default_locale

        # الحصول على أسماء اللغات
        source_lang_name = translator.get_translation(f"language_name.{source_locale}", source_locale)
        target_lang_name = translator.get_translation(f"language_name.{target_locale}", target_locale)

        # إنشاء طلب الترجمة
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Your task is to translate text from {source_lang_name} to {target_lang_name}. Maintain the original meaning and tone. Only return the translated text without any additional explanations or formatting."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )

            # استخراج النص المترجم
            translated_text = response.choices[0].message.content.strip()

            return translated_text
        except Exception as e:
            print(f"Translation error: {e}")
            return None

    def translate_content(self, content: Dict[str, Any], target_locale: str, source_locale: str = None) -> Optional[Dict[str, Any]]:
        """
        ترجمة محتوى

        Args:
            content: محتوى الترجمة
            target_locale: اللغة الهدف
            source_locale: اللغة المصدر (اختياري)

        Returns:
            المحتوى المترجم أو None في حالة الفشل
        """
        # نسخ المحتوى
        translated_content = content.copy()

        # ترجمة العناصر النصية
        if "title" in content:
            translated_content["title"] = self.translate_text(content["title"], target_locale, source_locale)

        if "description" in content:
            translated_content["description"] = self.translate_text(content["description"], target_locale, source_locale)

        if "content" in content:
            translated_content["content"] = self.translate_text(content["content"], target_locale, source_locale)

        if "summary" in content:
            translated_content["summary"] = self.translate_text(content["summary"], target_locale, source_locale)

        if "instructions" in content:
            translated_content["instructions"] = self.translate_text(content["instructions"], target_locale, source_locale)

        # ترجمة العناصر المتداخلة
        if "modules" in content:
            translated_content["modules"] = []
            for module in content["modules"]:
                translated_module = self.translate_content(module, target_locale, source_locale)
                if translated_module:
                    translated_content["modules"].append(translated_module)

        if "exercises" in content:
            translated_content["exercises"] = []
            for exercise in content["exercises"]:
                translated_exercise = self.translate_content(exercise, target_locale, source_locale)
                if translated_exercise:
                    translated_content["exercises"].append(translated_exercise)

        # إضافة معلومات الترجمة
        translated_content["translation_info"] = {
            "source_locale": source_locale or i18n_settings.default_locale,
            "target_locale": target_locale,
            "translated_at": "now"  # في التطبيق الحقيقي، سيتم استخدام التاريخ والوقت الفعلي
        }

        return translated_content

    def detect_language(self, text: str) -> Optional[str]:
        """
        الكشف عن لغة النص

        Args:
            text: النص المطلوب الكشف عن لغته

        Returns:
            رمز اللغة أو None في حالة الفشل
        """
        # التحقق من وجود عميل OpenAI
        if not self.client:
            return None

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a language detection expert. Your task is to identify the language of the given text and return only the ISO 639-1 language code (e.g., 'en' for English, 'ar' for Arabic). If you are unsure, return 'unknown'."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=10,
                temperature=0.1
            )

            # استخراج رمز اللغة
            language_code = response.choices[0].message.content.strip().lower()

            # التحقق مما إذا كانت اللغة مدعومة
            if language_code in i18n_settings.supported_locales:
                return language_code

            return None
        except Exception as e:
            print(f"Language detection error: {e}")
            return None

    def get_available_translations(self, content: Dict[str, Any]) -> List[str]:
        """
        الحصول على اللغات المتاحة للترجمة

        Args:
            content: المحتوى

        Returns:
            قائمة باللغات المتاحة للترجمة
        """
        # في التطبيق الحقيقي، سيتم التحقق من قاعدة البيانات
        # هنا نعيد جميع اللغات المدعومة
        return i18n_settings.supported_locales

    def batch_translate(self, texts: List[str], target_locale: str, source_locale: str = None) -> List[Optional[str]]:
        """
        ترجمة دفعة من النصوص

        Args:
            texts: قائمة النصوص المطلوب ترجمتها
            target_locale: اللغة الهدف
            source_locale: اللغة المصدر (اختياري)

        Returns:
            قائمة بالنصوص المترجمة
        """
        # التحقق من وجود عميل OpenAI
        if not self.client:
            return [None] * len(texts)

        # التحقق من صحة اللغات
        if target_locale not in i18n_settings.supported_locales:
            return [None] * len(texts)

        # إذا لم يتم تحديد اللغة المصدر، قم بالكشف عنها
        if source_locale is None:
            # في التطبيق الحقيقي، سيتم الكشف عن لغة كل نص على حدة
            # هنا سنفترض أن جميع النصوص بنفس اللغة
            sample_text = texts[0] if texts else ""
            source_locale = self.detect_language(sample_text)

        # إذا لم يتمكن من الكشف عن اللغة المصدر، استخدم اللغة الافتراضية
        if source_locale is None or source_locale not in i18n_settings.supported_locales:
            source_locale = i18n_settings.default_locale

        # الحصول على أسماء اللغات
        source_lang_name = translator.get_translation(f"language_name.{source_locale}", source_locale)
        target_lang_name = translator.get_translation(f"language_name.{target_locale}", target_locale)

        # إنشاء طلب الترجمة
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Your task is to translate texts from {source_lang_name} to {target_lang_name}. Maintain the original meaning and tone. Return each translated text on a new line without any additional explanations or formatting."
                    },
                    {
                        "role": "user",
                        "content": "\n".join(texts)
                    }
                ],
                max_tokens=2000 * len(texts),
                temperature=0.1
            )

            # استخراج النصوص المترجمة
            translated_texts = response.choices[0].message.content.strip().split("\n")

            # التأكد من أن عدد النصوص المترجمة مطابق للنصوص الأصلية
            if len(translated_texts) != len(texts):
                return [None] * len(texts)

            return translated_texts
        except Exception as e:
            print(f"Batch translation error: {e}")
            return [None] * len(texts)

# إنشاء مثيل من المترجم الآلي
auto_translator = AutoTranslator()
