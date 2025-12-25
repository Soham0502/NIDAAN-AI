import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io
from prompts import TRIAGE_PROMPT
import logging
from datetime import datetime

# ==================== SETUP LOGGING ====================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# ==================== API KEY VALIDATION ====================
api_key = os.getenv("GOOGLE_API_KEY")
logger.info("=" * 70)
logger.info("INITIALIZING GEMINI LLM MODULE")
logger.info("=" * 70)

if not api_key:
    logger.critical("❌ GOOGLE_API_KEY not found in environment!")
    logger.critical("Please check your .env file")
    raise ValueError("GOOGLE_API_KEY is required")
else:
    logger.info(f"✓ API Key loaded: {api_key[:10]}...{api_key[-4:]}")

try:
    genai.configure(api_key=api_key)
    logger.info("✓ Gemini API configured successfully")
except Exception as e:
    logger.error(f"❌ Failed to configure Gemini API: {e}")
    raise

# Configuration to force JSON output directly from the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

logger.debug("Generation Config:")
logger.debug(f"  - Temperature: {generation_config['temperature']}")
logger.debug(f"  - Top P: {generation_config['top_p']}")
logger.debug(f"  - Top K: {generation_config['top_k']}")
logger.debug(f"  - Max Tokens: {generation_config['max_output_tokens']}")
logger.debug(f"  - Response Type: {generation_config['response_mime_type']}")

try:
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
    )
    logger.info("✓ Gemini Model Initialized: gemini-2.0-flash-exp")
except Exception as e:
    logger.error(f"❌ Failed to initialize model: {e}")
    raise

logger.info("=" * 70)


def call_llm(symptom_text: str, image_bytes: bytes = None):
    """
    Main LLM calling function with comprehensive debugging
    
    Args:
        symptom_text: Patient's symptom description
        image_bytes: Optional image data
    
    Returns:
        dict: Parsed JSON response from LLM
    """
    
    call_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info("=" * 70)
    logger.info(f"LLM CALL STARTED - ID: {call_id}")
    logger.info("=" * 70)
    
    # Step 1: Prepare prompt
    logger.debug(f"[{call_id}] Step 1: Preparing Prompt")
    prompt = f"""
    {TRIAGE_PROMPT}

    Patient Symptoms:
    {symptom_text}
    """
    
    logger.debug(f"[{call_id}] Prompt Length: {len(prompt)} chars")
    logger.debug(f"[{call_id}] Symptom Text: '{symptom_text}'")
    logger.debug(f"[{call_id}] Full Prompt Preview:\n{prompt[:200]}...")
    
    content = [prompt]
    logger.debug(f"[{call_id}] Initial content list: [prompt]")

    # Step 2: Handle image safely using PIL
    if image_bytes:
        logger.debug(f"[{call_id}] Step 2: Processing Image")
        logger.debug(f"[{call_id}] Image bytes received: {len(image_bytes)} bytes ({len(image_bytes)/1024:.2f} KB)")
        
        try:
            logger.debug(f"[{call_id}] Opening image with PIL...")
            image = Image.open(io.BytesIO(image_bytes))
            
            logger.info(f"[{call_id}] ✓ Image opened successfully")
            logger.debug(f"[{call_id}] Image Format: {image.format}")
            logger.debug(f"[{call_id}] Image Size: {image.size}")
            logger.debug(f"[{call_id}] Image Mode: {image.mode}")
            
            content.append(image)
            logger.debug(f"[{call_id}] Image added to content list")
            logger.debug(f"[{call_id}] Content list now: [prompt, image]")
            
        except Exception as e:
            logger.error(f"[{call_id}] ⚠️ Image processing failed: {str(e)}")
            logger.exception(e)
            logger.warning(f"[{call_id}] Proceeding with text-only analysis")
            # We proceed with just text if image is corrupt, rather than crashing
    else:
        logger.debug(f"[{call_id}] Step 2: No image provided - text-only analysis")

    # Step 3: Generate content
    logger.debug(f"[{call_id}] Step 3: Calling Gemini API")
    logger.debug(f"[{call_id}] Content items to send: {len(content)}")
    
    try:
        logger.info(f"[{call_id}] 🧠 Sending request to Gemini...")
        start_time = datetime.now()
        
        response = model.generate_content(content)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"[{call_id}] ✓ Response received from Gemini")
        logger.debug(f"[{call_id}] Response time: {duration:.2f} seconds")
        
        # Step 4: Parse response
        logger.debug(f"[{call_id}] Step 4: Parsing JSON Response")
        
        if not response.text:
            logger.error(f"[{call_id}] ❌ Empty response text received")
            return {
                "error": "Empty response from AI",
                "raw_error": "Response text was empty or None"
            }
        
        logger.debug(f"[{call_id}] Response text length: {len(response.text)} chars")
        logger.debug(f"[{call_id}] Raw response preview: {response.text[:200]}...")
        
        # Since we used 'response_mime_type': 'application/json', 
        # response.text is GUARANTEED to be valid JSON.
        parsed_response = json.loads(response.text)
        
        logger.info(f"[{call_id}] ✓ JSON parsed successfully")
        logger.debug(f"[{call_id}] Parsed keys: {list(parsed_response.keys())}")
        
        # Validate expected fields
        expected_fields = ['risk', 'doctor_summary', 'advice']
        missing_fields = [f for f in expected_fields if f not in parsed_response]
        
        if missing_fields:
            logger.warning(f"[{call_id}] ⚠️ Missing expected fields: {missing_fields}")
        else:
            logger.debug(f"[{call_id}] ✓ All expected fields present")
        
        # Log field contents
        logger.debug(f"[{call_id}] Response Fields:")
        for key, value in parsed_response.items():
            if isinstance(value, str):
                preview = value[:100] + "..." if len(value) > 100 else value
                logger.debug(f"[{call_id}]   - {key}: '{preview}'")
            else:
                logger.debug(f"[{call_id}]   - {key}: {value}")
        
        logger.info(f"[{call_id}] LLM CALL COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        
        return parsed_response

    except json.JSONDecodeError as e:
        logger.error(f"[{call_id}] ❌ JSON parsing failed: {str(e)}")
        logger.error(f"[{call_id}] Raw response text: {response.text}")
        logger.exception(e)
        return {
            "error": "Failed to parse AI response as JSON", 
            "raw_error": str(e),
            "raw_text": response.text[:500] if hasattr(response, 'text') else "No text"
        }
        
    except Exception as e:
        logger.error(f"[{call_id}] ❌ LLM call failed: {str(e)}")
        logger.error(f"[{call_id}] Exception type: {type(e).__name__}")
        logger.exception(e)
        
        # FAIL SAFE: Must be a DICT, not a Set
        return {
            "error": "Failed to fetch the details", 
            "raw_error": str(e),
            "exception_type": type(e).__name__
        }


# ==================== MODULE INITIALIZATION COMPLETE ====================
logger.info("LLM module loaded and ready")
