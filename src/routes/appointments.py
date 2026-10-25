from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.entity.models import User
from src.repository.clinic import (
    cancel_appointment,
    create_appointment,
    get_appointment,
    list_user_appointments,
)
from src.routes.deps import get_current_user
from src.schemas.clinic import AppointmentCreate, AppointmentOut

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentOut)
def create_appointment_endpoint(data: AppointmentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can book appointments")
    return create_appointment(db, current_user.id, data.slot_id)


@router.get("", response_model=list[AppointmentOut])
def list_appointments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can view appointments")
    return list_user_appointments(db, current_user.id)


@router.get("/{appointment_id}", response_model=AppointmentOut)
def read_appointment(appointment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can view appointments")
    return get_appointment(db, appointment_id, current_user.id)


@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can cancel appointments")
    cancel_appointment(db, appointment_id, current_user.id)
    return {"status": "cancelled", "appointment_id": appointment_id}
