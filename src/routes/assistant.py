from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.entity.models import User
from src.routes.deps import get_current_user
from src.schemas.clinic import ChatRequest
from src.services.assistant import run_assistant

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat")
def assistant_chat(request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return run_assistant(request.message, current_user, db)
