import requests
import os
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_TRANSLATE_API_KEY')
        self.libretranslate_url = os.getenv('LIBRETRANSLATE_URL', 'https://libretranslate.com')
        
    def translate_text(self, text: str, target_language: str = 'bs', source_language: str = 'en') -> Optional[str]:
        """
        Translate text to target language using available translation services
        """
        if not text or not text.strip():
            return text
            
        # Try Google Translate first if API key is available
        if self.google_api_key:
            result = self._translate_with_google(text, target_language, source_language)
            if result:
                return result
        
        # Fallback to LibreTranslate
        result = self._translate_with_libretranslate(text, target_language, source_language)
        if result:
            return result
        
        # If all translation services fail, return demo translation
        return self._get_demo_translation(text, target_language)
    
    def _translate_with_google(self, text: str, target_language: str, source_language: str) -> Optional[str]:
        """
        Translate using Google Cloud Translation API
        """
        try:
            url = 'https://translation.googleapis.com/language/translate/v2'
            params = {
                'key': self.google_api_key,
                'q': text,
                'target': target_language,
                'source': source_language,
                'format': 'text'
            }
            
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and 'translations' in data['data']:
                translations = data['data']['translations']
                if translations and len(translations) > 0:
                    return translations[0]['translatedText']
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Translate API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Google Translate: {e}")
            return None
    
    def _translate_with_libretranslate(self, text: str, target_language: str, source_language: str) -> Optional[str]:
        """
        Translate using LibreTranslate API
        """
        try:
            url = f"{self.libretranslate_url}/translate"
            
            # LibreTranslate uses different language codes
            # Map common codes to LibreTranslate format
            lang_mapping = {
                'bs': 'hr',  # Use Croatian as closest to Bosnian if Bosnian not available
                'en': 'en',
                'es': 'es',
                'fr': 'fr',
                'de': 'de',
                'it': 'it',
                'pt': 'pt',
                'ru': 'ru'
            }
            
            target_lang = lang_mapping.get(target_language, target_language)
            source_lang = lang_mapping.get(source_language, source_language)
            
            data = {
                'q': text,
                'source': source_lang,
                'target': target_lang,
                'format': 'text'
            }
            
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if 'translatedText' in result:
                return result['translatedText']
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LibreTranslate API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in LibreTranslate: {e}")
            return None
    
    def _get_demo_translation(self, text: str, target_language: str) -> str:
        """
        Provide demo translations for testing purposes
        """
        # Simple demo translations for common sports terms
        demo_translations = {
            'Local Football Team Wins Championship': 'Lokalni fudbalski tim osvaja prvenstvo',
            'Basketball Season Kicks Off': 'Košarkaška sezona počinje',
            'Tennis Tournament Results': 'Rezultati teniskog turnira',
            'The hometown heroes defeated their rivals 3-1 in an exciting match.': 'Domaći heroji su porazili svoje rivale 3-1 u uzbudljivoj utakmici.',
            'The new basketball season starts with high expectations.': 'Nova košarkaška sezona počinje sa velikim očekivanjima.',
            'Latest results from the international tennis tournament.': 'Najnoviji rezultati sa međunarodnog teniskog turnira.',
            'In a thrilling championship match, the local football team secured victory...': 'U uzbudljivoj finalenoj utakmici, lokalni fudbalski tim je obezbedio pobedu...',
            'Teams are preparing for what promises to be an exciting basketball season...': 'Timovi se pripremaju za ono što obećava da bude uzbudljiva košarkaška sezona...',
            'The tennis tournament concluded with surprising upsets and great matches...': 'Teniski turnir je završen sa iznenađujućim preokretima i odličnim mečevima...'
        }
        
        # Return demo translation if available, otherwise add prefix
        if text in demo_translations:
            return demo_translations[text]
        else:
            return f"[DEMO PREVOD] {text}"
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Return supported language codes and names
        """
        return {
            'en': 'English',
            'bs': 'Bosnian',
            'hr': 'Croatian',
            'sr': 'Serbian',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian'
        }
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text
        """
        # Simple language detection based on common words
        # In a real implementation, you would use a proper language detection service
        
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        spanish_words = ['el', 'la', 'y', 'o', 'pero', 'en', 'de', 'con', 'por', 'para']
        french_words = ['le', 'la', 'et', 'ou', 'mais', 'dans', 'de', 'avec', 'par', 'pour']
        
        text_lower = text.lower()
        
        english_count = sum(1 for word in english_words if word in text_lower)
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        french_count = sum(1 for word in french_words if word in text_lower)
        
        if english_count > spanish_count and english_count > french_count:
            return 'en'
        elif spanish_count > french_count:
            return 'es'
        elif french_count > 0:
            return 'fr'
        else:
            return 'en'  # Default to English

