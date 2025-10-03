from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ChatRequest(BaseModel):
    '''User's message! '''
    message:str =Field(...,min_length=1, max_length=100)

    class Config:
        json_schema_extra= {
            "example":{
                "message":"How much did I spend this month?"
            }
        }
        
class ChatResponse(BaseModel):
    """Reply from the bot! """
    user_message: str
    bot_response: str
    intent: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes=True

class ChatHistoryResponse(BaseModel):
    """one chat's message from history"""
    id:int
    user_message:str
    bot_response:str
    intent: Optional[str]
    created_at:datetime

    class Config:
        from_attributes=True