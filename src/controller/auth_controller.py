from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database.core import get_db
from ..services.user_service import UserService
from ..services.auth_service import AuthService
from ..services.schemas import UserCreate, UserLogin, UserResponse
from ..exceptions.user_exceptions import UserAlreadyExistsError, InvalidCredentialsError
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, service: UserService = Depends(get_user_service)):
    """Register a new user"""
    user = service.create_user(user_data)
    return user

@router.post("/login")
def login(user_data: UserLogin, service: UserService = Depends(get_user_service)):
    """Login user and return JWT token"""
    user = service.authenticate_user(user_data)
    
    # Create token
    access_token = AuthService.create_access_token(
        data={"user_id": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    }