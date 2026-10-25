import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def get_env(name: str, default: str) -> str:
    return os.getenv(name, default)


APP_ENV = get_env("APP_ENV", "dev")
DATABASE_URL = get_env("APP_DATABASE_URL", f"sqlite:///{BASE_DIR / 'clinic.db'}")
SECRET_KEY = get_env("APP_SECRET_KEY", "dev-secret-key-change")
LLM_PROVIDER = get_env("LLM_PROVIDER", "mock").lower()
DOCUMENTS_DIR = BASE_DIR / "storage" / "documents"
