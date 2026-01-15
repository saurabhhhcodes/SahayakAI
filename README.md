# Sahayak.AI: The Omni-Lingual Educational AI Assistant

**Sahayak.AI** ("Helper" in Hindi) is a next-generation educational assistant designed to democratize access to quality learning. It adapts to the user's language, intellectual level, and style, providing deep, multimedia-rich explanations.

🔗 **Live Demo**: [https://sahayakai-okwu.onrender.com/app/](https://sahayakai-okwu.onrender.com/app/)

---

## 🚀 Key Features

### 1. 🧠 Intellectual Mirroring & Memory
- **Adaptive Persona**: The AI analyzes your tone. If you speak academically, it responds with profound depth. If you are casual, it relaxes while maintaining accuracy.
- **Context Awareness**: It remembers your name, previous topics, and learning progress throughout the session.

### 2. 🗣️ Omni-Lingual & Voice-First
- **Multilingual Support**: Chat in **Hindi**, **Tamil**, **Kannada**, **Telugu**, or **English**. The AI understands all and replies in your language.
- **Hybrid Voice Engine**: Automatically selects the best available voice (English Male/British preference) to provide a premium auditory experience.

### 3. 🎥 Multimedia Generation
- **AI Video**: Ask for a video (e.g., *"Show me a fox running"*), and it generates one using Hugging Face ModelScope (Text-to-Video).
  - *Fallback*: If the complex model is busy, it instantly creates a high-quality "Motion Slide" (Image-to-Video) so you never get an error.
- **Smart PPT**: Click **"Download PPT"** for any topic, and the system uses the LLM (Groq) to write **5 actual content slides** (Introduction, Key Concepts, Summary) for you.
- **YouTube Integration**: Just say *"Search YouTube for quantum physics"* to get instant video results.

### 4. ⚡ Hyper-Fast Architecture
- **Groq LPU**: Powered by **Llama 3.3 70B** on Groq, ensuring near-instantaneous text responses.
- **Hybrid Protocol**: Uses a smart mix of Plain Text (for speed/depth) and JSON (for tools) to minimize latency and errors.

---

## 🛠️ Deployment Guide (Render)

This project is configured for **1-Click Deployment** on Render.

1.  Fork/Clone this repo.
2.  Go to [Render Dashboard](https://dashboard.render.com/) -> **New Web Service**.
3.  Connect your repository (`saurabhhhcodes/SahayakAI`).
4.  **Settings**:
    - **Runtime**: Python 3
    - **Build Command**: `pip install -r backend/requirements.txt`
    - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5.  **Environment Variables** (Critical):
    - `PYTHON_VERSION`: `3.10.0`
    - `GROQ_API_KEY`: Get from [Groq Cloud](https://console.groq.com/)
    - `HF_TOKEN`: Get from [Hugging Face](https://huggingface.co/settings/tokens)

---

## 💻 Local Development

1.  **Clone**:
    ```bash
    git clone https://github.com/saurabhhhcodes/SahayakAI.git
    cd SahayakAI
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r backend/requirements.txt
    ```

3.  **Run Server**:
    ```bash
    cd backend
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```
    Open `http://localhost:8000/app/` in your browser.

---

## 🤝 Contributing
Open Source education is the future. Feel free to fork, submit PRs, or suggest features!

**Created by**: Saurabh Bajpai (`saurabhhhcodes`)