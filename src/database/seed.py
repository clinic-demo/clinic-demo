from __future__ import annotations

from src.conf.config import DOCUMENTS_DIR
from src.database.db import Base, SessionLocal, engine
from src.entity.models import Appointment, Document, Doctor, Slot, VisitNote
from src.repository.clinic import create_user


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed_database(db=None) -> None:
    close = False
    if db is None:
        db = SessionLocal()
        close = True
    try:
        create_user(db, "admin@clinic.demo", "admin123", "System Admin", role="admin")
        doctor_specs = [
            ("doctor.seed@example.com", "doctor123", "Dr Anna Petrova", "Cardiology", "A-101"),
            ("doctor2.seed@example.com", "doctor123", "Dr Ben Ivanov", "Neurology", "B-205"),
            ("doctor3.seed@example.com", "doctor123", "Dr Clara Sidorova", "Dermatology", "C-303"),
        ]
        doctors = []
        for email, password, name, specialty, room in doctor_specs:
            user = create_user(db, email, password, name, role="doctor")
            doctor = Doctor(user_id=user.id, specialty=specialty, room=room)
            db.add(doctor)
            db.commit()
            db.refresh(doctor)
            doctors.append(doctor)

        patient_specs = [
            ("patient1@example.com", "pass123", "Eva Patient"),
            ("patient2@example.com", "pass123", "Mila Patient"),
            ("patient3@example.com", "pass123", "Lena Patient"),
            ("patient4@example.com", "pass123", "Olia Patient"),
            ("patient5@example.com", "pass123", "Nora Patient"),
        ]
        patients = [create_user(db, email, password, name, role="patient") for email, password, name in patient_specs]

        for doctor in doctors:
            for day_offset in range(0, 7):
                db.add(
                    Slot(
                        doctor_id=doctor.id,
                        start_time=f"2026-10-{10 + day_offset:02d}T09:00:00",
                        end_time=f"2026-10-{10 + day_offset:02d}T09:30:00",
                        is_available=True,
                    )
                )
            db.commit()

        all_slots = db.query(Slot).all()
        for i in range(4):
            slot = all_slots[i]
            slot.is_available = False
            db.add(Appointment(patient_id=patients[i % len(patients)].id, slot_id=slot.id, status="scheduled"))
        db.commit()

        notes = [
            (patients[0].id, doctors[0].id, "Routine exam", "Patient reported mild fatigue, advised rest.", "2026-10-15"),
            (patients[1].id, doctors[1].id, "Neurology follow-up", "Symptoms improved; continue same regimen.", "2026-10-16"),
            (patients[2].id, doctors[0].id, "Cardiology review", "No acute issues, recommended hydration.", "2026-10-18"),
        ]
        for patient_id, doctor_id, summary, details, visit_date in notes:
            db.add(VisitNote(patient_id=patient_id, doctor_id=doctor_id, summary=summary, details=details, visit_date=visit_date))
        db.commit()

        docs_dir = DOCUMENTS_DIR
        docs_dir.mkdir(parents=True, exist_ok=True)
        sample_texts = {
            "lab_report.txt": "Patient labs: WBC 5.0, RBC 4.7. Clinical status stable.",
            "summary.txt": "Follow-up note: continues medication and hydration plan.",
        }
        for filename, content in sample_texts.items():
            file_path = docs_dir / filename
            file_path.write_text(content, encoding="utf-8")
            db.add(
                Document(
                    patient_id=patients[0].id,
                    filename=filename,
                    content_type="text/plain",
                    file_path=str(file_path),
                    file_size=file_path.stat().st_size,
                    summary="Sample clinical summary",
                )
            )
        db.commit()
    finally:
        if close:
            db.close()
