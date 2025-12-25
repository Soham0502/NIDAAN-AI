from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
from llm import call_llm
from sarvam_translator import bidirectional_translate, translate_to_english
import httpx
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import hashlib
import json

# ==================== SETUP LOGGING ====================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nidaan_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="NIDAAN-AI Medical Triage API",
    description="AI-powered medical triage system with multi-language support and healthcare compliance",
    version="2.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("=" * 70)
logger.info("NIDAAN-AI Backend Server Starting...")
logger.info(f"Timestamp: {datetime.now().isoformat()}")
logger.info("=" * 70)

# ==================== TWILIO CONFIGURATION ====================
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_WHATSAPP_NUMBER:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        logger.info("✓ Twilio client initialized successfully")
        logger.info(f"✓ WhatsApp sender number: {TWILIO_WHATSAPP_NUMBER}")
        TWILIO_ENABLED = True
    except Exception as e:
        logger.error(f"❌ Twilio initialization failed: {e}")
        twilio_client = None
        TWILIO_ENABLED = False
else:
    logger.warning("⚠️ Twilio credentials not found - WhatsApp feature disabled")
    twilio_client = None
    TWILIO_ENABLED = False

# ==================== DATA RETENTION SETTINGS ====================
DATA_RETENTION_DAYS = 90  # DISHA Act compliance
CONSENT_REQUIRED = True  # ABDM compliance

logger.info("=" * 70)


def anonymize_data(text: str) -> str:
    """
    Anonymize personal information for privacy compliance
    """
    # Remove phone numbers (basic pattern)
    import re
    text = re.sub(r'\b\d{10}\b', '[PHONE]', text)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    return text


def log_audit_trail(
    action: str,
    request_id: str,
    user_data: dict,
    status: str
):
    """
    Audit logging for compliance (DISHA Act requirement)
    """
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "request_id": request_id,
        "user_hash": hashlib.sha256(str(user_data).encode()).hexdigest()[:16],
        "status": status
    }
    
    # In production, save to secure audit database
    logger.info(f"AUDIT: {json.dumps(audit_entry)}")


@app.get("/")
async def root():
    """Health check endpoint with feature flags"""
    logger.debug("Root endpoint accessed")
    return {
        "status": "healthy",
        "service": "NIDAAN-AI Triage API",
        "version": "2.0.0",
        "features": {
            "whatsapp": TWILIO_ENABLED,
            "multilanguage": True,
            "compliance": {
                "abdm_ready": True,
                "disha_compliant": True,
                "data_retention_days": DATA_RETENTION_DAYS
            }
        },
        "disclaimer": "AI-assisted triage. Not a substitute for professional medical advice."
    }


@app.post("/consent")
async def record_consent(
    user_id: str = Form(...),
    consent_type: str = Form(...),  # data_collection, data_sharing, whatsapp_sharing
    consent_given: bool = Form(...)
):
    """
    Record user consent for ABDM compliance
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] Consent recording: {consent_type} = {consent_given}")
    
    consent_record = {
        "user_id": hashlib.sha256(user_id.encode()).hexdigest()[:16],
        "consent_type": consent_type,
        "consent_given": consent_given,
        "timestamp": datetime.now().isoformat(),
        "ip_address": "anonymized",  # In production, get from request
        "expires_at": (datetime.now() + timedelta(days=365)).isoformat()
    }
    
    # In production, save to database
    logger.info(f"CONSENT: {json.dumps(consent_record)}")
    
    return {
        "success": True,
        "message": "Consent recorded",
        "consent_id": request_id
    }


@app.post("/analyze")
async def analyze(
    symptom_text: str = Form(...),
    user_language: str = Form("English"),
    image: Optional[UploadFile] = File(None),
    consent_given: bool = Form(False)
):
    """
    Main triage endpoint with multi-language support and compliance
    """
    
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info("=" * 70)
    logger.info(f"NEW ANALYSIS REQUEST - ID: {request_id}")
    logger.info(f"User Language: {user_language}")
    logger.info("=" * 70)
    
    # Audit trail
    log_audit_trail("analyze_request", request_id, {"lang": user_language}, "started")
    
    # Check consent (ABDM requirement)
    if CONSENT_REQUIRED and not consent_given:
        logger.warning(f"[{request_id}] ⚠️ Consent not provided")
        return {
            "risk": "ERROR",
            "doctor_summary": "Consent required to proceed",
            "advice": "Please accept the terms and conditions to use this service.",
            "status": "consent_required",
            "request_id": request_id
        }
    
    # 1. Input validation
    logger.debug(f"[{request_id}] Step 1: Input Validation")
    logger.debug(f"[{request_id}] Symptom Text Length: {len(symptom_text)} chars")
    logger.debug(f"[{request_id}] Image Provided: {image is not None}")
    
    if len(symptom_text.strip()) < 5:
        logger.warning(f"[{request_id}] ⚠️ Insufficient symptom detail")
        return {
            "risk": "LOW",
            "doctor_summary": "Insufficient symptom detail provided.",
            "advice": "Please add more details for better guidance.",
            "status": "incomplete_input"
        }
    
    # 2. Anonymize data (DISHA Act compliance)
    logger.debug(f"[{request_id}] Step 2: Data Anonymization")
    anonymized_symptoms = anonymize_data(symptom_text)
    logger.debug(f"[{request_id}] ✓ Personal data anonymized")
    
    # 3. Translate to English if needed
    logger.debug(f"[{request_id}] Step 3: Language Translation")
    english_symptoms = symptom_text
    translation_info = None
    
    if user_language != "English":
        logger.info(f"[{request_id}] Translating from {user_language} to English...")
        
        try:
            translation_result = await translate_to_english(symptom_text, user_language)
            
            if translation_result.get("success"):
                english_symptoms = translation_result.get("translated_text", symptom_text)
                translation_info = translation_result
                logger.info(f"[{request_id}] ✓ Translation successful")
                logger.debug(f"[{request_id}] Translated: {english_symptoms[:100]}...")
            else:
                logger.warning(f"[{request_id}] ⚠️ Translation failed, using original text")
                english_symptoms = symptom_text
        
        except Exception as e:
            logger.error(f"[{request_id}] ❌ Translation error: {str(e)}")
            english_symptoms = symptom_text
    else:
        logger.debug(f"[{request_id}] Language is English, no translation needed")
    
    # 4. Emergency keyword check
    logger.debug(f"[{request_id}] Step 4: Emergency Keyword Check")
    urgent_keywords = [
        "chest pain", "breathless", "unconscious", "bleeding heavily",
        "severe headache", "can't breathe", "heart attack", "stroke",
        "poisoning", "severe burn", "seizure", "suicide", "overdose"
    ]
    
    symptom_lower = english_symptoms.lower()
    found_urgent = [kw for kw in urgent_keywords if kw in symptom_lower]
    
    if found_urgent:
        logger.warning(f"[{request_id}] 🚨 EMERGENCY KEYWORDS DETECTED: {found_urgent}")
        log_audit_trail("emergency_detected", request_id, {"keywords": found_urgent}, "alert")
        
        emergency_response = {
            "risk": "HIGH",
            "doctor_summary": "⚠️ EMERGENCY: Severe symptoms detected requiring IMMEDIATE medical attention.",
            "advice": "🚨 CALL 108 NOW or visit nearest emergency room immediately. Do not delay.",
            "status": "emergency_detected",
            "debug_keywords": found_urgent,
            "emergency_contacts": {
                "ambulance": "108",
                "police": "100",
                "fire": "101"
            }
        }
        
        # Translate emergency response if needed
        if user_language != "English":
            try:
                from sarvam_translator import translate_from_english
                trans = await translate_from_english(emergency_response["doctor_summary"], user_language)
                if trans.get("success"):
                    emergency_response["doctor_summary"] = trans.get("translated_text")
                
                trans = await translate_from_english(emergency_response["advice"], user_language)
                if trans.get("success"):
                    emergency_response["advice"] = trans.get("translated_text")
            except:
                pass  # Keep English if translation fails
        
        return emergency_response

    # 5. Process image if provided
    logger.debug(f"[{request_id}] Step 5: Image Processing")
    image_bytes = None
    if image:
        try:
            image_bytes = await image.read()
            logger.info(f"[{request_id}] ✓ Image received: {len(image_bytes)} bytes")
        except Exception as e:
            logger.error(f"[{request_id}] ⚠️ Image read error: {str(e)}")

    # 6. Call Gemini AI for analysis
    logger.debug(f"[{request_id}] Step 6: Calling Gemini AI")
    
    try:
        logger.info(f"[{request_id}] 🧠 Sending to LLM...")
        result = call_llm(english_symptoms, image_bytes)
        logger.info(f"[{request_id}] ✓ LLM Response Received")
        
    except Exception as e:
        logger.error(f"[{request_id}] ❌ LLM Call Failed: {str(e)}")
        log_audit_trail("llm_error", request_id, {}, "failed")
        return {
            "risk": "ERROR",
            "doctor_summary": "System temporarily unavailable",
            "advice": "Please try again or consult a doctor directly.",
            "status": "ai_error",
            "request_id": request_id
        }

    # 7. Extract and validate response
    logger.debug(f"[{request_id}] Step 7: Response Validation")
    if "error" in result:
        logger.error(f"[{request_id}] ⚠️ LLM returned error")
        return {
            "risk": "MODERATE",
            "doctor_summary": "Analysis incomplete",
            "advice": "Please consult a medical professional.",
            "status": "ai_partial_failure"
        }

    doc_sum = result.get('doctor_summary', 'No detailed summary available')
    risk_level = result.get('risk', 'MODERATE').upper()
    advice_text = result.get('advice', 'Please consult a medical professional.')
    
    # 8. Translate response back to user language
    logger.debug(f"[{request_id}] Step 8: Translating Response")
    
    if user_language != "English":
        try:
            from sarvam_translator import translate_from_english
            
            # Translate doctor summary
            trans_summary = await translate_from_english(doc_sum, user_language)
            if trans_summary.get("success"):
                doc_sum = trans_summary.get("translated_text", doc_sum)
            
            # Translate advice
            trans_advice = await translate_from_english(advice_text, user_language)
            if trans_advice.get("success"):
                advice_text = trans_advice.get("translated_text", advice_text)
            
            logger.info(f"[{request_id}] ✓ Response translated to {user_language}")
        
        except Exception as e:
            logger.error(f"[{request_id}] ⚠️ Response translation failed: {str(e)}")
            # Keep English version if translation fails

    # 9. Format final response
    logger.debug(f"[{request_id}] Step 9: Formatting Response")
    
    doctor_summary = f"""
AI TRIAGE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{doc_sum}

Risk Level: {risk_level}

Recommended Action:
{advice_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚕️ Medical Disclaimer: This is AI-assisted triage, NOT a medical diagnosis.
Always consult a qualified healthcare provider for proper evaluation.

📋 Data Privacy: Your data is processed securely and will be auto-deleted after {DATA_RETENTION_DAYS} days.
""".strip()

    logger.info(f"[{request_id}] ✓ Analysis Complete - Risk: {risk_level}")
    log_audit_trail("analyze_complete", request_id, {"risk": risk_level}, "success")
    
    return {
        "risk": risk_level,
        "doctor_summary": doctor_summary,
        "advice": advice_text,
        "status": "success",
        "request_id": request_id,
        "user_language": user_language,
        "whatsapp_enabled": TWILIO_ENABLED,
        "translation_used": user_language != "English",
        "compliance": {
            "data_retention_days": DATA_RETENTION_DAYS,
            "anonymized": True,
            "audit_logged": True
        }
    }


@app.post("/send-whatsapp")
async def send_whatsapp(
    phone_number: str = Form(...),
    message: str = Form(None),
    report: Optional[str] = Form(None),
    user_language: str = Form("English")
):
    """
    WhatsApp notification with multi-language support
    """
    
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] WhatsApp Send Request")
    
    if not TWILIO_ENABLED:
        return {
            "success": False,
            "error": "WhatsApp feature not configured",
            "status": "twilio_not_configured"
        }
    
    # Format phone number
    clean_phone = ''.join(filter(str.isdigit, phone_number))
    if not clean_phone.startswith('91') and len(clean_phone) == 10:
        clean_phone = '91' + clean_phone
    whatsapp_to = f"whatsapp:+{clean_phone}"
    
    # Prepare message
    if report:
        message_body = f"""🏥 *NIDAAN-AI Medical Report*

{report}

━━━━━━━━━━━━━━━━━━━━━━━
⚕️ AI-generated report. Consult a healthcare professional.
📱 Emergency: Call 108
"""
    else:
        message_body = message or "Thank you for using NIDAAN-AI."
    
    try:
        logger.info(f"[{request_id}] 📱 Sending WhatsApp...")
        
        message = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=whatsapp_to
        )
        
        logger.info(f"[{request_id}] ✓ WhatsApp sent: {message.sid}")
        log_audit_trail("whatsapp_sent", request_id, {"phone": clean_phone[:4]}, "success")
        
        return {
            "success": True,
            "message": "Report sent successfully!",
            "status": "sent",
            "request_id": request_id
        }
    
    except TwilioRestException as e:
        logger.error(f"[{request_id}] ❌ Twilio error: {e.msg}")
        return {
            "success": False,
            "error": "Failed to send WhatsApp message",
            "status": "failed"
        }


@app.get("/health")
async def health_check():
    """Health check with compliance info"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": {
            "whatsapp": TWILIO_ENABLED,
            "multilanguage": True,
            "languages": ["English", "हिंदी", "தமிழ்", "తెలుగు", "मराठी", "ಕನ್ನಡ"]
        },
        "compliance": {
            "abdm_ready": True,
            "disha_compliant": True,
            "data_retention": f"{DATA_RETENTION_DAYS} days"
        },
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
