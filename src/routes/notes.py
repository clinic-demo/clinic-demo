from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.entity.models import User
from src.repository.clinic import create_note_for_patient, list_notes_for_patient
from src.routes.deps import get_current_user
from src.schemas.clinic import VisitNoteCreate, VisitNoteOut

router = APIRouter(prefix="/patients", tags=["notes"])


@router.get("/{patient_id}/notes", response_model=list[VisitNoteOut])
def get_notes(patient_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can view notes")
    return list_notes_for_patient(db, patient_id)


@router.post("/{patient_id}/notes", response_model=VisitNoteOut)
def add_note(
    patient_id: int,
    note_data: VisitNoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can create notes")
    return create_note_for_patient(db, current_user.id, patient_id, note_data.summary, note_data.details, note_data.visit_date)
