from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import os
from typing import Optional
from faq_data import LOCAL_FAQ

app = FastAPI()

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

def get_smart_response(question: str) -> str:
    """Smart responses for common questions not in FAQ"""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ["hi", "hello", "hey", "greetings"]):
        return "👋 Hello! Welcome to our FAQ assistant. How can I help you today? You can ask about hours, returns, shipping, payments, or contact info!"
    
    if any(word in question_lower for word in ["how are you", "how are you doing"]):
        return "🤖 I'm doing great, thank you for asking! I'm here to help with any questions you have about our store."
    
    if any(word in question_lower for word in ["what can you do", "help", "capabilities"]):
        return "💡 I can help you with:\n• Store hours\n• Returns & refunds\n• Shipping & delivery times\n• Payment methods\n• Contact information\n• Product inquiries\nJust ask me anything!"
    
    if any(word in question_lower for word in ["product", "sell", "item", "merchandise", "what do you sell"]):
        return "🛍️ We sell a wide variety of products! Visit our website to browse our complete catalog. Is there something specific you're looking for?"
    
    if any(word in question_lower for word in ["gift", "card", "certificate"]):
        return "🎁 Yes, we offer gift cards from $25 to $200. They're available for purchase on our website!"
    
    if any(word in question_lower for word in ["loyalty", "reward", "program", "membership"]):
        return "⭐ Yes! Join our free loyalty program to earn points on every purchase. Sign up on our website!"
    
    if any(word in question_lower for word in ["solution", "problem", "issue"]):
        return "💡 I'm here to help! Please describe your specific issue, and I'll do my best to assist you."
    
    if any(word in question_lower for word in ["thank", "thanks", "appreciate"]):
        return "😊 You're very welcome! I'm happy to help. Is there anything else you'd like to know?"
    
    if any(word in question_lower for word in ["price", "cost", "how much"]):
        return "💰 Our prices start at $19.99. Check our website for current deals and special offers!"
    
    return "📚 I specialize in questions about hours, returns, shipping, payments, and contact info. Feel free to ask about any of these topics!"

@app.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    """Main endpoint to get answers"""
    print(f"📝 User asked: {question.question}")
    
    # First check local FAQ
    local_answer = get_local_faq_answer(question.question)
    if local_answer:
        print(f"📚 Local FAQ answer sent")
        return Answer(answer=local_answer, source="local_faq")
    
    # Then try smart responses
    smart_answer = get_smart_response(question.question)
    return Answer(answer=smart_answer, source="smart_response")

@app.get("/")
async def serve_frontend():
    """Serve the chat interface"""
    return FileResponse("static/index.html")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}