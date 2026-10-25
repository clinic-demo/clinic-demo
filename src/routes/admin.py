from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.entity.models import User
from src.repository.clinic import ensure_admin, list_all_users, update_user_role
from src.routes.deps import get_current_user
from src.schemas.clinic import UserOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def admin_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ensure_admin(current_user)
    return list_all_users(db)


@router.patch("/users/{user_id}", response_model=UserOut)
def admin_update_user(user_id: int, payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ensure_admin(current_user)
    role = payload.get("role")
    if role not in {"patient", "doctor", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    return update_user_role(db, user_id, role)
