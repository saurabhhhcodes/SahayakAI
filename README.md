# SahayakAI - AI Teaching Assistant

## Hackathon Deployment Ready
This project is configured for a **Production-Level MVP** deployment on [Render](https://render.com).

### Features
1. **Open Source LLM**: Powered by **Llama 3 (via Groq)** for fast, free, and high-quality inference.
2. **Open Source Embeddings**: Uses `sentence-transformers/all-MiniLM-L6-v2` (Hugging Face) locally. No OpenAI dependency.
3. **Architecture**: FastAPI Backend + Static Frontend (Served together).

### Setup & Run
1. **Get a Groq API Key**: [https://console.groq.com/keys](https://console.groq.com/keys) (It's Free).
2. **Environment**:
   Create a `.env` file in `backend/` or set variables in your terminal/Render dashboard:
   ```bash
   GROQ_API_KEY=gsk_...
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. **Run Server**:
   ```bash
   cd backend
   uvicorn app.main:app --port 5001
   ```

### Deploy to Render
1. Create a **New Web Service** on Render.
2. Connect this repository.
3. Render will automatically detect `render.yaml`.
4. **Important**: Add `GROQ_API_KEY` in the Render Environment Variables settings.
5. Deploy!

### Troubleshooting
- If no API key is provided, the system runs in **Mock Mode**, returning system alerts.