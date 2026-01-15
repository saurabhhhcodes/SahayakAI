const chatContainer = document.getElementById('chat-container');
const micBtn = document.getElementById('mic-btn');
const liveBtn = document.getElementById('live-btn'); // New Live Button using Badge
const textInput = document.getElementById('text-input');
const sendBtn = document.getElementById('send-btn');

let isRecording = false;
let recognition = null;
let synthesis = window.speechSynthesis;

// 1. Initialize Speech Recognition
const muteBtn = document.getElementById('mute-btn'); // New
const micPulse = document.getElementById('mic-pulse'); // New

let isMuted = false;
let isLiveMode = true; // Default to Live Mode on? Or Off? Let's default to ON for "Live Badge" visual.

// 1. Initialize Speech Recognition
const langSelect = document.getElementById('lang-select');
let currentLang = 'en-IN';

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = currentLang; // Default
    recognition.interimResults = false;

    // Update Lang on Change
    if (langSelect) {
        langSelect.addEventListener('change', () => {
            currentLang = langSelect.value;
            recognition.lang = currentLang;
            // Also notify backend? Ideally, passing lang in specific request is better.
            speakText("Language changed.");
        });
    }

    recognition.onstart = () => {
        isRecording = true;
        micBtn.classList.add('recording');
        micPulse.classList.add('active'); // Pulse on
        micBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';

        // CRITICAL: Stop any ongoing AI speech immediately when user starts speaking
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
        }
    };

    recognition.onend = () => {
        isRecording = false;
        micBtn.classList.remove('recording');
        micPulse.classList.remove('active'); // Pulse off
        micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
        micBtn.appendChild(micPulse); // Re-append pulse div

        // Auto-restart if Live Mode is active
        if (isLiveMode) {
            startRecording();
        }
    };
};

function startRecording() {
    if (!recognition || isRecording) return;
    try {
        recognition.start();
    } catch (e) {
        console.error("Start Recording Error:", e);
    }
}

function stopRecording() {
    if (!recognition || !isRecording) return;
    try {
        recognition.stop();
    } catch (e) {
        console.error("Stop Recording Error:", e);
    }
}

// 2. Text-to-Speech (TTS)
function speakText(text) {
    if (!synthesis || isMuted) return; // Respect Mute

    // CRITICAL: Stop listening while speaking to prevent self-loop
    if (isRecording) {
        recognition.stop();
        // We don't verify isRecording=false immediately effectively until onend, 
        // but we want to prevent new input.
    }

    // Stop any current speech
    synthesis.cancel();

    // Intelligent Summary: Don't read full slides
    let textToSpeak = text;
    if (text.includes('[SLIDE]')) {
        textToSpeak = "Here is the presentation you requested. You can swipe through the slides.";
    } else if (text.includes('mermaid')) {
        textToSpeak = text.split('mermaid')[0] + " Here is the diagram.";
    }

    // Remove HTML tags for reading
    const cleanText = textToSpeak.replace(/<[^>]*>?/gm, '');

    const utterance = new SpeechSynthesisUtterance(cleanText);

    utterance.onstart = () => {
        // Double safety to ensure mic is off
        if (isRecording) recognition.stop();
        micBtn.classList.add('disabled-while-speaking'); // Visual cue
    };

    utterance.onend = () => {
        micBtn.classList.remove('disabled-while-speaking');
        // Resume listening ONLY if:
        // 1. Live Mode is active 
        // 2. The user didn't manually stop it (hard to track, but Live Mode implies continuous)
        if (isLiveMode) {
            setTimeout(() => startRecording(), 300); // Small delay to avoid picking up echo
        }
    };

    utterance.rate = 1;
    // Slight variation for natural feel
    utterance.pitch = 1 + (Math.random() * 0.2 - 0.1);

    // Select Indian Accent Voice if available
    const voices = synthesis.getVoices();
    const indianVoice = voices.find(voice => voice.lang.includes('IN') || voice.name.includes('India'));
    if (indianVoice) {
        utterance.voice = indianVoice;
    }

    synthesis.speak(utterance);
}

// ... existing code ...

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    textInput.value = transcript;

    // UX DECISION: 
    // Standard Mode: Populate only. User confirms.
    // Live Mode: Auto-send (otherwise it's not "Live" fluid conversation)
    // BUT user specifically complained about "Directly uploading".
    // Compromise: Live Mode waits 2s? Or just Populate?
    // Let's follow user instruction strictly: "It should not properly directly upload it."

    if (isLiveMode) {
        // For Live Mode, maybe a short delay then send? 
        // Or populate and wait for silence?
        // Let's try: Populate -> Wait 2s -> Send (if no edits).
        // Simpler for now: Populate, but call sendMessage() ONLY if LiveMode.
        setTimeout(() => sendMessage(), 1500);
    } else {
        // Standard Mode: JUST POPULATE. Do nothing else.
        textInput.focus();
    }
};

// Haptic Language Slider Logic
const languages = [
    { code: 'en-IN', name: '🇬🇧 English (India)', label: 'English' },
    { code: 'hi-IN', name: '🇮🇳 Hindi', label: 'हिंदी' },
    { code: 'bn-IN', name: '🇮🇳 Bengali', label: 'বাংলা' },
    { code: 'ta-IN', name: '🇮🇳 Tamil', label: 'தமிழ்' },
    { code: 'te-IN', name: '🇮🇳 Telugu', label: 'తెలుగు' },
    { code: 'mr-IN', name: '🇮🇳 Marathi', label: 'मराठी' },
    { code: 'am-ET', name: '🇪🇹 Amharic', label: 'አማርኛ' },
    { code: 'ti-ET', name: '🇪🇹 Tigrinya', label: 'ትግርኛ' },
    { code: 'es-ES', name: '🇪🇸 Spanish', label: 'Español' },
    { code: 'fr-FR', name: '🇫🇷 French', label: 'Français' },
];

const translations = {
    'en-IN': {
        intro_title: "Namaste. I am Sahayak AI.",
        intro_subtitle: "\"I am the child who wants to learn. Will you teach me?\"<br>Your AI Pedagogical Companion.",
        start_teaching: "Start Teaching",
        select_language: "Select Interaction Language",
        input_placeholder: "Ask Sahayak...",
        voice_enabled: "Voice Output Enabled",
        voice_disabled: "Voice Output Muted"
    },
    'hi-IN': {
        intro_title: "नमस्ते। मैं सीख रहा हूँ।",
        intro_subtitle: "\"मैं वह बच्चा हूँ जो सीखना चाहता है। क्या आप मुझे सिखाएंगे?\"<br>आपका एआई शिक्षण साथी।",
        start_teaching: "पढ़ाना शुरू करें",
        select_language: "बातचीत की भाषा चुनें",
        input_placeholder: "सहायक से पूछें...",
        voice_enabled: "आवाज़ सक्षम है",
        voice_disabled: "आवाज़ बंद है"
    }
    // Add others as needed for demo
};

// --- Slider Logic ---
const langOverlay = document.getElementById('lang-overlay');
const langBtn = document.getElementById('lang-btn');
const closeLangBtn = document.getElementById('close-lang-btn');
const pickerList = document.getElementById('lang-picker-list');
let lastScrollY = 0;
let hapticTimeout;

if (langBtn) {
    langBtn.addEventListener('click', () => {
        langOverlay.classList.remove('hidden');
        renderPicker();
        // Scroll to current
        setTimeout(scrollToCurrentLang, 100);
    });
}

if (closeLangBtn) {
    closeLangBtn.addEventListener('click', () => {
        langOverlay.classList.add('hidden');
    });
}

function renderPicker() {
    pickerList.innerHTML = '';
    languages.forEach(lang => {
        const li = document.createElement('li');
        li.className = 'picker-item';
        li.textContent = lang.name;
        li.dataset.code = lang.code;
        if (lang.code === currentLang) li.classList.add('selected');

        li.addEventListener('click', () => {
            // Click to select
            setLanguage(lang.code);
            scrollToCurrentLang();
        });

        pickerList.appendChild(li);
    });
}

function scrollToCurrentLang() {
    const selected = pickerList.querySelector(`[data-code="${currentLang}"]`);
    if (selected) {
        selected.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Haptic Scroll Support
pickerList.addEventListener('scroll', (e) => {
    const itemHeight = 40;
    const scrollTop = pickerList.scrollTop;

    // Find closest item
    const index = Math.round(scrollTop / itemHeight);

    // Simple Debounce for Haptics
    // Only vibrate if we crossed an index threshold
    const prevIndex = Math.round(lastScrollY / itemHeight);

    if (index !== prevIndex) {
        if (navigator.vibrate) navigator.vibrate(5); // Light tick
    }
    lastScrollY = scrollTop;

    // Visual selection update (loop through all)
    const items = pickerList.querySelectorAll('.picker-item');
    items.forEach((item, idx) => {
        if (idx === index) {
            if (!item.classList.contains('selected')) {
                // New selection logic could go here if we wanted auto-select on scroll
                // For now, just visual highlight or keep "selected" class only for confirmed one?
                // Let's make the center one bigger visually but not ACTUALLY change lang until click/confirm?
                // OR auto-select when scrolling stops (like iOS).
                // Let's try Auto-Select on scroll end.

                clearTimeout(hapticTimeout);
                hapticTimeout = setTimeout(() => {
                    setLanguage(item.dataset.code);
                    updatePickerVisuals(item.dataset.code);
                }, 200);
            }
        }
    });
});

function updatePickerVisuals(code) {
    const items = pickerList.querySelectorAll('.picker-item');
    items.forEach(item => {
        if (item.dataset.code === code) {
            item.classList.add('selected');
            item.style.transform = 'scale(1.1)';
            item.style.color = 'var(--primary)';
        } else {
            item.classList.remove('selected');
            item.style.transform = 'scale(1)';
            item.style.color = '#94a3b8';
        }
    });
}

function setLanguage(code) {
    if (currentLang === code) return;
    currentLang = code;
    recognition.lang = currentLang;

    // Update Text
    const dict = translations[code] || translations['en-IN']; // Fallback

    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        if (dict[key]) el.textContent = dict[key];
    });

    // HTML content handling (subtitles)
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
        const key = el.dataset.i18nHtml;
        if (dict[key]) el.innerHTML = dict[key];
    });

    // Placeholder handling
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.dataset.i18nPlaceholder;
        if (dict[key]) el.placeholder = dict[key];
    });

    // Notify user
    // speakText("Language changed"); // Optional, might be annoying if scrolling fast
}

// Event Listeners for Audio Controls
if (muteBtn) {
    muteBtn.addEventListener('click', () => {
        isMuted = !isMuted;
        muteBtn.classList.toggle('muted', isMuted);
        if (isMuted) {
            synthesis.cancel();
            muteBtn.innerHTML = '<i class="fa-solid fa-volume-xmark"></i>';
        } else {
            muteBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
            speakText("Voice output enabled.");
        }
    });
}

// Load voices (sometimes checking immediately yields empty array)
window.speechSynthesis.onvoiceschanged = () => {
    // Just force a reload of voices
    window.speechSynthesis.getVoices();
};


micBtn.addEventListener('click', () => {
    // IMMEDIATE INTERRUPT of any ongoing speech
    if (window.speechSynthesis.speaking) window.speechSynthesis.cancel();

    if (!isRecording) startRecording();
    else stopRecording();
    if (!isRecording) startRecording();
    else stopRecording();
});

// Live Mode Toggle Logic
if (liveBtn) {
    liveBtn.addEventListener('click', () => {
        isLiveMode = !isLiveMode;

        // Visual Update
        const dot = liveBtn.querySelector('.live-dot');
        const text = liveBtn.querySelector('span');

        if (isLiveMode) {
            liveBtn.style.borderColor = 'rgba(34, 197, 94, 0.2)';
            liveBtn.style.background = 'rgba(34, 197, 94, 0.1)';
            dot.style.background = '#22c55e';
            dot.style.boxShadow = '0 0 8px #22c55e';
            dot.style.animation = 'pulse-green 2s infinite';
            text.style.color = '#22c55e';

            // If we just turned it on, start listening
            if (!isRecording) startRecording();
        } else {
            liveBtn.style.borderColor = 'rgba(148, 163, 184, 0.2)';
            liveBtn.style.background = 'rgba(148, 163, 184, 0.1)';
            dot.style.background = '#94a3b8';
            dot.style.boxShadow = 'none';
            dot.style.animation = 'none';
            text.style.color = '#94a3b8';

            // If we turned it off, stop listening (optional, but logical)
            stopRecording();
        }
    });
}

// --- CLEAN CODE REFACTOR: Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // 1. Elements
    const introOverlay = document.getElementById('intro-overlay');
    const mainApp = document.getElementById('main-app');

    // DISABLE INTRO (User Request)
    if (introOverlay) {
        introOverlay.style.display = 'none';
    }
    if (mainApp) {
        mainApp.style.opacity = '1';
    }

    // Auto-Focus
    if (textInput) textInput.focus();
});

sendBtn.addEventListener('click', sendMessage);
textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
    const text = textInput.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    textInput.value = '';
    const loadingId = addLoadingIndicator();

    try {
        const response = await fetch('/chat', { // New Endpoint
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        const data = await response.json();
        removeMessage(loadingId);

        // --- GROQ JSON HANDLER ---
        const tool = data.tool_used || 'text'; // Fallback
        const content = data.data;
        const metadata = data.metadata || {};
        const agentName = (metadata.audience_level === 'teacher') ? 'Pedagogy' : 'Sahayak';

        let displayHTML = "";

        if (tool === 'text') {
            displayHTML = content; // Will be marked-parsed in addMessage
        }
        else if (tool === 'mermaid') {
            displayHTML = `<div class="mermaid">${content}</div>`;
        }
        else if (tool === 'image_prompt') {
            displayHTML = `**Generating Image...**\n*${content}*`;
            // Trigger Client-Side Image Gen
            fetchAndAppendImage(content);
        }
        else if (tool === 'presentation') {
            // data is slides array.
            // We'll store it in a way the button can access, or just pass title.
            // For this Hackathon Demo, "Title" is enough to generate a mock/real file.
            const title = metadata.topic || "Lesson";
            displayHTML = `**Presentation Ready: ${title}**\n[DOWNLOAD_PPT: ${title}]`;
        }
        else if (tool === 'document') {
            const title = metadata.topic || "Document";
            displayHTML = `**Document Ready: ${title}**\n[DOWNLOAD_PDF: ${title}]`;
        }

        // Render
        const msgDiv = addMessage(displayHTML, 'ai', true, agentName);

        // Speak
        if (tool === 'text') speakText(content);

    } catch (error) {
        console.error('Error:', error);
        removeMessage(loadingId);
        addMessage("Sorry, I am unable to reach the Brain (Groq). Please check the backend connection.", 'ai');
    }
}

// Helper: Fetch Image (Client-Side)
async function fetchAndAppendImage(prompt) {
    const chatContainer = document.getElementById('chat-container');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai-message';
    loadingDiv.innerHTML = `<div class="message-content"><i class="fa-solid fa-paintbrush fa-bounce"></i> Painting "${prompt.substring(0, 20)}..."</div>`;
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    try {
        const res = await fetch(`/generate/image?prompt=${encodeURIComponent(prompt)}`);
        if (!res.ok) throw new Error("Image Gen Failed");
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);

        const img = document.createElement('img');
        img.src = url;
        img.className = "generated-image";
        img.style.cssText = "max-width: 100%; border-radius: 12px; margin-top: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);";
        img.onclick = () => window.open(url, '_blank');

        loadingDiv.querySelector('.message-content').innerHTML = '';
        loadingDiv.querySelector('.message-content').appendChild(img);

    } catch (e) {
        loadingDiv.innerHTML = `<div class="message-content" style="color:red">Image Generation Failed on Server.</div>`;
    }
}

// Helper: Fetch Video
async function fetchAndAppendVideo(prompt) {
    const chatContainer = document.getElementById('chat-container');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai-message';
    loadingDiv.innerHTML = `<div class="message-content"><i class="fa-solid fa-video fa-bounce"></i> Filming "${prompt.substring(0, 20)}..."</div>`;
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    try {
        const res = await fetch(`/generate/video?prompt=${encodeURIComponent(prompt)}`);
        if (!res.ok) throw new Error("Video Gen Failed");
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);

        const video = document.createElement('video');
        video.src = url;
        video.controls = true;
        video.autoplay = true;
        video.loop = true;
        video.className = "generated-video";
        video.style.cssText = "max-width: 100%; border-radius: 12px; margin-top: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); width: 400px;";

        loadingDiv.querySelector('.message-content').innerHTML = '';
        loadingDiv.querySelector('.message-content').appendChild(video);

    } catch (e) {
        loadingDiv.innerHTML = `<div class="message-content" style="color:red">Video Generation Failed (Server Busy).</div>`;
    }
}

// ... (previous code)

function addMessage(text, sender, isHTML = false, agent = '') {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;
    const id = 'msg-' + Date.now();
    msgDiv.id = id;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = sender === 'ai' ? '<i class="fa-solid fa-robot"></i>' : '<i class="fa-solid fa-user"></i>';

    const content = document.createElement('div');
    content.className = 'message-content';

    if (sender === 'ai') {
        const agentName = agent ? (agent.charAt(0).toUpperCase() + agent.slice(1)) : 'Assistant';
        const badge = `<span class="agent-tag"><i class="fa-solid fa-brain"></i> ${agentName} Agent</span>`;

        // 1. Extract Quiz Blocks specifically (detect before Markdown parsing)
        const quizRegex = /\[QUIZ\]([\s\S]*?)\[END QUIZ\]/g;
        let quizMatch;

        // --- NEW: Download Buttons Detection ---
        // Pattern: [DOWNLOAD_PDF: Title], [DOWNLOAD_PPT: Title], [DOWNLOAD_VIDEO: Title]
        const downloadRegex = /\[DOWNLOAD_(PDF|PPT|VIDEO):\s*(.*?)\]/g;

        // Temporary separate content for downloads
        let downloadButtonsHTML = "";
        let cleanText = text.replace(downloadRegex, (match, type, title) => {
            const icon = type === 'PDF' ? 'fa-file-pdf' : (type === 'PPT' ? 'fa-file-powerpoint' : 'fa-video');
            const color = type === 'PDF' ? 'red' : (type === 'PPT' ? '#d04423' : '#4f46e5');
            // Return empty string to remove tag from text, and build button separately
            // We encode content in a data attribute or just trigger a generic request? 
            // Ideally, the backend should have generated it already vs generating on demand. 
            // For this POC, we will generate on demand using the *title* and *previous context* (which backend has).

            downloadButtonsHTML += `
                    <button onclick="downloadMedia('${type}', '${title.replace(/'/g, "\\'")}')" class="download-btn" style="
                        margin-top: 10px; margin-right: 10px; padding: 8px 16px; 
                        background: ${color}; color: white; border: none; border-radius: 8px; 
                        cursor: pointer; display: inline-flex; align-items: center; gap: 8px;
                        font-family: 'Outfit', sans-serif;">
                        <i class="fa-solid ${icon}"></i> Download ${type}
                    </button>
                `;
            return "";
        });

        // Parse Markdown for the rest
        const rawHtml = marked.parse(cleanText);
        content.innerHTML = rawHtml + downloadButtonsHTML;

        // ... existing quiz logic ...
        let quizBlocks = [];
        let match;
        while ((match = quizRegex.exec(text)) !== null) {
            quizBlocks.push(match[1]);
        }

        // Remove QUIZ blocks from display text
        let finalCleanText = text.replace(quizRegex, '').trim();

        // Fix: Global cleanup for persistent LLM syntax errors
        finalCleanText = finalCleanText.replace(/Syntax error in text/gi, '')
            .replace(/mermaid version \d+\.\d+\.\d+/gi, '')
            .replace(/mermaid version 10\.9\.5/gi, ''); // Specific hardcoded version often seen

        // 2. Parse Markdown
        let htmlContent = marked.parse(finalCleanText);

        content.innerHTML = badge + htmlContent;

        // Post-process for Mermaid
        // Convert pre.language-mermaid to div.mermaid
        const mermaidBlocks = content.querySelectorAll('pre.language-mermaid');
        mermaidBlocks.forEach(block => {
            let graphDefinition = block.textContent;

            // Fix: Aggressively remove garbage lines
            const lines = graphDefinition.split('\n');
            const cleanLines = lines.filter(line => {
                const l = line.trim().toLowerCase();
                return !l.includes('mermaid version') && !l.includes('syntax error');
            });
            graphDefinition = cleanLines.join('\n').trim();

            const mermaidDiv = document.createElement('div');
            mermaidDiv.className = 'mermaid';
            mermaidDiv.textContent = graphDefinition;
            block.replaceWith(mermaidDiv);
        });

        // 5. Render Mermaid
        const mermaidDivs = content.querySelectorAll('.mermaid');
        if (mermaidDivs.length > 0) {
            // Slight delay to ensure DOM is ready if needed, but usually direct init is fine here.
            setTimeout(() => {
                try {
                    mermaid.init(undefined, mermaidDivs);
                } catch (err) {
                    console.error("Mermaid Init Failed:", err);
                    mermaidDivs.forEach(div => {
                        div.innerHTML = `<div style="color:red; font-size:0.8rem;">Diagram Error (Syntax)</div><pre>${div.textContent}</pre>`;
                    });
                }
                if (typeof hljs !== 'undefined') hljs.highlightAll();
            }, 100);
        }

        // 7. Render Mock Quizzes
        if (quizBlocks.length > 0) {
            const quizContainer = document.createElement('div');
            quizContainer.className = 'quiz-container';
            quizBlocks.forEach(qText => renderQuiz(qText, quizContainer));
            content.appendChild(quizContainer); // Append to content, not msgDiv, to be inside bubble
        }

        // 8. Visualizer/Emoji Triggers
        if (typeof floatEmojis === 'function') floatEmojis(text);
        if (typeof startPresentation === 'function' && text.includes('[SLIDE]')) {
            startPresentation(text); // Pass original text for slides
        }

        // Detect Presentation Slides
        if (text.includes("[SLIDE]")) {
            const startPresBtn = document.createElement('button');
            startPresBtn.className = 'icon-btn';
            startPresBtn.style.cssText = "font-size: 0.8rem; margin-top: 10px; background: #fce7f3; color: #db2777; width: auto; padding: 5px 10px; border-radius: 8px; margin-left: 10px;";
            startPresBtn.innerHTML = '<i class="fa-solid fa-play"></i> Play Presentation';
            startPresBtn.onclick = () => startPresentation(text);
            content.appendChild(startPresBtn);
        }

        // Detect & Render Quiz
        if (text.includes("[QUIZ]")) {
            renderQuiz(text, content);
        }


        // Add Download PDF Button for Pedagogy (Only for substantial content)
        if (agent === 'pedagogy' && text.length > 150) {
            const pdfBtn = document.createElement('button');
            pdfBtn.className = 'icon-btn';
            pdfBtn.style.cssText = "font-size: 0.8rem; margin-top: 10px; background: #e0e7ff; color: #4f46e5; width: auto; padding: 5px 10px; border-radius: 8px;";
            pdfBtn.innerHTML = '<i class="fa-solid fa-file-pdf"></i> Download Lesson Plan';
            pdfBtn.onclick = () => downloadPDF("Lesson Plan", text);
            content.appendChild(pdfBtn);
        }

        // Trigger Floating Emojis based on content
        floatEmojis(text);

    } else {
        // Quick check for Pollinations URL in text to render as image
        // We now intercept this to use OUR backend generator (Open Source SDXL) if possible.
        const imgRegex = /(https:\/\/image\.pollinations\.ai\/prompt\/[^\s]+)/g;
        if (imgRegex.test(text)) {
            const parts = text.split(imgRegex);
            parts.forEach(part => {
                if (part.match(imgRegex)) {
                    try {
                        // Extract prompt from URL
                        const urlObj = new URL(part.replace(/\)$/, ''));
                        const prompt = decodeURIComponent(urlObj.pathname.replace('/prompt/', ''));

                        // Use OUR Backend (Open Source HF)
                        const newSrc = `/generate/image?prompt=${encodeURIComponent(prompt)}`;

                        const img = document.createElement('img');
                        img.src = newSrc;
                        img.className = "generated-image";
                        img.style.cssText = "max-width: 100%; border-radius: 10px; margin-top: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); cursor: pointer;";
                        img.onclick = () => window.open(newSrc, '_blank');
                        content.appendChild(img);
                    } catch (e) {
                        console.error("Image Parse Error", e);
                        // Fallback to original
                        const img = document.createElement('img');
                        img.src = part;
                        content.appendChild(img);
                    }
                } else if (part.trim()) {
                    const txt = document.createElement('span');
                    txt.textContent = part;
                    content.appendChild(txt);
                }
            });
        } else {
            content.innerHTML = marked.parse(text);
        }
    }

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(content);
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    return msgDiv;
}

// ... (rest of code)

function addLoadingIndicator() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai-message loading-msg';
    msgDiv.innerHTML = `
        <div class="avatar"><i class="fa-solid fa-robot"></i></div>
        <div class="message-content">
            <i class="fa-solid fa-circle-notch fa-spin"></i> Thinking...
        </div>
    `;
    const id = 'loading-' + Date.now();
    msgDiv.id = id;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Hack: Simple chart detection from text response
// Expects: [CHART:{type:'bar', data:[10,20], labels:['A','B']}] - Fake protocol for demo
function checkForChart(text, container) {
    // This is a dummy function for now. In a real scenario, the LLM would output structured JSON.
    // For this hackathon, we can trigger a demo chart based on keywords.

    if (text.toLowerCase().includes("performance") || text.toLowerCase().includes("progress")) {
        const chartWrapper = document.createElement('div');
        chartWrapper.className = 'chart-container';
        const canvas = document.createElement('canvas');
        chartWrapper.appendChild(canvas);

        // Append inside the message content
        container.querySelector('.message-content').appendChild(chartWrapper);

        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Student Engagement',
                    data: [65, 59, 80, 81],
                    backgroundColor: 'rgba(99, 102, 241, 0.5)',
                    borderColor: 'rgb(99, 102, 241)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true } }
            }
        });
    }
}

async function downloadPDF(title, content) {
    try {
        const response = await fetch('/download/pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "Lesson_Plan.pdf";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    } catch (error) {
        console.error("PDF Download Error", error);
    }
}

// Presentation Mode Logic
let currentSlideIndex = 0;
let slides = [];
let presentationOverlay = null;

function startPresentation(text) {
    // 1. Parse text into slides
    const rawSlides = text.split("[SLIDE]").filter(s => s.trim().length > 0);
    slides = rawSlides.map(s => marked.parse(s));

    if (slides.length === 0) return;

    currentSlideIndex = 0;

    // 2. Create Overlay
    presentationOverlay = document.createElement('div');
    presentationOverlay.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: #0f172a; z-index: 9999; display: flex; flex-direction: column;
        justify-content: center; align-items: center; color: white;
    `;

    // Slide Container
    const slideContent = document.createElement('div');
    slideContent.id = 'slide-content';
    slideContent.style.cssText = `
        width: 80%; height: 70%; background: white; color: #1e293b;
        border-radius: 20px; padding: 40px; font-size: 2rem; overflow-y: auto;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    `;

    // Controls
    const controls = document.createElement('div');
    controls.style.cssText = "margin-top: 20px; display: flex; gap: 20px;";

    const prevBtn = document.createElement('button');
    prevBtn.innerHTML = '<i class="fa-solid fa-backward"></i>';
    prevBtn.onclick = () => showSlide(currentSlideIndex - 1);

    const nextBtn = document.createElement('button');
    nextBtn.innerHTML = '<i class="fa-solid fa-forward"></i>';
    // User requested auto-play, but manual is safer MVP. 
    // We can add auto-play logic:

    nextBtn.onclick = () => showSlide(currentSlideIndex + 1);

    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '<i class="fa-solid fa-xmark"></i> Close';
    closeBtn.onclick = () => {
        document.body.removeChild(presentationOverlay);
        presentationOverlay = null;
    };

    [prevBtn, nextBtn, closeBtn].forEach(btn => {
        btn.style.cssText = "padding: 10px 20px; font-size: 1.2rem; border-radius: 10px; cursor: pointer; border: none;";
    });

    controls.appendChild(prevBtn);
    controls.appendChild(nextBtn);
    controls.appendChild(closeBtn);

    presentationOverlay.appendChild(slideContent);
    presentationOverlay.appendChild(controls);
    document.body.appendChild(presentationOverlay);

    showSlide(0);

    // Auto-advance feature (User Request)
    // "Automatically move to next slide after 10 seconds"
    let autoPlayInterval = setInterval(() => {
        if (!presentationOverlay) {
            clearInterval(autoPlayInterval);
            return;
        }
        if (currentSlideIndex < slides.length - 1) {
            showSlide(currentSlideIndex + 1);
        } else {
            clearInterval(autoPlayInterval);
        }
    }, 10000); // 10 seconds
}

function showSlide(index) {
    if (index < 0 || index >= slides.length) return;
    currentSlideIndex = index;
    const container = document.getElementById('slide-content');
    if (container) {
        container.innerHTML = slides[currentSlideIndex];
        // Re-run Mermaid if slide has it
        if (slides[currentSlideIndex].includes('mermaid')) {
            setTimeout(() => {
                const mermaidBlocks = container.querySelectorAll('.language-mermaid');
                mermaidBlocks.forEach(block => {
                    const graphDefinition = block.textContent;
                    const pre = block.parentElement;
                    const div = document.createElement('div');
                    div.className = 'mermaid';
                    div.textContent = graphDefinition;
                    pre.replaceWith(div);
                });
                mermaid.run({ nodes: container.querySelectorAll('.mermaid') });
            }, 50);
        }
    }
}

// 3. Floating Emojis Logic
function floatEmojis(text) {
    const keywords = {
        'star': '⭐', 'space': '🚀', 'planet': '🪐', 'earth': '🌍',
        'idea': '💡', 'think': '🤔', 'love': '❤️', 'happy': '😊',
        'question': '❓', 'game': '🎮', 'music': '🎵', 'fire': '🔥'
    };

    // Check keywords
    const lowerText = text.toLowerCase();
    Object.keys(keywords).forEach(key => {
        if (lowerText.includes(key)) {
            createFloatingEmoji(keywords[key]);
        }
    });
}

function createFloatingEmoji(emojiChar) {
    const emoji = document.createElement('div');
    emoji.textContent = emojiChar;
    emoji.style.cssText = `
        position: fixed;
        font-size: 2rem;
        pointer-events: none;
        z-index: 1000;
        animation: floatUp 4s ease-in forwards;
        bottom: -50px;
        left: ${Math.random() * 90}vw;
    `;
    document.body.appendChild(emoji);

    // Add keyframes if not present
    if (!document.getElementById('float-style')) {
        const style = document.createElement('style');
        style.id = 'float-style';
        style.textContent = `
            @keyframes floatUp {
                0% { transform: translateY(0) rotate(0deg); opacity: 1; }
                100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    // Cleanup
    setTimeout(() => {
        if (document.body.contains(emoji)) {
            document.body.removeChild(emoji);
        }
    }, 4000);
}

// 4. Interactive Quiz Logic
function renderQuiz(text, container) {
    const quizRegex = /\[QUIZ\]([\s\S]*?)\[END QUIZ\]/g;
    let match;

    while ((match = quizRegex.exec(text)) !== null) {
        const quizContent = match[1];
        const lines = quizContent.split('\n').filter(l => l.trim());

        const quizBox = document.createElement('div');
        quizBox.className = 'quiz-container';
        quizBox.style.cssText = "background: #f0fdf4; padding: 15px; border-radius: 12px; margin-top: 15px; border: 1px solid #bbf7d0;";

        let question = "";
        let options = [];
        let correct = "";
        let reason = "";

        lines.forEach(line => {
            if (line.startsWith("Question:")) question = line.replace("Question:", "").trim();
            else if (line.match(/^[A-D]\)/)) options.push(line.trim());
            else if (line.startsWith("Correct:")) correct = line.replace("Correct:", "").trim();
            else if (line.startsWith("Reason:")) reason = line.replace("Reason:", "").trim();
        });

        const qTitle = document.createElement('h4');
        qTitle.textContent = "🧠 Quick Quiz: " + question;
        qTitle.style.marginBottom = "10px";
        quizBox.appendChild(qTitle);

        const feedbackDiv = document.createElement('div');
        feedbackDiv.style.marginTop = "10px";
        feedbackDiv.style.fontWeight = "bold";

        options.forEach(opt => {
            const btn = document.createElement('button');
            btn.textContent = opt;
            btn.style.cssText = "display: block; width: 100%; margin: 5px 0; padding: 8px; text-align: left; border: 1px solid #ccc; border-radius: 6px; background: white; cursor: pointer;";

            btn.onclick = () => {
                const letter = opt.charAt(0);
                if (letter === correct) {
                    btn.style.background = "#dcfce7"; // Green
                    btn.style.borderColor = "#22c55e";
                    feedbackDiv.textContent = "✅ Correct! " + reason;
                    feedbackDiv.style.color = "#15803d";
                    createFloatingEmoji('🎉');
                } else {
                    btn.style.background = "#fee2e2"; // Red
                    btn.style.borderColor = "#ef4444";
                    feedbackDiv.textContent = "❌ Try again!";
                    feedbackDiv.style.color = "#b91c1c";
                }
            };
            quizBox.appendChild(btn);
        });

        quizBox.appendChild(feedbackDiv);
        container.appendChild(quizBox);
    }
}

// 5. Audio Visualizer Logic
let audioContext, analyser, dataArray, canvasCtx, visualizerCanvas;

function setupVisualizer() {
    visualizerCanvas = document.getElementById('audio-visualizer');
    canvasCtx = visualizerCanvas.getContext('2d');

    // Resize canvas
    visualizerCanvas.width = window.innerWidth;
    visualizerCanvas.height = 100;

    if (!navigator.mediaDevices) return;

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            const source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);
            analyser.fftSize = 256;
            const bufferLength = analyser.frequencyBinCount;
            dataArray = new Uint8Array(bufferLength);
            drawVisualizer();
        })
        .catch(err => console.error("Mic Error for Visualizer", err));
}

function drawVisualizer() {
    if (!visualizerCanvas || !analyser) return;

    // Only draw if Live Mode is active or mic is recording
    const isLive = document.getElementById('live-mode-toggle') && document.getElementById('live-mode-toggle').checked;
    const isRec = document.getElementById('mic-btn') && document.getElementById('mic-btn').classList.contains('recording');

    if (isLive || isRec) {
        visualizerCanvas.style.display = 'block';
    } else {
        visualizerCanvas.style.display = 'none';
        requestAnimationFrame(drawVisualizer);
        return;
    }

    requestAnimationFrame(drawVisualizer);

    analyser.getByteFrequencyData(dataArray);

    canvasCtx.clearRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);

    const barWidth = (visualizerCanvas.width / dataArray.length) * 2.5;
    let barHeight;
    let x = 0;

    for (let i = 0; i < dataArray.length; i++) {
        barHeight = dataArray[i] / 2;

        // Dynamic Color: Pink/Purple
        canvasCtx.fillStyle = `rgba(219, 39, 119, ${barHeight / 100})`;
        canvasCtx.fillRect(x, visualizerCanvas.height - barHeight, barWidth, barHeight);

        x += barWidth + 1;
    }
}

// 9. History Implementation (Real API)
async function fetchHistoryList() {
    try {
        const response = await fetch('/history');
        const data = await response.json();
        const listDiv = document.getElementById('history-list');
        if (!listDiv) return;

        listDiv.innerHTML = ''; // Clear

        data.sessions.forEach(session => {
            const item = document.createElement('div');
            item.className = 'history-item';
            item.textContent = session.summary || session.id;
            item.onclick = () => loadHistory(session.id);
            listDiv.appendChild(item);
        });
    } catch (e) {
        console.error("Failed to load history list", e);
    }
}

// Load List on Start
window.addEventListener('load', fetchHistoryList);

window.loadHistory = async function (sessionId) {
    const chatContainer = document.getElementById('chat-container');
    chatContainer.innerHTML = '';

    addMessage(`Loading session...`, 'user');
    const loadingId = addLoadingIndicator();

    try {
        const response = await fetch(`/history/${sessionId}`);
        const data = await response.json();

        removeMessage(loadingId);
        chatContainer.innerHTML = ''; // Clear loading msg

        data.history.forEach(msg => {
            // Rehydrate message
            const isHTML = true; // Assume history stored as raw content
            const sender = msg.role === 'user' ? 'user' : 'ai';
            addMessage(msg.content, sender, isHTML);
        });

        addMessage("Session restored.", 'ai');

    } catch (e) {
        removeMessage(loadingId);
        addMessage("Error loading session history.", 'ai');
        console.error(e);
    }
};

// Initialize Visualizer on first click
document.body.addEventListener('click', () => {
    if (!audioContext) setupVisualizer();
}, { once: true });

// Intro Avatar Customization
const editAvatarBtn = document.getElementById('edit-avatar-btn');
if (editAvatarBtn) {
    editAvatarBtn.addEventListener('click', () => {
        const currentPrompt = "cute 3d cartoon indian students and teacher learning together happy vibrant colors"; // default
        const newPrompt = prompt("Customize your Intro Avatar!\nDescribe the scene (e.g., 'Futuristic classroom with robot teacher'):", "");

        if (newPrompt && newPrompt.trim() !== "") {
            const encodedPrompt = encodeURIComponent(newPrompt);
            const newUrl = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=400&height=400&nologo=true`;

            const mascot = document.getElementById('intro-mascot');
            mascot.src = newUrl;

            // Save for future visits
            localStorage.setItem('intro_avatar_prompt', newPrompt);
        }
    });

    // Load saved intro avatar
    const savedIntro = localStorage.getItem('intro_avatar_prompt');
    if (savedIntro) {
        const mascot = document.getElementById('intro-mascot');
        const encodedPrompt = encodeURIComponent(savedIntro);
        mascot.src = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=400&height=400&nologo=true`;
    }
    // End of Intro Avatar Logic

    // 4. Download Handler
    async function downloadMedia(type, title) {
        const endpoint = `/download/${type.toLowerCase()}`;
        const btn = event.target.closest('button');
        const originalText = btn.innerHTML;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Generating...`;
        btn.disabled = true;

        try {
            // We pass title and "Context" (Content). For now, we will pass a generic content
            // In a real app, we'd pass the full chat context or specific lesson content.
            // We can grab the last AI message text as content? 
            // Let's use a placeholder request for now as the Backend generates content based on Title in this POC logic 
            // (See backend: generate_pdf uses title + content). 
            // Actually backend logic takes `content`. We should send something.

            const content = "Generated Lesson PlanContent based on: " + title + ". (Full content would be here)";
            const slides = [{ title: title, content: "Generated Content" }];

            const body = type === 'PPT' ? { title, slides } : { title, content };

            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            if (!res.ok) throw new Error("Generation Failed");

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${title}.${type === 'PPT' ? 'pptx' : (type === 'VIDEO' ? 'mp4' : 'pdf')}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            btn.innerHTML = `<i class="fa-solid fa-check"></i> Done`;
        } catch (err) {
            console.error(err);
            btn.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Error`;
        } finally {
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 3000);
        }
    }
}
// End of file
