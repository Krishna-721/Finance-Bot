from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel): # Requesting the backend
    """
    Schema for creating a new user
    Frontend sends data to backend
    """
    email: EmailStr
    password: str = Field(min_length=8, max_length=12)
    full_name: str = Field(min_length=2, max_length=100)

class Config:
    json_schema_extra = {
        "example": {
                "email": "john@example.com",
                "password": "securepassword123",
                "full_name": "John Doe"
            }
    }

class UserLogin(BaseModel): 
    """
    Schema for user login
    Frontend sends data to backend
    """
    email: EmailStr
    password: str = Field(min_length=8, max_length=12)

class UserResponse(BaseModel): # Responding from backend and never send the password to the frontend
    """ User gets response from backend 
    or Backend sends data to frontend
    """
    id: int
    email: EmailStr 
    full_name: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  #Sqlalchemy model to Pydantic model
