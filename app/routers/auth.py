from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    grade: int
    school: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register_user(user: UserCreate):
    """Register a new student user"""
    return {
        "message": "User registration endpoint",
        "user_email": user.email,
        "status": "coming_soon"
    }

@router.post("/login")
async def login_user(credentials: UserLogin):
    """Login user and return JWT token"""
    return {
        "message": "User login endpoint", 
        "email": credentials.email,
        "status": "coming_soon"
    }

@router.get("/me")
async def get_current_user():
    """Get current user profile"""
    return {
        "message": "Current user endpoint",
        "status": "coming_soon"
    }
