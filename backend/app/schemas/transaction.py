from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.transaction import TransactionType

class TransactionCreate(BaseModel):
    amount: float=Field(...,gt=0, 
            description="Amount must be more than 0!")
    type: TransactionType
    category: str=Field(...,min_length=1, max=100)
    description: Optional[str] = Field(None, max_length=500)
    date: datetime

    class Config:
        json_schema_extra = {
            "example":{
                "amount":200,
                "type":"expense",
                "category":"Food",
                "description": "Daily needs",
                "date": "2025-09-30T10:30:00"
            }
        }

class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[datetime] = None

class TransactionResponse(BaseModel):
    """
    Schema for returning transaction data
    """
    id: int
    user_id: int
    amount: float
    type: TransactionType
    category: str
    description: Optional[str]
    date: datetime
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class TransactionSummary(BaseModel):
    """
    Schema for financial summary
    """
    total_income: float
    total_expenses: float
    net_savings: float
    transaction_count: int