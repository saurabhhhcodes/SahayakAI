import os
import json
import uuid
import csv
from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import Utils (Ensure these exist/work)
from app.utils.media_generator import MediaGenerator
from app.utils.image_generator import image_gen

app = FastAPI(title="Sahayak.AI EduCore", version="2.0.0")

# --- CONFIGURATION ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") 
HF_TOKEN = os.environ.get("HF_TOKEN", "hf_...")       

try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Groq Init Warning: {e}")
    groq_client = None

# Mount Frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MASTER SYSTEM PROMPT ---
MASTER_PROMPT = """
### SYSTEM INSTRUCTION: Sahayak.AI (Teacher Support Agent)
**IDENTITY & MISSION**
You are **Sahayak**, an empathetic, intelligent, and pedagogical AI companion designed for Indian school teachers. Your mission is to provide "just-in-time" support to teachers.

**OPERATIONAL CONTEXT**
* **Users:** School teachers in India (Namaste / Hinglish friendly).
* **Tone:** Professional, Encouraging, Solution-Oriented.
* **Format:** Markdown (use **bold** for key concepts).

**CORE GUIDELINES (STRICT ADHERENCE)**
1.  **Pedagogy Over Content**: Explain *how to teach*, not just *what it is*.
2.  **Native Language First**: NEVER use English transliteration for Indian languages.
    *   **Hindi**: Use Devanagari (नमस्ते), NOT "Namaste".
    *   **Bengali**: Use Bengali Script (নমস্কার).
    *   **Tamil**: Use Tamil Script (வணக்கம்).
3.  **Real Media First**:
    *   If explaining a concept (e.g., "Gravity", "Python"), prefer finding **Real Videos** (`youtube_search`) over generating fake ones.
    *   Only use `image_prompt` / `video_prompt` when the user explicitly asks to *create* something new or fictional.
4.  **Safety & Ethics (ZERO TOLERANCE)**:
    *   **Prohibited**: NSFW, Violence, Self-harm, Substance Abuse.
    *   **Refusal**: Firmly refuse unsafe requests.
5.  **Hide the Plumbing**: NEVER output raw JSON to the user.

**TOOL USAGE (JSON MODE)**
To generate Media or Files, you MUST output a Single Valid JSON Block.
JSON Schema:
{
  "tool_used": "mermaid" | "image_prompt" | "video_prompt" | "youtube_search" | "presentation" | "document" | "csv" | "docx" | "excel",
  "data": <content_string_or_object>,
  "metadata": { "topic": "summary", "audience_level": "child"|"teacher" }
}

**TOOLS AVALIABLE:**
1. "mermaid": Flowcharts/Diagrams (graph TD).
2. "image_prompt": Safe, Educational Image Generation.
3. "video_prompt": Educational Video Generation.
4. "youtube_search": Search Keyword (e.g., "Gravity for kids"). NEVER provide a URL.
5. "presentation": Lesson Plan Slides.
6. "document": PDF Handouts.
7. "csv": Structured Data (CSV).
8. "docx": Word Documents.
9. "excel": Excel Spreadsheets.

**CAPABILITIES:**
- **Math/Science**: Always use **LaTeX** for formulas ($$ E=mc^2 $$).
- **Scope**: Adjust depth for UKG (Fun) to Graduate (Deep).

**INTERACTION FLOW**
1.  **Acknowledge**: Validate the teacher's struggle.
2.  **Diagnose**: Ask clarifying questions if needed.
3.  **Solution**: Provide a specific, bite-sized strategy.

**CURRENT STATE:**
You are online. Await the teacher's input.
"""

class QueryRequest(BaseModel):
    text: str
    user_id: str = "guest"

# In-Memory Session Store
SESSION_STORE = {}

@app.post("/chat")
async def chat_handler(request: QueryRequest):
    if not groq_client:
        return {"tool_used": "text", "data": "Groq API Key missing.", "metadata": {}}

    user_id = request.user_id
    if user_id not in SESSION_STORE:
        SESSION_STORE[user_id] = []
    
    # Add User Message to History
    SESSION_STORE[user_id].append({"role": "user", "content": request.text})
    
    # Limit context window (last 10 messages)
    history = SESSION_STORE[user_id][-10:]

    try:
        # --- MULTI-LLM FALLBACK SYSTEM ---
        # Uses LiteLLM to cycle through providers when rate limited
        from app.llm_factory import llm_factory
        
        llm_response = llm_factory.chat(
            messages=history,
            system_prompt=MASTER_PROMPT
        )
        
        if not llm_response.get("success", False):
            # All providers failed - return error message
            return {
                "tool_used": "text",
                "data": llm_response["content"],
                "metadata": {"model_used": "none"}
            }
        
        content_str = llm_response["content"]
        model_used = llm_response.get("model_used", "unknown")
        # 3. Robust JSON Parsing (Handles "Here is the JSON: {...}")
        import re
        try:
            # First, strip markdown code blocks if present
            clean_str = content_str
            if "```" in clean_str:
                matches = re.findall(r"```(?:json)?(.*?)```", clean_str, re.DOTALL)
                if matches:
                    clean_str = matches[0].strip()
            
            # Find the JSON object
            json_match = re.search(r'\{.*\}', clean_str, re.DOTALL)
            parsed_json = None
            
            if json_match:
                try:
                    parsed_json = json.loads(json_match.group(0))
                except:
                    parsed_json = None
            
            if parsed_json and "tool_used" in parsed_json:
                data = parsed_json
            else:
                # If no Valid JSON tool structure found, treat entire string as text.
                # Crucially, ensure we don't accidentally send a JSON-looking string as 'data' if it was meant to be the structure.
                # But since we failed to parse it as structure, it must be content.
                data = {"tool_used": "text", "data": content_str}
                
        except Exception as e:
            print(f"JSON Parse Logic Error: {e}. Fallback to text.")
            data = {"tool_used": "text", "data": content_str}

        # --- TOOL INTERCEPTIONS (Runs regardless of JSON success/fail) ---
        response_data = data
        
        try:
            # Youtube Search: Real Backend Execution
            if response_data.get("tool_used") == "youtube_search":
                query = response_data.get("data", "")
                print(f"Executing Deep YouTube Search for: {query}")
                from app.utils.video_search import video_searcher
                results = video_searcher.search(query)
                # Replace string query with rich object
                response_data["data"] = results 
        except Exception as e:
            print(f"Tool Execution Error: {e}")
            # Keep original data if tool fails

        # Add AI Response to History
        ai_text = str(response_data.get("data", ""))
        SESSION_STORE[user_id].append({"role": "assistant", "content": ai_text})
        
        print(f"DEBUG RESPONSE: {json.dumps(response_data)}") # DEBUG LOG
        return response_data

    except Exception as e:
        print(f"Groq Critical Error: {e}")
        # Final Fallback: Mock Mode (When API is totally dead)
        return {
            "tool_used": "text", 
            "data": "⚠️ **System Alert**: My daily AI fuel (API Limit) is exhausted. I cannot think right now.\n\nPlease update the `GROQ_API_KEY` in your Render settings with a fresh key (it's free!).", 
            "metadata": {}
        }

# --- MEDIA ENDPOINTS ---

# ... imports
from app.utils.video_generator import video_gen

# ... (Previous code)

@app.get("/generate/image")
async def generate_image_endpoint(prompt: str):
    filename = f"img_{uuid.uuid4()}.png"
    filepath = os.path.join("/tmp", filename)
    try:
        image_gen.generate(prompt, filepath)
        return FileResponse(filepath, media_type="image/png")
    except:
        return FileResponse(filepath)

@app.get("/generate/video")
async def generate_video_endpoint(prompt: str):
    filename = f"vid_{uuid.uuid4()}.mp4"
    filepath = os.path.join("/tmp", filename)
    try:
        # Generate video (Blocking, might take 30s+)
        video_gen.generate(prompt, filepath)
        return FileResponse(filepath, media_type="video/mp4")
    except:
        # Fallback or Error
        return JSONResponse({"error": "Video generation failed"}, status_code=500)

class PDFRequest(BaseModel):
    title: str
    content: str
@app.post("/download/pdf")
async def download_pdf(request: PDFRequest):
    filename = f"lesson_{uuid.uuid4()}.pdf"
    filepath = os.path.join("/tmp", filename)
    MediaGenerator.generate_pdf(request.title, request.content, filepath)
    return FileResponse(filepath, media_type='application/pdf', filename=filename)

class PPTRequest(BaseModel):
    title: str
    slides: List[Dict] = []
@app.post("/download/ppt")
async def download_ppt(request: PPTRequest):
    filename = f"pres_{uuid.uuid4()}.pptx"
    filepath = os.path.join("/tmp", filename)
    
    # SMART PPT: If no slides provided, generate them!
    slides_data = request.slides
    if not slides_data:
        print(f"Generating Smart PPT content for: {request.title}")
        try:
            # Generate content using Groq
            ppt_prompt = f"""
            Create a 5-slide educational presentation structure for the topic: '{request.title}'.
            Audience: Students.
            Output JSON ONLY:
            [
                {{"title": "Introduction", "content": ["Point 1", "Point 2"]}},
                {{"title": "Key Concept 1", "content": ["Detail A", "Detail B"]}}
            ]
            """
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": ppt_prompt}],
                response_format={"type": "json_object"}
            )
            # Custom parsing to handle potential deviations
            content_str = completion.choices[0].message.content
            print(f"DEBUG PPT JSON: {content_str[:100]}...") # Log first 100 chars
            
            try:
                data = json.loads(content_str)
                # Normalize data to List[Dict]
                if isinstance(data, list):
                    slides_data = data
                elif isinstance(data, dict):
                    if "slides" in data and isinstance(data["slides"], list):
                        slides_data = data["slides"]
                    else:
                        # Values dump
                        for k, v in data.items():
                            if isinstance(v, list):
                                slides_data = v
                                break
                
                # Validation: Ensure it looks like slides
                valid_slides = []
                for s in slides_data:
                    if isinstance(s, dict) and 'title' in s:
                        # Ensure content is string or list
                        if 'content' not in s: s['content'] = []
                        valid_slides.append(s)
                
                if valid_slides:
                    slides_data = valid_slides
                else:
                    raise ValueError("No valid slides found in JSON")
                    
            except Exception as parse_err:
                print(f"PPT Parsing Error: {parse_err}")
                # Fallback structure
                slides_data = [
                    {"title": request.title, "content": ["AI generated content structure failed.", "Using fallback mode."]},
                    {"title": "Summary", "content": ["Topic: " + request.title]}
                ]

        except Exception as e:
            print(f"Smart PPT Gen Critical Error: {e}")
            slides_data = [{"title": request.title, "content": ["Content generation failed.", "Check logs."]}]

    try:
        MediaGenerator.generate_pptx(request.title, slides_data, filepath)
        return FileResponse(filepath, media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation', filename=filename)
    except Exception as e:
         print(f"PPTX Creation Error: {e}")
         return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/")
async def root_redirect():
    return RedirectResponse(url="/app/")

@app.get("/health")
def health_check():
    return {"status": "ok"}
