# 🏥 NIDAAN-AI Medical Triage System (Debug Enhanced)

## 📋 Overview

This is your enhanced NIDAAN-AI medical triage system with comprehensive debugging capabilities integrated throughout the codebase.

**What's New:**
- ✅ Full logging system in backend (Python)
- ✅ Console debugging in frontend (JavaScript)
- ✅ Request tracking with unique IDs
- ✅ Performance monitoring
- ✅ Error tracing with stack traces
- ✅ Step-by-step execution logging

---

## 📦 Package Contents

### Core Files (Enhanced with Debugging)
```
main.py              - Backend API with comprehensive logging
llm.py               - Gemini AI integration with debug tracking
chat.js              - Frontend with console debugging
```

### Supporting Files (Unchanged)
```
chat.html            - Chat interface HTML
chat.css             - Chat interface styles
index.html           - Landing page
styles.css           - Landing page styles
main.js              - Landing page animations
prompts.py           - AI prompt templates
requirements.txt     - Python dependencies
run_app.bat          - Startup script
.env                 - Environment variables (you need to create/update)
```

### Documentation (New)
```
DEBUGGING_GUIDE.md   - Complete debugging guide
CHANGES_SUMMARY.md   - Summary of all changes
QUICK_REFERENCE.md   - Quick reference card
README.md            - This file
```

---

## 🚀 Quick Start

### 1. Setup Environment

**Create/Update `.env` file:**
```env
GOOGLE_API_KEY=your_actual_api_key_here
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

### 2. Start Application

```bash
# Simply run this
run_app.bat
```

This will:
1. Start the backend server (http://localhost:8000)
2. Wait 5 seconds for startup
3. Open the frontend in your browser

### 3. Monitor Logs

**Backend:**
- Watch the terminal window
- Check `nidaan_debug.log` file

**Frontend:**
- Press F12 in browser
- Open Console tab

---

## 🔍 New Debugging Features

### Backend (Python)

**Logging System:**
```python
- File: nidaan_debug.log (persistent)
- Console: Real-time output
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**What's Logged:**
- ✅ Request IDs for tracking
- ✅ Step-by-step execution (8 steps per request)
- ✅ Input validation details
- ✅ Image processing information
- ✅ LLM call timing (seconds)
- ✅ Response validation
- ✅ Error details with stack traces

**Example Output:**
```
2025-12-25 10:30:45 - main - INFO - NEW ANALYSIS REQUEST - ID: 20251225_103045_123456
2025-12-25 10:30:45 - main - DEBUG - [20251225_103045_123456] Step 1: Input Validation
2025-12-25 10:30:45 - main - DEBUG - [20251225_103045_123456] Symptom Text Length: 45 chars
2025-12-25 10:30:46 - llm - INFO - [20251225_103046_789012] ✓ Response received from Gemini
2025-12-25 10:30:46 - llm - DEBUG - [20251225_103046_789012] Response time: 1.23 seconds
```

### Frontend (JavaScript)

**Console Logging:**
```javascript
- Timestamps: ISO 8601 format
- Categories: INIT, EVENT, API, MESSAGE, UI, LANG, INPUT
- Structured data: Objects and arrays
```

**What's Logged:**
- ✅ Initialization steps
- ✅ User interactions (clicks, inputs)
- ✅ API requests/responses
- ✅ State changes
- ✅ Performance timing
- ✅ Error details

**Example Output:**
```
[2025-12-25T10:30:40.000Z] [INIT] NIDAAN AI CHAT INTERFACE STARTING
[2025-12-25T10:30:43.123Z] [EVENT] Language button clicked: English
[2025-12-25T10:30:45.456Z] [API] NEW API REQUEST - ID: 1735123845456
[2025-12-25T10:30:47.789Z] [API] ✓ Response received in 2.33s
```

---

## 🎯 How to Use for Debugging

### Scenario 1: Backend Won't Start

**Check terminal for:**
```
❌ GOOGLE_API_KEY not found in environment!
```

**Solution:**
1. Create/update `.env` file
2. Add: `GOOGLE_API_KEY=your_key_here`
3. Restart application

**Expected Success:**
```
✓ API Key loaded: AIza...xyz
✓ Gemini API configured successfully
✓ Gemini Model Initialized: gemini-2.0-flash-exp
```

---

### Scenario 2: Frontend Can't Connect

**Check browser console for:**
```
[API] ❌ Network error - backend may not be running
```

**Solution:**
1. Verify backend is running
2. Check http://localhost:8000/health
3. Look for CORS errors

**Expected Success:**
```
[API] Backend URL: http://localhost:8000/analyze
[API] ✓ Response received in 2.45s
```

---

### Scenario 3: Tracking a Specific Request

**Step 1: Note the Request ID from frontend**
```
[API] NEW API REQUEST - ID: 1735123845456
```

**Step 2: Search backend logs for matching ID**
```
[main] NEW ANALYSIS REQUEST - ID: 20251225_103045_123456
```

**Step 3: Follow the execution flow**
```
Step 1: Input Validation ✓
Step 2: Emergency Keyword Check ✓
Step 3: Image Processing ✓
Step 4: Calling Gemini AI ✓
...
```

---

## 📊 Performance Monitoring

**Expected Response Times:**
```
✓ Language selection:  < 100ms
✓ Image upload:        < 500ms
✓ API call (text):     1-3 seconds
✓ API call (image):    2-5 seconds
✓ UI render:           < 100ms
```

**Check logs for timing:**
```python
# Backend
Response time: 1.23 seconds

# Frontend
✓ Response received in 2.33s
```

---

## 🔍 Common Issues & Solutions

### Issue 1: API Key Error
```
ERROR: GOOGLE_API_KEY not found
```
**Fix:** Update `.env` file with valid API key

### Issue 2: Port Already in Use
```
ERROR: Address already in use
```
**Fix:** Close other apps using port 8000

### Issue 3: Image Upload Fails
```
WARNING: Image processing failed
```
**Fix:** Use JPEG/PNG format, check file size < 5MB

### Issue 4: Slow Response
```
Response time: 8.45 seconds
```
**Fix:** Check network, API rate limits, image size

### Issue 5: JSON Parsing Error
```
ERROR: JSON parsing failed
```
**Fix:** Verify model configuration, check API response format

---

## 📚 Documentation

**Read these for detailed information:**

1. **DEBUGGING_GUIDE.md**
   - Complete debugging guide
   - Error patterns and solutions
   - Step-by-step troubleshooting

2. **CHANGES_SUMMARY.md**
   - All changes made
   - File-by-file breakdown
   - Debug feature details

3. **QUICK_REFERENCE.md**
   - Quick reference card
   - Common commands
   - Success indicators

---

## ✅ Health Check

**Verify everything is working:**

```bash
# 1. Check backend
curl http://localhost:8000/health
# Expected: {"status": "healthy", "api_version": "1.0.0"}

# 2. Check frontend
# Open browser console and look for:
# [INIT] CHAT INTERFACE INITIALIZED SUCCESSFULLY

# 3. Test end-to-end
# - Select language
# - Enter symptoms
# - Check both consoles for matching request IDs
```

---

## 🎯 Testing Checklist

Before reporting issues, verify:

- [ ] Backend starts without errors
- [ ] API key is correctly set in `.env`
- [ ] Port 8000 is available
- [ ] Frontend loads in browser
- [ ] Console shows initialization complete
- [ ] Language selection works
- [ ] Text input enabled after language
- [ ] Send button works
- [ ] Response appears in chat
- [ ] Request IDs match in both logs
- [ ] No error messages in logs

---

## 📝 API Endpoints

```
GET  /              - Root endpoint (health check)
GET  /health        - Detailed health check
POST /analyze       - Main triage analysis
POST /send-whatsapp - WhatsApp notification (demo)
POST /translate     - Hindi translation (optional)
```

---

## 🔐 Security Notes

**What's logged:**
- ✅ Request IDs
- ✅ Timestamps
- ✅ File sizes
- ✅ Error messages

**What's NOT logged:**
- ❌ Full API keys (masked)
- ❌ Personal health information (by default)
- ❌ Passwords
- ❌ Authentication tokens

**API Key Masking:**
```
Original: AIzaSyAbc123...xyz789
Logged:   AIzaSy...789
```

---

## 🛠️ Development Tips

### Enable Verbose Logging
```python
# In main.py or llm.py
logging.basicConfig(level=logging.DEBUG)
```

### Filter Browser Logs
```javascript
// In browser console
console.filter("API")  // Show only API logs
console.filter("❌")    // Show only errors
```

### Export Logs
```bash
# Backend
copy nidaan_debug.log backup_2025-12-25.log

# Frontend
# Right-click in Console → Save as...
```

---

## 🎉 Success Indicators

**Backend Terminal:**
```
✓ API Key loaded
✓ Gemini API configured successfully
✓ Gemini Model Initialized
```

**Browser Console:**
```
[INIT] CHAT INTERFACE INITIALIZED SUCCESSFULLY
```

**Successful Request:**
```
Backend:  ✓ Analysis Complete - Risk: MODERATE
Frontend: ✓ Response displayed to user
```

---

## 📞 Support

**For issues:**
1. Check `nidaan_debug.log` for backend errors
2. Check browser console for frontend errors
3. Look for request IDs to trace specific requests
4. Compare timing logs to identify bottlenecks
5. Refer to `DEBUGGING_GUIDE.md` for detailed help

---

## 🚀 Next Steps

1. **Test the enhanced version**
   - Run through various scenarios
   - Monitor both consoles
   - Verify all features work

2. **Customize for your needs**
   - Adjust log levels
   - Add custom categories
   - Filter relevant logs

3. **Prepare for production**
   - Set log level to WARNING
   - Configure log rotation
   - Set up monitoring alerts

---

## 📦 File Structure

```
nidaan-ai/
├── main.py                  # Backend API (enhanced)
├── llm.py                   # LLM module (enhanced)
├── prompts.py               # AI prompts
├── requirements.txt         # Dependencies
├── .env                     # Environment variables
├── run_app.bat              # Startup script
├── nidaan_debug.log         # Log file (created on run)
├── chat.html                # Chat interface
├── chat.css                 # Chat styles
├── chat.js                  # Chat logic (enhanced)
├── index.html               # Landing page
├── styles.css               # Landing styles
├── main.js                  # Landing animations
├── README.md                # This file
├── DEBUGGING_GUIDE.md       # Complete guide
├── CHANGES_SUMMARY.md       # All changes
└── QUICK_REFERENCE.md       # Quick reference
```

---

## 💡 Pro Tips

1. **Keep both consoles open** during development
2. **Match request IDs** across systems
3. **Check timing logs** for performance issues
4. **Export logs** before closing for later analysis
5. **Test with and without images** separately
6. **Use health check** to verify backend status
7. **Read DEBUGGING_GUIDE.md** for detailed info

---

**Version:** 1.0.0 with Debug Integration
**Last Updated:** December 25, 2025
**Status:** Ready for Testing ✅

---

## 🎊 What's Different from Original?

**Original Code:**
- ❌ No logging system
- ❌ No request tracking
- ❌ No performance monitoring
- ❌ Basic error messages
- ❌ Hard to debug issues

**Enhanced Code:**
- ✅ Comprehensive logging
- ✅ Unique request IDs
- ✅ Performance timing
- ✅ Detailed error traces
- ✅ Easy to track issues
- ✅ No breaking changes
- ✅ All original features intact

---

**Happy Debugging! 🎉**

For questions or issues, refer to the documentation files or check the logs.
