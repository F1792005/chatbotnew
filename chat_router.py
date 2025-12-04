from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from chat_service import CVChatService
import logging
import os

app = FastAPI(title="CV Chat Assistant")
logger = logging.getLogger(__name__)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

svc = CVChatService()


class ChatRequest(BaseModel):
    question: str
    include_thinking: bool = True


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    """Chat endpoint that returns thinking process and answer.
    
    Request:
        {
            "question": "string",
            "include_thinking": true/false (optional, default: true)
        }
    
    Response:
        {
            "thinking": "string (quá trình suy nghĩ)",
            "answer": "string (câu trả lời)"
        }
    """
    result = svc.generate_response(req.question, req.include_thinking)
    return result


@app.get("/suggestions")
def suggestions():
    """Get suggested questions based on CV content."""
    return svc.get_suggested_questions()

# Mount frontend static files
# This must be after API routes to avoid conflicts
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")



@app.get("/suggestions")
def get_suggestions():
    """Get suggested questions for the CV assistant.
    
    Response:
        {
            "suggestions": ["question1", "question2", ...]
        }
    """
    suggestions = svc.get_suggested_questions()
    return {"suggestions": suggestions}
