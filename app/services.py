from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Appointment, Doctor, Document, Slot, User, VisitNote
from app.security import hash_password, verify_password


def create_user(db: Session, email: str, password: str, name: str, role: str = "patient") -> User:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=email, password_hash=hash_password(password), name=name, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def list_doctors(db: Session, q: Optional[str] = None, specialty: Optional[str] = None):
    query = db.query(Doctor).join(User, Doctor.user_id == User.id)
    if q:
        query = query.filter(User.name.ilike(f"%{q}%"))
    if specialty:
        query = query.filter(Doctor.specialty.ilike(f"%{specialty}%"))
    return query.all()


def get_free_slots_for_doctor(db: Session, doctor_id: int):
    return db.query(Slot).filter(Slot.doctor_id == doctor_id, Slot.is_available.is_(True)).all()


def create_appointment(db: Session, patient_id: int, slot_id: int) -> Appointment:
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    if not slot.is_available:
        raise HTTPException(status_code=400, detail="Slot unavailable")
    existing = db.query(Appointment).filter(Appointment.slot_id == slot_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slot already booked")
    appointment = Appointment(patient_id=patient_id, slot_id=slot_id, status="scheduled")
    slot.is_available = False
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def list_user_appointments(db: Session, patient_id: int):
    return db.query(Appointment).filter(Appointment.patient_id == patient_id).all()


def get_appointment(db: Session, appointment_id: int, patient_id: Optional[int] = None):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if patient_id is not None and appointment.patient_id != patient_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return appointment


def cancel_appointment(db: Session, appointment_id: int, patient_id: int):
    appointment = get_appointment(db, appointment_id, patient_id)
    appointment.status = "cancelled"
    if appointment.slot:
        appointment.slot.is_available = True
    db.commit()
    return appointment


def list_notes_for_patient(db: Session, patient_id: int):
    return db.query(VisitNote).filter(VisitNote.patient_id == patient_id).all()


def create_note_for_patient(db: Session, doctor_id: int, patient_id: int, summary: str, details: str, visit_date: str):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    note = VisitNote(
        patient_id=patient_id,
        doctor_id=doctor_id,
        summary=summary,
        details=details,
        visit_date=visit_date,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def create_document(db: Session, patient_id: int, filename: str, content_type: str, file_path: str, file_size: int, summary: Optional[str] = None):
    doc = Document(
        patient_id=patient_id,
        filename=filename,
        content_type=content_type,
        file_path=file_path,
        file_size=file_size,
        summary=summary,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document(db: Session, document_id: int, patient_id: Optional[int] = None):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if patient_id is not None and doc.patient_id != patient_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return doc


def list_all_users(db: Session):
    return db.query(User).all()


def update_user_role(db: Session, user_id: int, role: str):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    db.commit()
    db.refresh(user)
    return user


def ensure_admin(user):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")


def ensure_patient(user):
    if user.role not in {"patient", "admin"}:
        raise HTTPException(status_code=403, detail="Forbidden")


def ensure_doctor(user):
    if user.role != "doctor":
        raise HTTPException(status_code=403, detail="Forbidden")
