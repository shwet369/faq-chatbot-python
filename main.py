from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import os
from typing import Optional
import json
from faq_data import LOCAL_FAQ

app = FastAPI()

# Hugging Face API (FREE - no credit card needed)
# Get your free token at: https://huggingface.co/settings/tokens
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "YOUR_FREE_HUGGINGFACE_TOKEN")
HF_MODEL = "microsoft/DialoGPT-medium"  # Free conversational model

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str
    source: str

def get_local_faq_answer(question: str) -> Optional[str]:
    """Check local FAQ first (faster, no API call)"""
    question_lower = question.lower()
    for faq in LOCAL_FAQ:
        for keyword in faq["keywords"]:
            if keyword.lower() in question_lower:
                return faq["answer"]
    return None

def get_ai_answer(question: str) -> str:
    """Use Hugging Face free API for intelligent answers"""
    if not HF_API_TOKEN or HF_API_TOKEN == "YOUR_FREE_HUGGINGFACE_TOKEN":
        return "Please set up your free Hugging Face token to enable AI answers. Contact support@example.com for now."
    
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    # For FAQ-style responses
    payload = {
        "inputs": f"Question: {question}\nAnswer:",
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            # Extract generated text
            if isinstance(result, list) and len(result) > 0:
                answer = result[0].get("generated_text", "").strip()
                if answer:
                    return answer
        
        # Fallback to a different free model
        return get_fallback_ai_answer(question)
    
    except Exception as e:
        print(f"AI Error: {e}")
        return "I'm having trouble connecting to AI. Please try again or contact support@example.com."

def get_fallback_ai_answer(question: str) -> str:
    """Backup: Use free Hugging Face QA model"""
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    # Using BERT-based QA model
    payload = {
        "inputs": {
            "question": question,
            "context": "This is a customer support chatbot for an online store. We offer shipping within 3-5 days, 30-day returns, and 24/7 email support at support@example.com."
        }
    }
    
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/bert-large-uncased-whole-word-masking-finetuned-squad",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("answer", "I found a partial answer. Please contact support for details.")
    except:
        pass
    
    return "I couldn't find a specific answer. Please email support@example.com for help."

@app.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    """Main endpoint to get answers"""
    # First check local FAQ
    local_answer = get_local_faq_answer(question.question)
    if local_answer:
        return Answer(answer=local_answer, source="local_faq")
    
    # Then try AI
    ai_answer = get_ai_answer(question.question)
    return Answer(answer=ai_answer, source="ai")

@app.get("/")
async def serve_frontend():
    """Serve the chat interface"""
    return FileResponse("static/index.html")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Health check for deployment
@app.get("/health")
async def health_check():
    return {"status": "healthy"}