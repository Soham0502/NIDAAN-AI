# 🔍 NIDAAN-AI Debugging Guide

## Overview
This enhanced version includes comprehensive debugging statements throughout the application to help track issues and monitor performance.

---

## 📋 What Was Added

### 1. **Backend Debugging (main.py)**

#### Logging System
- **File logging**: All logs saved to `nidaan_debug.log`
- **Console logging**: Real-time output in terminal
- **Log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

#### Debug Features Added:
```python
✓ Request ID tracking (unique ID per request)
✓ Step-by-step execution logging
✓ Input validation logging
✓ Emergency keyword detection logging
✓ Image processing details
✓ LLM call monitoring
✓ Response validation
✓ Timing information
✓ Error stack traces
```

#### Example Log Output:
```
2025-12-25 10:30:45 - main - INFO - ======================================================================
2025-12-25 10:30:45 - main - INFO - NEW ANALYSIS REQUEST - ID: 20251225_103045_123456
2025-12-25 10:30:45 - main - INFO - ======================================================================
2025-12-25 10:30:45 - main - DEBUG - [20251225_103045_123456] Step 1: Input Validation
2025-12-25 10:30:45 - main - DEBUG - [20251225_103045_123456] Symptom Text Length: 45 chars
2025-12-25 10:30:45 - main - DEBUG - [20251225_103045_123456] Image Provided: True
```

### 2. **LLM Module Debugging (llm.py)**

#### Features Added:
```python
✓ API key validation logging
✓ Model initialization tracking
✓ Prompt preparation logging
✓ Image processing details (format, size, mode)
✓ API call timing
✓ JSON parsing validation
✓ Response field validation
✓ Error handling with full stack traces
```

#### Example Log Output:
```
2025-12-25 10:30:46 - llm - INFO - LLM CALL STARTED - ID: 20251225_103046_789012
2025-12-25 10:30:46 - llm - DEBUG - [20251225_103046_789012] Prompt Length: 250 chars
2025-12-25 10:30:46 - llm - DEBUG - [20251225_103046_789012] Image Format: JPEG
2025-12-25 10:30:46 - llm - DEBUG - [20251225_103046_789012] Image Size: (1920, 1080)
2025-12-25 10:30:47 - llm - INFO - [20251225_103046_789012] ✓ Response received from Gemini
2025-12-25 10:30:47 - llm - DEBUG - [20251225_103046_789012] Response time: 1.23 seconds
```

### 3. **Frontend Debugging (chat.js)**

#### Features Added:
```javascript
✓ Console logging with timestamps
✓ Category-based logging (INIT, EVENT, API, MESSAGE, UI, LANG)
✓ State tracking
✓ API request/response logging
✓ Network error detection
✓ Performance timing
✓ User interaction tracking
```

#### Example Console Output:
```
[2025-12-25T10:30:45.123Z] [INIT] NIDAAN AI CHAT INTERFACE STARTING
[2025-12-25T10:30:45.124Z] [INIT] DOM Elements loaded: {chat: true, textInput: true...}
[2025-12-25T10:30:50.456Z] [EVENT] Language button clicked: English
[2025-12-25T10:30:50.457Z] [EVENT] ✓ Language selected: English
[2025-12-25T10:30:55.789Z] [API] NEW API REQUEST - ID: 1735123855789
[2025-12-25T10:30:55.790Z] [API] Request details: {text: "headache...", hasImage: false}
```

---

## 🚀 How to Use

### 1. Start the Application

```bash
# Run the batch file
run_app.bat
```

### 2. Monitor Logs

#### Backend Logs (Terminal):
- Watch the terminal where uvicorn is running
- Logs appear in real-time
- Color-coded by severity

#### Backend Logs (File):
```bash
# View log file
type nidaan_debug.log

# Tail log file (Windows PowerShell)
Get-Content nidaan_debug.log -Wait -Tail 50
```

#### Frontend Logs (Browser):
```
1. Open browser DevTools (F12)
2. Go to Console tab
3. All frontend logs appear here
4. Filter by category: [INIT], [API], [EVENT], etc.
```

---

## 🔍 Debugging Common Issues

### Issue 1: Backend Not Starting

**Check logs for:**
```
❌ GOOGLE_API_KEY not found in environment!
```

**Solution:**
1. Verify `.env` file exists
2. Check `GOOGLE_API_KEY` is set correctly
3. Restart the backend

**Expected logs:**
```
✓ API Key loaded: AIzaSyAbc...xyz
✓ Gemini API configured successfully
✓ Gemini Model Initialized: gemini-2.0-flash-exp
```

---

### Issue 2: Frontend Can't Connect

**Check browser console for:**
```
[API] ❌ Network error - backend may not be running
```

**Solution:**
1. Verify backend is running on http://localhost:8000
2. Check `/health` endpoint: http://localhost:8000/health
3. Look for CORS errors in browser console

**Expected logs:**
```
[API] Backend URL: http://localhost:8000/analyze
[API] ✓ Response received in 2.45s
```

---

### Issue 3: Image Upload Fails

**Check backend logs for:**
```
[REQUEST_ID] ⚠️ Image read error: [error details]
```

**Check frontend logs for:**
```
[EVENT] ✓ Image stored as pending {name: "photo.jpg", size: "234.5 KB"}
```

**Solution:**
1. Verify image format (JPEG, PNG)
2. Check image size (< 5MB recommended)
3. Look for PIL image processing errors

---

### Issue 4: LLM Returns Error

**Check backend logs for:**
```
[REQUEST_ID] ❌ LLM call failed: [error details]
[REQUEST_ID] Exception type: GoogleAPIError
```

**Common causes:**
- Invalid API key
- Rate limiting
- Network issues
- Malformed prompt

**Expected logs:**
```
[REQUEST_ID] 🧠 Sending request to Gemini...
[REQUEST_ID] ✓ Response received from Gemini
[REQUEST_ID] ✓ JSON parsed successfully
```

---

### Issue 5: Empty or Invalid Response

**Check logs for:**
```
[REQUEST_ID] ⚠️ Missing expected fields: ['advice']
[REQUEST_ID] ❌ JSON parsing failed: [error]
```

**Solution:**
1. Check prompt structure in `prompts.py`
2. Verify `response_mime_type` is set to "application/json"
3. Look for raw response text in logs

---

## 📊 Log Analysis

### Request Flow Timeline

```
1. Frontend: User clicks send
   [EVENT] Handle send triggered
   
2. Frontend: API call initiated
   [API] NEW API REQUEST - ID: xxx
   
3. Backend: Request received
   [main] NEW ANALYSIS REQUEST - ID: xxx
   
4. Backend: LLM processing
   [llm] LLM CALL STARTED - ID: xxx
   
5. Backend: Response generated
   [llm] LLM CALL COMPLETED SUCCESSFULLY
   
6. Backend: Response formatted
   [main] ✓ Analysis Complete - Risk: MODERATE
   
7. Frontend: Response displayed
   [API] ✓ Response displayed to user
```

### Performance Metrics

**Look for these timing logs:**
```python
# Backend
Response time: 1.23 seconds

# Frontend
✓ Response received in 2.45s
```

---

## 🛠️ Advanced Debugging

### Enable Verbose Logging

**In llm.py:**
```python
# Change to DEBUG level
logging.basicConfig(level=logging.DEBUG)
```

### Filter Logs by Category

**Browser Console:**
```javascript
// Filter by category
console.filter = (category) => {
  // Returns only logs matching category
}
```

### Export Logs

**Backend:**
```bash
# Copy log file
copy nidaan_debug.log nidaan_debug_backup_2025-12-25.log
```

**Browser:**
```
Right-click in Console → Save as...
```

---

## 📝 Debug Information in API Responses

All API responses now include debug information:

```json
{
  "risk": "MODERATE",
  "doctor_summary": "...",
  "advice": "...",
  "status": "success",
  "request_id": "20251225_103045_123456",
  "debug_info": {
    "symptom_length": 45,
    "image_provided": true,
    "image_size_kb": 234.5
  }
}
```

---

## 🎯 Key Debugging Points

### Backend Entry Points:
1. `/analyze` - Main triage endpoint
2. `/send-whatsapp` - WhatsApp notification
3. `/translate` - Hindi translation
4. `/health` - Health check

### Frontend Entry Points:
1. Language selection click
2. Image upload change
3. Text input change
4. Send button click
5. API fetch call

### LLM Processing:
1. Prompt preparation
2. Image processing (if provided)
3. Content generation
4. JSON parsing
5. Response validation

---

## 🐛 Common Error Patterns

### Pattern 1: API Key Issues
```
CRITICAL - ❌ GOOGLE_API_KEY not found in environment!
```
**Fix:** Check `.env` file

### Pattern 2: Network Issues
```
[API] ❌ Network error - backend may not be running
```
**Fix:** Start backend server

### Pattern 3: Image Processing Issues
```
[llm] ⚠️ Image processing failed: cannot identify image file
```
**Fix:** Use supported image formats

### Pattern 4: JSON Parsing Issues
```
[llm] ❌ JSON parsing failed: Expecting value
```
**Fix:** Check model configuration

---

## 📞 Support

For issues not covered here:
1. Check `nidaan_debug.log` for backend errors
2. Check browser console for frontend errors
3. Look for request IDs to trace specific requests
4. Compare timing logs to identify bottlenecks

---

## ✅ Health Check

**Verify everything is working:**

```bash
# 1. Check backend health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "api_version": "1.0.0",
  "timestamp": "2025-12-25T10:30:45.123456"
}

# 2. Check frontend loading
# Open browser console and look for:
[INIT] CHAT INTERFACE INITIALIZED SUCCESSFULLY
```

---

## 🎉 Success Indicators

**Backend running correctly:**
```
✓ API Key loaded
✓ Gemini API configured successfully
✓ Gemini Model Initialized
```

**Frontend running correctly:**
```
[INIT] NIDAAN AI CHAT INTERFACE STARTING
[INIT] DOM Elements loaded: {all true}
[INIT] CHAT INTERFACE INITIALIZED SUCCESSFULLY
```

**Successful analysis:**
```
[REQUEST_ID] ✓ Analysis Complete - Risk: MODERATE
[API] ✓ Response displayed to user
```

---

## 📌 Quick Reference

| Component | Log Location | Key Indicators |
|-----------|-------------|----------------|
| Backend | `nidaan_debug.log` + Console | Request IDs, Step numbers |
| Frontend | Browser Console | Timestamps, Categories |
| LLM | Backend logs | API calls, Timings |
| API | Both locations | Request/Response IDs |

---

**Remember:** Always check logs when something doesn't work as expected!
