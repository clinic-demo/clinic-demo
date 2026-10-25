from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.entity.models import User
from src.routes.deps import get_current_user
from src.schemas.clinic import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def patch_my_profile(update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if update.name is not None:
        current_user.name = update.name
    if update.phone is not None:
        current_user.phone = update.phone
    db.commit()
    db.refresh(current_user)
    return current_user
