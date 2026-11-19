
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

from app.database import get_db
from app.models.user import User
from app.auth_security import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# REQUEST MODELS

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# REGISTER

@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):

    email = str(data.email).lower()

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = pwd_context.hash(data.password)

    user = User(
        name=data.name,
        email=email,
        password_hash=hashed_password,
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Registration successful",
        "user_id": user.id,
        "name": user.name,
        "role": user.role
    }


# LOGIN

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    email = str(data.email).lower()

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user or not pwd_context.verify(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }
