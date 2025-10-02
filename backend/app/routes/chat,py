from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from app.models.user import User
from app.services.chatbot_service import ChatbotService
from app.utils.dependencies import get_current_user

router = APIRouter(
    prefix="/chat",
    tags=["Chatbot"]
)

@router.post("/", response_model=ChatResponse)
def send_message(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the chatbot and get a response
    
    **Protected route** - requires authentication
    
    Examples:
    - "What's my balance?"
    - "How much did I spend on food?"
    - "Show my recent transactions"
    - "Give me savings tips"
    """
    response = ChatbotService.process_message(db, current_user, chat_request.message)
    return response

@router.get("/history", response_model=List[ChatHistoryResponse])
def get_chat_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's chat history
    
    **Protected route** - requires authentication
    """
    messages = ChatbotService.get_chat_history(db, current_user, limit)
    return messages