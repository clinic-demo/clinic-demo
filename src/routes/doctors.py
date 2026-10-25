from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.entity.models import User
from src.repository.clinic import get_free_slots_for_doctor, list_doctors
from src.routes.deps import get_current_user
from src.schemas.clinic import DoctorOut, SlotOut

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=list[DoctorOut])
def list_doctors_endpoint(q: Optional[str] = None, specialty: Optional[str] = None, db: Session = Depends(get_db)):
    rows = list_doctors(db, q=q, specialty=specialty)
    return [
        DoctorOut(id=row.id, name=row.user.name, specialty=row.specialty, room=row.room)
        for row in rows
    ]


@router.get("/{doctor_id}/slots", response_model=list[SlotOut])
def get_slots(doctor_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    slots = get_free_slots_for_doctor(db, doctor_id)
    return [
        SlotOut(id=s.id, doctor_id=s.doctor_id, start_time=s.start_time, end_time=s.end_time, is_available=s.is_available)
        for s in slots
    ]
