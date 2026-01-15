import os
import json
import uuid
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
You are 'EduCore' (Sahayak.AI), an advanced open-source educational AI engine.

MODE 1: CONVERSATION (Default)
- Reply naturally in the User's Language.
- **STYLE ADAPTATION CRITICAL**: Analyze the User's tone, vocabulary, and sentence structure. 
  - If they are formal/academic -> Be academic and profound.
  - If they are casual/slang -> Be casual and relatable.
  - If they are simple/childlike -> Be encouraging and simple.
  - **MIRROR THEIR INTELLECTUAL LEVEL.**
- Do NOT use JSON for normal chat. Just talk.

MODE 2: TOOLS (Action Required)
- If you need to generate Media or Documents, you MUST output a single valid JSON object.
- JSON Schema:
{
  "tool_used": "mermaid" | "image_prompt" | "video_prompt" | "youtube_search" | "presentation" | "document",
  "data": <content_string_or_object>,
  "metadata": { "topic": "summary", "audience_level": "child"|"teacher" }
}

TOOLS:
1. "mermaid": ONLY strict Mermaid code (graph TD).
2. "image_prompt": English prompt for Image Gen.
3. "video_prompt": English prompt for Video Gen.
4. "youtube_search": Search query.
5. "presentation": Presentation Title.
6. "document": Document Content.

CAPABILITIES:
- You CAN generate images, videos, and search YouTube.
- NEVER say "I cannot". Use the appropriate JSON tool.
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
        # Construct Messages
        messages = [{"role": "system", "content": MASTER_PROMPT}] + history
        
        # HYBRID MODE: No response_format forced. We parse the result.
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        content_str = completion.choices[0].message.content
        
        # 1. Try JSON Parse (Tool Usage)
        try:
            # Helper to find JSON substring if mixed content
            # (Simple heuristic: if it looks like JSON start/end)
            response_data = json.loads(content_str)
            
            # Allow pure text response to be treated as text
            if "tool_used" not in response_data:
                 raise ValueError("Not a tool response")
                 
        except Exception:
            # 2. Fallback to TEXT (Conversation)
            response_data = {
                "tool_used": "text",
                "data": content_str,
                "metadata": {}
            }
        
        # Add AI Response to History
        ai_text = str(response_data.get("data", ""))
        SESSION_STORE[user_id].append({"role": "assistant", "content": ai_text})
        
        return response_data

    except Exception as e:
        print(f"Groq Error: {e}")
        return {"tool_used": "text", "data": f"Error: {str(e)}", "metadata": {}}

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
