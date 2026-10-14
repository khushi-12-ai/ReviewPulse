"""
Multilingual language detection and translation utility for ReviewPulse.
Provides robust fallback between GoogleTranslator and MyMemoryTranslator.
"""
import logging
from langdetect import detect
from deep_translator import GoogleTranslator, MyMemoryTranslator

logger = logging.getLogger(__name__)

# Map 2-letter ISO codes to MyMemory supported language names/codes
MYMEMORY_LANG_MAP = {
    'es': 'spanish',
    'fr': 'french',
    'de': 'german',
    'it': 'italian',
    'pt': 'portuguese',
    'zh-cn': 'chinese simplified',
    'zh-tw': 'chinese traditional',
    'zh': 'chinese simplified',
    'ja': 'japanese',
    'ko': 'korean',
    'ru': 'russian',
    'ar': 'arabic',
    'hi': 'hindi',
    'nl': 'dutch',
    'tr': 'turkish',
    'vi': 'vietnamese',
    'pl': 'polish',
    'sv': 'swedish',
    'no': 'norwegian bokmål',
    'da': 'danish',
    'fi': 'finnish',
    'el': 'greek',
    'cs': 'czech',
    'ro': 'romanian',
    'hu': 'hungarian',
    'id': 'indonesian',
    'th': 'thai'
}


def detect_and_translate(text: str):
    """
    Detects the language of input text and translates it to English if non-English.
    
    Returns:
        tuple (translated_text, detected_language_code)
    """
    if not text or not str(text).strip():
        return text, "unknown"
    
    cleaned_text = str(text).strip()
    
    # 1. Detect language
    try:
        lang_code = detect(cleaned_text)
    except Exception as e:
        logger.warning(f"Language detection fallback: {e}")
        lang_code = "unknown"
    
    # If already English or unknown, return directly
    if lang_code in ["en", "unknown"]:
        return cleaned_text, lang_code
    
    # 2. Attempt GoogleTranslator first
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(cleaned_text)
        if translated and str(translated).strip():
            return translated, lang_code
    except Exception as e:
        logger.info(f"GoogleTranslator unavailable ({e}), trying MyMemoryTranslator fallback...")
    
    # 3. Fallback to MyMemoryTranslator with code resolution
    try:
        src_lang = MYMEMORY_LANG_MAP.get(lang_code.lower(), lang_code.lower())
        translated = MyMemoryTranslator(source=src_lang, target='en-US').translate(cleaned_text)
        if translated and str(translated).strip():
            return translated, lang_code
    except Exception as e:
        logger.warning(f"MyMemory translation fallback failed: {e}")
    
    # If all translations fail, return original text with detected language
    return cleaned_text, lang_code
