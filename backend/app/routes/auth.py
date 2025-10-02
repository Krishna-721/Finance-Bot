from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix='/auth',
    tags=["Authentication"]
)

@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate, db: Session = Depends(get_db)):
    """Registering a new user needs: email, fullname, password (min 8 characters)"""
    user= AuthService.register_user(db, user_data)
    return user

@router.post('/login')
def login(login_data: UserLogin, db:Session = Depends(get_db)):
    """Login needs email, password
    returns jwt tokens for authenticated requests"""
    result = AuthService.login_user(db, login_data)
    return {
        "access_token": result["access_token"],
        "token_type": result["token_type"],
        "user": UserResponse.from_orm(result["user"])
    }

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile
    
    **Protected route** - requires valid JWT token
    """
    return current_user