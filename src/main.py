from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database.db import Base, SessionLocal, engine
from src.database.seed import seed_database
from src.entity.models import User
from src.routes import (
    admin,
    appointments,
    assistant,
    auth,
    doctors,
    documents,
    health,
    notes,
    users,
)

app = FastAPI(title="Clinic Demo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (health, auth, users, doctors, appointments, notes, documents, admin, assistant):
    app.include_router(module.router)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            seed_database(db)
    finally:
        db.close()
