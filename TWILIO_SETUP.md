# 📱 Twilio WhatsApp Setup Guide

## Step 1: Create Twilio Account

1. Go to: https://www.twilio.com/try-twilio
2. Sign up for a FREE account
3. Verify your email and phone number

## Step 2: Get Your Twilio Credentials

After login, you'll see your **Dashboard**:

1. **Account SID** - Copy this (looks like: ACxxxxxxxxxxxxxxxxxxxxx)
2. **Auth Token** - Click to reveal and copy

## Step 3: Set Up WhatsApp Sandbox

### For Testing (Free - Sandbox):

1. Go to: **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Or direct link: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn

3. You'll see instructions like:
   ```
   Join the sandbox by sending:
   "join <code>" to +14155238886
   ```

4. **On your phone:**
   - Open WhatsApp
   - Send message to: **+1 415 523 8886**
   - Text: `join <your-code>` (e.g., `join happy-tiger`)

5. You'll receive: "Sandbox Joined!"

### For Production (Requires approval):

1. Go to: **Messaging** → **Senders** → **WhatsApp senders**
2. Click "Add new sender"
3. Follow approval process (can take 1-2 weeks)

## Step 4: Get Your WhatsApp Number

**Sandbox (for testing):**
- Number: `+14155238886`
- Format: `whatsapp:+14155238886`

**Production:**
- Your approved business number
- Format: `whatsapp:+<your_number>`

## Step 5: Add to .env File

Add these to your `.env` file:

```env
# Existing
GOOGLE_API_KEY=your_google_api_key

# New - Add these Twilio credentials
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

**Important:** 
- Don't share these credentials
- Don't commit .env to git
- Keep them secret!

## Step 6: Install Twilio Python Package

```bash
pip install twilio
```

Or update your `requirements.txt`:
```
fastapi
uvicorn[standard]
google-generativeai
python-dotenv
pillow
python-multipart
twilio
```

Then run:
```bash
pip install -r requirements.txt
```

## 🔍 Verify Setup

### Test 1: Check Credentials
```python
# test_twilio.py
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

print(f"Account SID: {account_sid[:10]}...")
print(f"Auth Token: {auth_token[:10]}...")

client = Client(account_sid, auth_token)
print("✓ Twilio client created successfully!")
```

### Test 2: Send Test Message
```python
# send_test.py
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

message = client.messages.create(
    from_='whatsapp:+14155238886',
    body='Hello from Nidaan AI! 🏥',
    to='whatsapp:+919876543210'  # Replace with your WhatsApp number
)

print(f"Message sent! SID: {message.sid}")
```

## 📱 Phone Number Format

**Important:** Use international format with country code

**India:** 
- ❌ Wrong: 9876543210
- ✅ Correct: +919876543210
- ✅ With prefix: whatsapp:+919876543210

**USA:**
- ✅ Correct: +14155551234
- ✅ With prefix: whatsapp:+14155551234

## 🚨 Common Issues

### Issue 1: "Unable to create record"
**Cause:** Phone not joined to sandbox
**Fix:** Send "join <code>" message first

### Issue 2: "Authenticate"
**Cause:** Wrong credentials
**Fix:** Check Account SID and Auth Token

### Issue 3: "Invalid phone number"
**Cause:** Wrong format
**Fix:** Use +[country code][number] format

### Issue 4: "To number not in sandbox"
**Cause:** For sandbox, recipient must join first
**Fix:** Have recipient send "join <code>" message

## 💡 Sandbox Limitations

**Sandbox (Free):**
- ✅ Good for testing
- ❌ Recipient must join sandbox first
- ❌ Limited to pre-approved numbers
- ❌ Twilio branding in messages

**Production (Approved):**
- ✅ Send to anyone
- ✅ Your own branding
- ✅ Custom sender ID
- 💰 Pay per message (~$0.005 per message)

## ✅ Ready Checklist

- [ ] Twilio account created
- [ ] Account SID copied
- [ ] Auth Token copied
- [ ] WhatsApp sandbox joined
- [ ] Phone number verified
- [ ] Credentials added to .env
- [ ] Twilio package installed
- [ ] Test message sent successfully

## 🎯 Next Steps

Once setup is complete:
1. Use the enhanced main.py I'll provide
2. Test with the frontend
3. Send triage reports via WhatsApp!

---

**Need Help?**
- Twilio Docs: https://www.twilio.com/docs/whatsapp
- Support: https://support.twilio.com
