from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import logging

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
DEFAULT_EMAIL = os.getenv("DEFAULT_EMAIL", "agraharivishal19981@gmail.com")
ORCHESTRATOR_SCRIPT = "orchestrator.py"
DATA_DIR = Path("data")

class AnalyzeRequest(BaseModel):
    window_days: int
    email: str = ""

def find_latest_pulse_file():
    """Find the most recently created review_pulse_*.json file"""
    pulse_files = list(DATA_DIR.glob("review_pulse_*.json"))
    if not pulse_files:
        return None
    return max(pulse_files, key=lambda p: os.path.getctime(str(p)))

@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    """Run orchestrator and send emails"""
    
    # Validate window_days
    if not isinstance(request.window_days, int) or request.window_days < 7 or request.window_days > 35:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "window_days must be between 7 and 35 (1-5 weeks)."}
        )
    
    user_email = request.email.strip() if request.email else None
    
    # Validate email format if provided
    if user_email and "@" not in user_email:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Invalid email format."}
        )
    
    try:
        logger.info(f"Running orchestrator with window_days={request.window_days}, email={user_email}")
        
        # Build email list
        emails_to_send = [DEFAULT_EMAIL]
        if user_email and user_email != DEFAULT_EMAIL:
            emails_to_send.append(user_email)
        
        email_arg = ",".join(emails_to_send)
        
        # Run orchestrator
        cmd = [
            "python",
            ORCHESTRATOR_SCRIPT,
            "--window-days",
            str(request.window_days)
        ]
        
        env = os.environ.copy()
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if not gemini_key:
            raise Exception("GEMINI_API_KEY environment variable is not set. Please set it before running.")
        env["GEMINI_API_KEY"] = gemini_key
        env["TO_EMAILS"] = email_arg
        
        logger.info(f"Using GEMINI_API_KEY: {gemini_key[:10]}...")
        logger.info(f"Email recipients: {email_arg}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=900)
        
        if result.returncode != 0:
            logger.error(f"Orchestrator failed with return code {result.returncode}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            raise Exception(f"Orchestrator execution failed: {result.stderr}")
        
        logger.info("Orchestrator completed successfully")
        
        # Find and load the latest pulse file
        pulse_file = find_latest_pulse_file()
        if not pulse_file:
            raise Exception("No pulse file found in data directory")
        
        with open(pulse_file, 'r', encoding='utf-8') as f:
            pulse_data = json.load(f)
        
        return {
            "status": "success",
            "message": "Weekly pulse generated and emails sent.",
            "window_days": request.window_days,
            "pulse_file_name": pulse_file.name,
            "pulse_data": {
                "start_date": pulse_data.get("start_date"),
                "end_date": pulse_data.get("end_date"),
                "top_themes": pulse_data.get("top_themes", []),
                "quotes": pulse_data.get("quotes", []),
                "action_ideas": pulse_data.get("action_ideas", []),
                "note_markdown": pulse_data.get("note_markdown", "")
            }
        }
    
    except subprocess.TimeoutExpired:
        logger.error("Orchestrator timeout (15 minutes exceeded)")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": "Analysis timeout (15 minutes). Please try with a shorter time window."}
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )

@app.get("/api/download-pulse")
async def download_pulse(file: str):
    """Download pulse file"""
    
    # Validate file name to prevent path traversal
    if not file.startswith("review_pulse_") or ".." in file:
        raise HTTPException(status_code=400, detail="Invalid file name")
    
    pulse_path = DATA_DIR / file
    
    if not pulse_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        pulse_path,
        media_type="application/json",
        filename=file
    )

# Serve static frontend files (if dist folder exists)
if Path("frontend/dist").exists():
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
