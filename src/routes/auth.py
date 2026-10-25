from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.entity.models import User
from src.repository.clinic import create_user
from src.schemas.clinic import AuthResponse, UserCreate, UserLogin
from src.services.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_data.email, user_data.password, user_data.name, user_data.role or "patient")
    token = create_access_token(str(user.id), user.role)
    return AuthResponse(access_token=token, user=user)


@router.post("/login", response_model=AuthResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user.id), user.role)
    return AuthResponse(access_token=token, user=user)
