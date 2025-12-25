"""
Sarvam AI Translation Service
Multi-language support for Indian languages
"""

import os
import httpx
import logging
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Sarvam AI Configuration
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_API_URL = "https://api.sarvam.ai/translate"

# Language mapping
LANGUAGE_CODES = {
    "English": "en-IN",
    "हिंदी": "hi-IN",
    "தமிழ்": "ta-IN",
    "తెలుగు": "te-IN",
    "मराठी": "mr-IN",
    "ಕನ್ನಡ": "kn-IN",
    "বাংলা": "bn-IN",
    "ગુજરાતી": "gu-IN",
    "മലയാളം": "ml-IN",
    "ਪੰਜਾਬੀ": "pa-IN"
}

# Reverse mapping for API responses
CODE_TO_LANGUAGE = {v: k for k, v in LANGUAGE_CODES.items()}


class SarvamTranslator:
    """
    Sarvam AI translation service for Indian languages
    """
    
    def __init__(self):
        self.api_key = SARVAM_API_KEY
        self.api_url = SARVAM_API_URL
        
        if not self.api_key:
            logger.warning("⚠️ SARVAM_API_KEY not found - translation disabled")
            self.enabled = False
        else:
            logger.info(f"✓ Sarvam AI initialized with key: {self.api_key[:10]}...")
            self.enabled = True
    
    async def translate(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str
    ) -> Optional[Dict]:
        """
        Translate text between languages
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., "hi-IN")
            target_lang: Target language code (e.g., "en-IN")
        
        Returns:
            Dict with translated text or None on error
        """
        
        if not self.enabled:
            logger.error("❌ Sarvam AI not enabled")
            return {
                "success": False,
                "error": "Translation service not configured",
                "original_text": text
            }
        
        request_id = f"sarvam_{int(os.times()[4] * 1000)}"
        logger.info(f"[{request_id}] Translation request: {source_lang} → {target_lang}")
        logger.debug(f"[{request_id}] Text length: {len(text)} chars")
        logger.debug(f"[{request_id}] Text preview: {text[:100]}...")
        
        try:
            async with httpx.AsyncClient() as client:
                # Prepare request
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "input": text,
                    "source_language_code": source_lang,
                    "target_language_code": target_lang,
                    "speaker_gender": "Female",  # Optional
                    "mode": "formal",  # formal/casual
                    "model": "mayura:v1",  # Sarvam's translation model
                    "enable_preprocessing": True
                }
                
                logger.debug(f"[{request_id}] Sending request to Sarvam API...")
                
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                logger.debug(f"[{request_id}] Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    translated_text = data.get("translated_text", "")
                    
                    logger.info(f"[{request_id}] ✓ Translation successful")
                    logger.debug(f"[{request_id}] Translated text: {translated_text[:100]}...")
                    
                    return {
                        "success": True,
                        "original_text": text,
                        "translated_text": translated_text,
                        "source_language": source_lang,
                        "target_language": target_lang,
                        "detected_language": data.get("detected_language"),
                        "confidence": data.get("confidence", 1.0)
                    }
                else:
                    error_msg = response.text
                    logger.error(f"[{request_id}] ❌ API error: {error_msg}")
                    
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}",
                        "original_text": text,
                        "details": error_msg
                    }
        
        except httpx.TimeoutException as e:
            logger.error(f"[{request_id}] ❌ Timeout: {str(e)}")
            return {
                "success": False,
                "error": "Translation request timed out",
                "original_text": text
            }
        
        except Exception as e:
            logger.error(f"[{request_id}] ❌ Unexpected error: {str(e)}")
            logger.exception(e)
            
            return {
                "success": False,
                "error": str(e),
                "original_text": text
            }
    
    async def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of input text
        
        Args:
            text: Text to analyze
        
        Returns:
            Language code (e.g., "hi-IN") or None
        """
        
        logger.debug(f"Detecting language for: {text[:50]}...")
        
        # For now, use a simple translation attempt to English
        # Sarvam API will auto-detect source language
        result = await self.translate(
            text=text,
            source_lang="auto",  # Auto-detect
            target_lang="en-IN"
        )
        
        if result.get("success"):
            detected = result.get("detected_language", "en-IN")
            logger.info(f"✓ Language detected: {detected}")
            return detected
        else:
            logger.warning("⚠️ Language detection failed")
            return None
    
    def get_language_code(self, language_name: str) -> str:
        """
        Get language code from language name
        
        Args:
            language_name: Name like "हिंदी" or "English"
        
        Returns:
            Language code like "hi-IN"
        """
        return LANGUAGE_CODES.get(language_name, "en-IN")
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get language name from code
        
        Args:
            language_code: Code like "hi-IN"
        
        Returns:
            Language name like "हिंदी"
        """
        return CODE_TO_LANGUAGE.get(language_code, "English")


# Singleton instance
translator = SarvamTranslator()


async def translate_to_english(text: str, source_language: str) -> Dict:
    """
    Translate user input to English for Gemini processing
    
    Args:
        text: User's message in their language
        source_language: Language name (e.g., "हिंदी")
    
    Returns:
        Translation result dict
    """
    
    logger.info(f"Translating to English from: {source_language}")
    
    # If already English, no translation needed
    if source_language == "English":
        logger.debug("Input already in English, skipping translation")
        return {
            "success": True,
            "original_text": text,
            "translated_text": text,
            "source_language": "en-IN",
            "target_language": "en-IN",
            "skipped": True
        }
    
    source_code = translator.get_language_code(source_language)
    
    result = await translator.translate(
        text=text,
        source_lang=source_code,
        target_lang="en-IN"
    )
    
    return result


async def translate_from_english(text: str, target_language: str) -> Dict:
    """
    Translate Gemini's English response to user's language
    
    Args:
        text: English response from Gemini
        target_language: User's language (e.g., "हिंदी")
    
    Returns:
        Translation result dict
    """
    
    logger.info(f"Translating from English to: {target_language}")
    
    # If target is English, no translation needed
    if target_language == "English":
        logger.debug("Target is English, skipping translation")
        return {
            "success": True,
            "original_text": text,
            "translated_text": text,
            "source_language": "en-IN",
            "target_language": "en-IN",
            "skipped": True
        }
    
    target_code = translator.get_language_code(target_language)
    
    result = await translator.translate(
        text=text,
        source_lang="en-IN",
        target_lang=target_code
    )
    
    return result


async def bidirectional_translate(
    user_input: str,
    user_language: str,
    gemini_response: str
) -> Dict:
    """
    Complete translation flow: User → English → Gemini → User language
    
    Args:
        user_input: User's message in their language
        user_language: User's selected language
        gemini_response: Gemini's response in English
    
    Returns:
        Dict with both translations
    """
    
    logger.info("=" * 70)
    logger.info("BIDIRECTIONAL TRANSLATION FLOW")
    logger.info("=" * 70)
    
    # Step 1: Translate user input to English
    logger.info("Step 1: User language → English")
    input_translation = await translate_to_english(user_input, user_language)
    
    if not input_translation.get("success"):
        logger.error("❌ Failed to translate user input")
        return {
            "success": False,
            "error": "Failed to translate user input",
            "input_translation": input_translation
        }
    
    english_input = input_translation.get("translated_text", user_input)
    logger.info(f"✓ User input translated: {english_input[:50]}...")
    
    # Step 2: Translate Gemini response to user language
    logger.info("Step 2: English → User language")
    response_translation = await translate_from_english(gemini_response, user_language)
    
    if not response_translation.get("success"):
        logger.error("❌ Failed to translate Gemini response")
        # Return English version as fallback
        return {
            "success": False,
            "error": "Failed to translate response",
            "english_input": english_input,
            "english_response": gemini_response,
            "translated_response": gemini_response,  # Fallback
            "response_translation": response_translation
        }
    
    translated_response = response_translation.get("translated_text", gemini_response)
    logger.info(f"✓ Response translated: {translated_response[:50]}...")
    
    logger.info("=" * 70)
    logger.info("✓ BIDIRECTIONAL TRANSLATION COMPLETE")
    logger.info("=" * 70)
    
    return {
        "success": True,
        "english_input": english_input,
        "english_response": gemini_response,
        "translated_response": translated_response,
        "input_translation": input_translation,
        "response_translation": response_translation,
        "user_language": user_language
    }


# Initialize on module load
logger.info("Sarvam AI translation module loaded")
if translator.enabled:
    logger.info("✓ Translation service ready")
else:
    logger.warning("⚠️ Translation service disabled - add SARVAM_API_KEY to .env")
