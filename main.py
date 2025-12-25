from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from llm import call_llm
import httpx
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

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
    description="AI-powered medical triage system for rural India",
    version="1.0.0"
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

@app.get("/")
async def root():
    """Health check endpoint"""
    logger.debug("Root endpoint accessed")
    return {
        "status": "healthy",
        "service": "NIDAAN-AI Triage API",
        "version": "1.0.0"
    }

@app.post("/analyze")
async def analyze(
    symptom_text: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    """
    Main triage endpoint
    Accepts: symptom text + optional image
    Returns: Risk level, doctor summary, and advice
    """
    
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info("=" * 70)
    logger.info(f"NEW ANALYSIS REQUEST - ID: {request_id}")
    logger.info("=" * 70)
    
    # 1. Input validation
    logger.debug(f"[{request_id}] Step 1: Input Validation")
    logger.debug(f"[{request_id}] Symptom Text Length: {len(symptom_text)} chars")
    logger.debug(f"[{request_id}] Symptom Text Preview: {symptom_text[:100]}...")
    logger.debug(f"[{request_id}] Image Provided: {image is not None}")
    
    if len(symptom_text.strip()) < 5:
        logger.warning(f"[{request_id}] ⚠️ Insufficient symptom detail (less than 5 chars)")
        return {
            "risk": "LOW",
            "doctor_summary": "Insufficient symptom detail provided.",
            "advice": "Please add more details for better guidance.",
            "status": "incomplete_input"
        }
    
    # 2. Quick keyword check for emergency cases (fast fail)
    logger.debug(f"[{request_id}] Step 2: Emergency Keyword Check")
    urgent_keywords = [
        "chest pain", "breathless", "unconscious", "bleeding heavily",
        "severe headache", "can't breathe", "heart attack", "stroke",
        "poisoning", "severe burn", "seizure"
    ]
    
    symptom_lower = symptom_text.lower()
    found_urgent = [kw for kw in urgent_keywords if kw in symptom_lower]
    
    if found_urgent:
        logger.warning(f"[{request_id}] 🚨 EMERGENCY KEYWORDS DETECTED: {found_urgent}")
        return {
            "risk": "HIGH",
            "doctor_summary": "⚠️ Severe symptoms detected requiring urgent attention.",
            "advice": "🚨 IMMEDIATE ACTION: Seek emergency care NOW. Call 108 or visit nearest hospital immediately.",
            "status": "emergency_detected",
            "debug_keywords": found_urgent
        }
    else:
        logger.debug(f"[{request_id}] ✓ No emergency keywords found")

    # 3. Process image if provided
    logger.debug(f"[{request_id}] Step 3: Image Processing")
    image_bytes = None
    if image:
        try:
            logger.debug(f"[{request_id}] Reading image file...")
            logger.debug(f"[{request_id}] Image filename: {image.filename}")
            logger.debug(f"[{request_id}] Image content_type: {image.content_type}")
            
            image_bytes = await image.read()
            logger.info(f"[{request_id}] ✓ Image received: {len(image_bytes)} bytes ({len(image_bytes)/1024:.2f} KB)")
            
        except Exception as e:
            logger.error(f"[{request_id}] ⚠️ Image read error: {str(e)}")
            logger.exception(e)
    else:
        logger.debug(f"[{request_id}] No image provided - text-only analysis")

    # 4. Call Gemini AI for analysis
    logger.debug(f"[{request_id}] Step 4: Calling Gemini AI")
    logger.debug(f"[{request_id}] Preparing LLM call...")
    
    try:
        logger.info(f"[{request_id}] 🧠 Sending to LLM...")
        result = call_llm(symptom_text, image_bytes)
        logger.info(f"[{request_id}] ✓ LLM Response Received")
        logger.debug(f"[{request_id}] Raw LLM Result: {result}")
        
    except Exception as e:
        logger.error(f"[{request_id}] ❌ LLM Call Failed: {str(e)}")
        logger.exception(e)
        return {
            "risk": "ERROR",
            "doctor_summary": "System temporarily unavailable",
            "advice": "Please try again or consult a doctor directly.",
            "debug": str(e),
            "status": "ai_error",
            "request_id": request_id
        }

    # 5. Check if AI returned error
    logger.debug(f"[{request_id}] Step 5: Validating LLM Response")
    if "error" in result:
        logger.error(f"[{request_id}] ⚠️ LLM returned error: {result.get('error')}")
        logger.debug(f"[{request_id}] Raw error: {result.get('raw_error')}")
        return {
            "risk": "MODERATE",  # Safe fallback
            "doctor_summary": f"Analysis incomplete: {result.get('error', 'Unknown error')}",
            "advice": "Please consult a medical professional for proper evaluation.",
            "debug": result.get("raw_error"),
            "status": "ai_partial_failure",
            "request_id": request_id
        }

    # 6. Safe variable extraction with defaults
    logger.debug(f"[{request_id}] Step 6: Extracting Response Fields")
    doc_sum = result.get('doctor_summary', 'No detailed summary available')
    risk_level = result.get('risk', 'MODERATE').upper()
    advice_text = result.get('advice', 'Please consult a medical professional.')
    
    logger.debug(f"[{request_id}] Extracted Risk Level: {risk_level}")
    logger.debug(f"[{request_id}] Summary Length: {len(doc_sum)} chars")
    logger.debug(f"[{request_id}] Advice Length: {len(advice_text)} chars")

    # 7. Validate risk level
    logger.debug(f"[{request_id}] Step 7: Risk Level Validation")
    valid_risks = ["LOW", "MODERATE", "HIGH"]
    if risk_level not in valid_risks:
        logger.warning(f"[{request_id}] ⚠️ Invalid risk level '{risk_level}', defaulting to MODERATE")
        risk_level = "MODERATE"
    else:
        logger.debug(f"[{request_id}] ✓ Valid risk level: {risk_level}")

    # 8. Construct formatted doctor summary
    logger.debug(f"[{request_id}] Step 8: Formatting Final Response")
    doctor_summary = f"""
AI TRIAGE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Symptoms Analysis: {doc_sum}

Risk Level: {risk_level}

Recommended Action:
{advice_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚕️ Note: This is AI-assisted triage, not a medical diagnosis.
For definitive care, please consult a qualified healthcare provider.
""".strip()

    logger.info(f"[{request_id}] ✓ Analysis Complete - Risk: {risk_level}")
    logger.info(f"[{request_id}] " + "=" * 70)
    
    return {
        "risk": risk_level,
        "doctor_summary": doctor_summary,
        "advice": advice_text,
        "status": "success",
        "request_id": request_id,
        "debug_info": {
            "symptom_length": len(symptom_text),
            "image_provided": image is not None,
            "image_size_kb": round(len(image_bytes)/1024, 2) if image_bytes else 0
        }
    }


@app.post("/send-whatsapp")
async def send_whatsapp(
    phone_number: str = Form(...),
    message: str = Form(...),
    report: Optional[str] = Form(None)
):
    """
    WhatsApp notification endpoint (Twilio integration ready)
    For MVP: Returns success without actual sending
    """
    
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] WhatsApp Send Request")
    logger.debug(f"[{request_id}] Phone: {phone_number}")
    logger.debug(f"[{request_id}] Message Length: {len(message)} chars")
    logger.debug(f"[{request_id}] Report Attached: {report is not None}")
    
    # For production: Integrate with Twilio
    # TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    # TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    # TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
    
    logger.warning(f"[{request_id}] ⚠️ WhatsApp send simulated (demo mode)")
    
    # Simulate WhatsApp send for demo
    return {
        "success": True,
        "message": "WhatsApp notification queued",
        "recipient": phone_number,
        "note": "Webhook-ready for Twilio integration",
        "status": "demo_mode",
        "request_id": request_id
    }


@app.post("/translate")
async def translate_to_hindi(text: str = Form(...)):
    """
    Optional: Translate medical advice to Hindi using external API
    Uses httpx for async HTTP requests
    """
    
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] Translation Request")
    logger.debug(f"[{request_id}] Text to translate: {text[:100]}...")
    
    # Example: Google Translate API or custom translation service
    translate_api_url = "https://translation.googleapis.com/language/translate/v2"
    
    try:
        logger.debug(f"[{request_id}] Calling Google Translate API...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                translate_api_url,
                params={
                    "key": os.getenv("GOOGLE_TRANSLATE_API_KEY", ""),
                    "q": text,
                    "target": "hi",
                    "format": "text"
                },
                timeout=10.0
            )
            
            logger.debug(f"[{request_id}] Translation API Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                translated_text = data['data']['translations'][0]['translatedText']
                logger.info(f"[{request_id}] ✓ Translation successful")
                return {
                    "success": True,
                    "original": text,
                    "translated": translated_text,
                    "language": "hindi",
                    "request_id": request_id
                }
            else:
                logger.warning(f"[{request_id}] Translation API error: {response.status_code}")
                return {
                    "success": False,
                    "error": "Translation service unavailable",
                    "original": text,
                    "request_id": request_id
                }
                
    except Exception as e:
        logger.error(f"[{request_id}] Translation failed: {str(e)}")
        logger.exception(e)
        return {
            "success": False,
            "error": str(e),
            "original": text,
            "note": "Fallback to original text",
            "request_id": request_id
        }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    logger.debug("Health check endpoint accessed")
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze",
            "whatsapp": "/send-whatsapp",
            "translate": "/translate"
        },
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
