from app.database import SessionLocal, engine
from app.main import seed_database
from app.models import User


def main() -> None:
    from app.database import Base

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).count()
        if existing == 0:
            seed_database()
            print("Database seeded successfully.")
        else:
            print("Database already contains data; skipping seed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
