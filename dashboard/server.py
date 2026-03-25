import os
import sys
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

# Add parent directory to path to allow importing agent.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import run_pipeline, get_history, save_to_history, CLAUDE_AVAILABLE, GEMINI_AVAILABLE, OPENAI_AVAILABLE

app = FastAPI(title="Nextdot AI Agent API")

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origin
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessRequest(BaseModel):
    message: str
    model: str = "claude"  # "claude", "gemini", or "both"
    label: Optional[str] = "web_input"

@app.get("/")
async def root():
    return {
        "status": "online",
        "models": {
            "claude": CLAUDE_AVAILABLE,
            "gemini": GEMINI_AVAILABLE,
            "openai": OPENAI_AVAILABLE
        }
    }

@app.post("/process")
async def process_message(req: ProcessRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        result = run_pipeline(req.message, label=req.label, model=req.model, save_output=True)
        # result is a dict (or dict of dicts if model="both")
        save_to_history(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def history():
    return get_history()

if __name__ == "__main__":
    import uvicorn
    # Use the port specified in environment variables for deployment, fallback to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
