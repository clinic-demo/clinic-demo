"""Populate the database with demo data.

Usage (from repo root):
    python scripts/seed.py           # create tables and seed if empty
    python scripts/seed.py --reset   # drop everything and reseed
"""
from __future__ import annotations

import sys
from pathlib import Path

# дозволяє запуск як `python scripts/seed.py` з кореня репозиторію
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database.db import Base, SessionLocal, engine  # noqa: E402
from src.database.seed import reset_database, seed_database  # noqa: E402
from src.entity.models import User  # noqa: E402


def main() -> None:
    if "--reset" in sys.argv:
        reset_database()
        seed_database()
        print("Database reset and seeded.")
        return

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            seed_database(db)
            print("Database seeded.")
        else:
            print("Database already has data; nothing to do (use --reset to reseed).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
