# 🔗 Frontend-Backend Integration Test

## Quick Integration Check

### Step 1: Start Backend
```bash
# Run this in terminal
uvicorn main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
✓ API Key loaded: AIza...xyz
✓ Gemini API configured successfully
```

### Step 2: Test Backend Directly
```bash
# In another terminal or browser
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "api_version": "1.0.0",
  "endpoints": {...}
}
```

### Step 3: Open Frontend
Open `chat.html` in your browser

**Expected in Console:**
```
[INIT] CHAT INTERFACE INITIALIZED SUCCESSFULLY
```

### Step 4: Test Full Integration

1. **Select Language** (e.g., English)
   - Frontend logs: `[EVENT] ✓ Language selected: English`

2. **Enter Symptoms** (e.g., "headache and fever")
   - Type in the text box

3. **Click Send**
   
   **Frontend logs:**
   ```
   [API] NEW API REQUEST - ID: 1735123845456
   [API] Sending request to backend...
   ```
   
   **Backend logs:**
   ```
   INFO - NEW ANALYSIS REQUEST - ID: 20251225_103045_123456
   DEBUG - Step 1: Input Validation
   DEBUG - Step 2: Emergency Keyword Check
   DEBUG - Step 4: Calling Gemini AI
   INFO - ✓ Analysis Complete - Risk: MODERATE
   ```
   
   **Frontend logs:**
   ```
   [API] ✓ Response received in 2.33s
   [API] ✓ Response displayed to user
   ```

4. **See Response** in chat interface
   - Risk level with color coding
   - Doctor summary
   - Advice

## ✅ Integration Success Checklist

- [ ] Backend starts on port 8000
- [ ] Backend health check returns JSON
- [ ] Frontend loads without errors
- [ ] Language selection works
- [ ] Send button triggers API call
- [ ] Request ID appears in both logs
- [ ] Response appears in chat within 5 seconds
- [ ] No CORS errors in browser console
- [ ] No 404 or 500 errors

## 🚨 Common Integration Issues

### Issue 1: "Network Error" in Frontend
**Cause:** Backend not running
**Fix:** Start backend with `uvicorn main:app --reload`

### Issue 2: CORS Error
**Symptoms:** 
```
Access to fetch at 'http://localhost:8000/analyze' from origin 'null' 
has been blocked by CORS policy
```
**Fix:** Already configured in main.py - restart backend

### Issue 3: 404 Not Found
**Symptoms:**
```
POST http://localhost:8000/analyze 404 (Not Found)
```
**Fix:** Verify endpoint exists in main.py and backend is running

### Issue 4: Different Ports
**Symptoms:** Connection refused
**Check:** 
- Backend URL in chat.js: `http://localhost:8000/analyze`
- Backend actually running on: Check terminal output

## 📊 Integration Flow with Debug Output

```
USER ACTION: Clicks "Send"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FRONTEND (chat.js):
[EVENT] Handle send triggered
[API] NEW API REQUEST - ID: 1735123845456
[API] Request details: {text: "headache...", hasImage: false}
[API] Backend URL: http://localhost:8000/analyze
[API] Sending POST request to backend
       ↓
       ↓ HTTP POST
       ↓
BACKEND (main.py):
INFO - NEW ANALYSIS REQUEST - ID: 20251225_103045_123456
DEBUG - [ID] Step 1: Input Validation ✓
DEBUG - [ID] Step 2: Emergency Keyword Check ✓
DEBUG - [ID] Step 3: Image Processing (none)
DEBUG - [ID] Step 4: Calling Gemini AI
       ↓
       ↓ API Call
       ↓
LLM MODULE (llm.py):
INFO - LLM CALL STARTED - ID: 20251225_103046_789012
DEBUG - [ID] Prompt Length: 250 chars
DEBUG - [ID] 🧠 Sending request to Gemini...
DEBUG - [ID] ✓ Response received from Gemini
DEBUG - [ID] Response time: 1.23 seconds
DEBUG - [ID] ✓ JSON parsed successfully
       ↓
       ↓ Return
       ↓
BACKEND (main.py):
DEBUG - [ID] Step 5: Validating LLM Response ✓
DEBUG - [ID] Step 6: Extracting Response Fields ✓
DEBUG - [ID] Step 7: Risk Level Validation ✓
DEBUG - [ID] Step 8: Formatting Final Response ✓
INFO - [ID] ✓ Analysis Complete - Risk: MODERATE
       ↓
       ↓ JSON Response
       ↓
FRONTEND (chat.js):
[API] ✓ Response received in 2.33s
[API] JSON parsed successfully
[API] Risk color determined: #fbbf24 for MODERATE
[API] ✓ Response displayed to user
[MESSAGE] ✓ Bot message added to chat

USER SEES: Response in chat interface
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🔧 Manual Integration Test

If you want to test the backend independently:

```bash
# Test with curl (Windows PowerShell)
$body = @{
    symptom_text = "headache and fever"
} | ConvertTo-Json

curl -X POST http://localhost:8000/analyze `
  -H "Content-Type: application/json" `
  -d $body
```

**Expected Response:**
```json
{
  "risk": "MODERATE",
  "doctor_summary": "AI TRIAGE SUMMARY\n━━━━━━━━━━...",
  "advice": "...",
  "status": "success",
  "request_id": "20251225_103045_123456"
}
```

## ✅ Integration is Working When:

1. **Backend Terminal Shows:**
   - Server started message
   - Request received logs
   - LLM call logs
   - Response sent logs

2. **Browser Console Shows:**
   - Request sent logs
   - Response received logs
   - No error messages

3. **Chat Interface Shows:**
   - User message appears
   - Loading indicator appears
   - Bot response appears with colored risk level

4. **Timing is Reasonable:**
   - Total response time: 2-5 seconds
   - No timeouts
   - No hanging requests

## 🎉 Success!

If all the above works, your **frontend and backend are fully integrated** and communicating properly!

The debug statements I added just make it easier to see this integration happening in real-time.
