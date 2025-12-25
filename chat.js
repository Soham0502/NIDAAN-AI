/* ================= ELEMENTS ================= */
const chat = document.getElementById("chatWrapper");
const textInput = document.getElementById("textInput");
const sendBtn = document.getElementById("sendBtn");
const imageInput = document.getElementById("imageInput");
const micBtn = document.getElementById("micBtn");

/* ================= STATE ================= */
let selectedLanguage = null;
let pendingImage = null; // Store image until text is sent

textInput.disabled = true; 
sendBtn.disabled = true;

/* ================= DEBUGGING HELPERS ================= */
function debugLog(category, message, data = null) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${category}] ${message}`;
  
  console.log(logMessage);
  
  if (data) {
    console.log(`[${timestamp}] [${category}] Data:`, data);
  }
}

function debugError(category, message, error = null) {
  const timestamp = new Date().toISOString();
  console.error(`[${timestamp}] [${category}] ❌ ${message}`);
  
  if (error) {
    console.error(`[${timestamp}] [${category}] Error details:`, error);
    if (error.stack) {
      console.error(`[${timestamp}] [${category}] Stack trace:`, error.stack);
    }
  }
}

/* ================= INITIALIZATION ================= */
debugLog('INIT', '='.repeat(70));
debugLog('INIT', 'NIDAAN AI CHAT INTERFACE STARTING');
debugLog('INIT', '='.repeat(70));
debugLog('INIT', 'DOM Elements loaded:', {
  chat: !!chat,
  textInput: !!textInput,
  sendBtn: !!sendBtn,
  imageInput: !!imageInput,
  micBtn: !!micBtn
});
debugLog('INIT', 'Initial state:', {
  selectedLanguage,
  pendingImage,
  textInputDisabled: textInput.disabled,
  sendBtnDisabled: sendBtn.disabled
});

/* ================= TIME ================= */
function timeNow() {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

/* ================= SCROLL ================= */
function scrollBottom() {
  setTimeout(() => {
    chat.scrollTop = chat.scrollHeight;
    debugLog('UI', `Scrolled to bottom: ${chat.scrollTop}px`);
  }, 100);
}

/* ================= MESSAGE HELPERS ================= */
function addUserMessage(html) {
  debugLog('MESSAGE', 'Adding user message', { htmlLength: html.length });
  
  const div = document.createElement('div');
  div.className = 'message user';
  div.innerHTML = `
      <div class="content">
        <div class="bubble">${html}</div>
        <span class="time">${timeNow()}</span>
      </div>
      <div class="avatar user">👤</div>
  `;
  chat.appendChild(div);
  scrollBottom();
  
  debugLog('MESSAGE', '✓ User message added to chat');
}

function addBotMessage(html) {
  debugLog('MESSAGE', 'Adding bot message', { htmlLength: html.length });
  
  const div = document.createElement('div');
  div.className = 'message ai';
  div.innerHTML = `
      <div class="avatar bot">🤖</div>
      <div class="content">
        <div class="bubble">${html}</div>
        <span class="time">${timeNow()}</span>
      </div>
  `;
  chat.appendChild(div);
  scrollBottom();
  
  debugLog('MESSAGE', '✓ Bot message added to chat');
  return div; // Return element so we can remove it if needed (e.g. loading state)
}

function showLoading() {
  const id = "loading-" + Date.now();
  debugLog('UI', `Showing loading indicator: ${id}`);
  
  const div = document.createElement('div');
  div.className = 'message ai';
  div.id = id;
  div.innerHTML = `
      <div class="avatar bot">🤖</div>
      <div class="content">
        <div class="bubble">Analyzing symptoms... 🩺</div>
      </div>
  `;
  chat.appendChild(div);
  scrollBottom();
  
  debugLog('UI', `✓ Loading indicator shown: ${id}`);
  return id;
}

function removeLoading(id) {
  debugLog('UI', `Removing loading indicator: ${id}`);
  const el = document.getElementById(id);
  if (el) {
    el.remove();
    debugLog('UI', '✓ Loading indicator removed');
  } else {
    debugLog('UI', '⚠️ Loading indicator not found');
  }
}

/* ================= BOT TEXT TRANSLATIONS ================= */
function getBotText(type) {
  debugLog('LANG', `Getting bot text for type: ${type}, language: ${selectedLanguage}`);
  
  const data = {
    English: {
      languageSelected: "Great 👍 You can now describe your symptoms or upload an image.",
      error: "⚠️ Connection error. Is the backend running?",
    },
    हिंदी: {
      languageSelected: "बहुत बढ़िया 👍 अब आप अपने लक्षण बताइए या कोई तस्वीर अपलोड करें।",
      error: "⚠️ संपर्क त्रुटि। क्या सर्वर चल रहा है?",
    },
    // Add other languages as needed...
  };
  
  const text = data[selectedLanguage]?.[type] || data.English[type];
  debugLog('LANG', `✓ Bot text retrieved: ${text.substring(0, 50)}...`);
  return text;
}

/* ================= API CALL (THE INTEGRATION) ================= */
async function sendToBackend(text, imageFile) {
  const requestId = Date.now();
  debugLog('API', '='.repeat(70));
  debugLog('API', `NEW API REQUEST - ID: ${requestId}`);
  debugLog('API', '='.repeat(70));
  debugLog('API', 'Request details:', {
    text: text.substring(0, 100) + '...',
    textLength: text.length,
    hasImage: !!imageFile,
    imageSize: imageFile ? `${(imageFile.size / 1024).toFixed(2)} KB` : 'N/A'
  });
  
  const loadingId = showLoading();
  
  // Prepare FormData
  debugLog('API', 'Step 1: Preparing FormData');
  const formData = new FormData();
  formData.append('symptom_text', text);
  
  if (imageFile) {
    formData.append('image', imageFile);
    debugLog('API', '✓ Image attached to FormData', {
      name: imageFile.name,
      type: imageFile.type,
      size: imageFile.size
    });
  }

  try {
    // Call the Python Backend
    debugLog('API', 'Step 2: Sending POST request to backend');
    debugLog('API', 'Backend URL: http://localhost:8000/analyze');
    
    const startTime = performance.now();
    
    const response = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      body: formData
    });

    const endTime = performance.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    
    debugLog('API', `✓ Response received in ${duration}s`, {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });

    if (!response.ok) {
      debugError('API', `HTTP error! status: ${response.status}`);
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    debugLog('API', 'Step 3: Parsing JSON response');
    const data = await response.json();
    
    debugLog('API', '✓ JSON parsed successfully', {
      risk: data.risk,
      status: data.status,
      hasRequestId: !!data.request_id,
      summaryLength: data.doctor_summary?.length || 0
    });
    
    removeLoading(loadingId);

    // Step 4: Display response
    if (data.doctor_summary) {
      debugLog('API', 'Step 4: Formatting and displaying response');
      
      // Format the output (convert newlines to <br>)
      const summaryHtml = data.doctor_summary.replace(/\n/g, '<br>');
      
      // Color code the risk
      let riskColor = '#fbbf24'; // yellow (moderate default)
      if(data.risk === 'HIGH') riskColor = '#ef4444'; // red
      if(data.risk === 'LOW') riskColor = '#10b981'; // green
      
      debugLog('API', `Risk color determined: ${riskColor} for ${data.risk}`);

      const formattedResponse = `
        <div style="border-left: 4px solid ${riskColor}; padding-left: 10px;">
          <strong>Risk Level: <span style="color:${riskColor}">${data.risk}</span></strong>
          <br><br>
          ${summaryHtml}
        </div>
      `;
      
      addBotMessage(formattedResponse);
      debugLog('API', '✓ Response displayed to user');
      
      // Log debug info if available
      if (data.debug_info) {
        debugLog('API', 'Debug info from backend:', data.debug_info);
      }
      
    } else {
      debugLog('API', '⚠️ No doctor_summary in response', data);
      addBotMessage("I couldn't analyze that. Please add more details.");
    }
    
    debugLog('API', '='.repeat(70));
    debugLog('API', 'API REQUEST COMPLETED SUCCESSFULLY');
    debugLog('API', '='.repeat(70));

  } catch (error) {
    removeLoading(loadingId);
    
    debugError('API', 'Request failed', error);
    debugLog('API', 'Error details:', {
      name: error.name,
      message: error.message,
      stack: error.stack
    });
    
    // Check if it's a network error
    if (error.message.includes('fetch')) {
      debugError('API', 'Network error - backend may not be running');
      addBotMessage("⚠️ Cannot connect to backend server. Please make sure it's running on http://localhost:8000");
    } else {
      addBotMessage(getBotText("error"));
    }
    
    debugLog('API', '='.repeat(70));
    debugLog('API', 'API REQUEST FAILED');
    debugLog('API', '='.repeat(70));
  }
}

/* ================= EVENT LISTENERS ================= */

// 1. Language Selection
debugLog('EVENT', 'Setting up language selection listener');
chat.addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;

  const lang = btn.innerText.trim();
  debugLog('EVENT', `Language button clicked: ${lang}`);
  
  const allowed = ["English", "हिंदी", "தமிழ்", "తెలుగు", "मराठी"];
  if (!allowed.includes(lang)) {
    debugLog('EVENT', `⚠️ Invalid language: ${lang}`);
    return;
  }

  selectedLanguage = lang;
  debugLog('EVENT', `✓ Language selected: ${selectedLanguage}`);
  
  textInput.disabled = false;
  textInput.placeholder = "Describe your symptoms...";
  debugLog('EVENT', 'Text input enabled');

  // Remove language buttons
  const languageMessages = document.querySelectorAll(".message.ai");
  let removedCount = 0;
  languageMessages.forEach(msg => {
    if (msg.querySelector(".language-options")) {
      msg.remove();
      removedCount++;
    }
  });
  debugLog('EVENT', `Removed ${removedCount} language selection message(s)`);

  addUserMessage(lang);
  setTimeout(() => {
    addBotMessage(getBotText("languageSelected"));
    textInput.focus();
    debugLog('EVENT', 'Input focused for user');
  }, 400);
});

// 2. Image Selection
debugLog('EVENT', 'Setting up image input listener');
imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  
  debugLog('EVENT', 'Image input changed', {
    hasFile: !!file,
    selectedLanguage: selectedLanguage
  });
  
  if (!file) {
    debugLog('EVENT', '⚠️ No file selected');
    return;
  }
  
  if (!selectedLanguage) {
    debugLog('EVENT', '⚠️ No language selected yet');
    return;
  }

  pendingImage = file; // Store for sending later
  debugLog('EVENT', '✓ Image stored as pending', {
    name: file.name,
    type: file.type,
    size: `${(file.size / 1024).toFixed(2)} KB`
  });

  const url = URL.createObjectURL(file);
  debugLog('EVENT', `✓ Object URL created: ${url}`);
  
  addUserMessage(`<div class="image-bubble"><img src="${url}"></div>`);
  
  // Prompt user to add text
  setTimeout(() => {
    addBotMessage("Image received. Please describe the pain or symptoms.");
    textInput.focus();
  }, 500);
  
  // Clear input value so same file can be selected again if needed
  imageInput.value = "";
  debugLog('EVENT', 'Image input value cleared for reuse');
});

// 3. Send Message
function handleSend() {
  debugLog('EVENT', 'Handle send triggered');
  
  const text = textInput.value.trim();
  debugLog('EVENT', 'Send attempt', {
    hasText: !!text,
    textLength: text.length,
    selectedLanguage: selectedLanguage,
    hasPendingImage: !!pendingImage
  });
  
  if (text && selectedLanguage) {
    debugLog('EVENT', '✓ Valid send conditions met');
    addUserMessage(text);
    sendToBackend(text, pendingImage);
    
    // Reset inputs
    textInput.value = "";
    pendingImage = null; // Clear image after sending
    sendBtn.disabled = true;
    
    debugLog('EVENT', '✓ Inputs reset', {
      textInput: textInput.value,
      pendingImage: pendingImage,
      sendBtnDisabled: sendBtn.disabled
    });
  } else {
    debugLog('EVENT', '⚠️ Invalid send conditions', {
      hasText: !!text,
      hasLanguage: !!selectedLanguage
    });
  }
}

debugLog('EVENT', 'Setting up send button listener');
sendBtn.addEventListener("click", handleSend);

debugLog('EVENT', 'Setting up Enter key listener');
textInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    debugLog('EVENT', 'Enter key pressed');
    e.preventDefault();
    handleSend();
  }
});

debugLog('EVENT', 'Setting up input validation listener');
textInput.addEventListener("input", () => {
  const hasText = !!textInput.value.trim();
  const hasLanguage = !!selectedLanguage;
  const shouldEnable = hasText && hasLanguage;
  
  sendBtn.disabled = !shouldEnable;
  
  debugLog('INPUT', 'Input validation', {
    hasText,
    hasLanguage,
    buttonEnabled: !sendBtn.disabled
  });
});

/* ================= INITIALIZATION COMPLETE ================= */
debugLog('INIT', '='.repeat(70));
debugLog('INIT', 'CHAT INTERFACE INITIALIZED SUCCESSFULLY');
debugLog('INIT', '='.repeat(70));
debugLog('INIT', 'Waiting for user interaction...');
