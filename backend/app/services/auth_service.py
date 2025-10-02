from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.security import hash_password, verify_password, create_access_token
from datetime import timedelta
from app.config import get_settings

setting= get_settings()

class AuthService:
    """Service layer for handling authentication and authorization.
    Separates business logic from routes.
    """
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """ Register a user 
        Input: db:Session, user_data: Validating user data from the UserCreate schema
        Output: User: The created user object
        else raises HTTPException if user already exists
        """
        existing_user=db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        hashed_pass = hash_password(user_data.password)

        new_user = User(
            email=user_data.email,
            hashed_password=hashed_pass,
            full_name=user_data.full_name
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    @staticmethod
    def login_user(db: Session, login_data: UserLogin)->dict:
        """Input
        db: Session , login_Data: from UserLogin schema
        Output: Dict with access token and token type
        db: Session , login_Data: from UserLogin schema
        Output: Dict with access token and token type
        else raises HTTPException if credentials are invalid
        """

        user = db.query(User).filter(User.email == login_data.email).first()
        
        # Check if user exists and password is correct
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    @staticmethod
    def get_current_user(db: Session, user_id: int) -> User:
        """
        Get user by ID (used for protected routes)
        Input:
            db: Database session
            user_id: User ID from JWT token  
        Output: User object
        else Raises: HTTPException: If user not found
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
