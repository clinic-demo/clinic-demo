# Clinic Demo

Навчальний сервіс запису до клініки з FastAPI, SQLite, JWT та ШІ-асистентом на базі `mock_llm.py`.

## Опис

Проєкт реалізує сценарій клініки:
- реєстрація та логін користувачів;
- профіль пацієнта;
- пошук лікарів і перегляд вільних слотів;
- запис пацієнта на прийом;
- нотатки лікаря після візиту;
- завантаження та перегляд документів пацієнта;
- адмін-панель для управління ролями;
- асистент `/assistant/chat` зі 5 інструментами та захистом від prompt-injection.

## Технології

- Python 3.12
- FastAPI
- SQLite
- SQLAlchemy
- JWT
- pytest
- Docker + Docker Compose

## Швидкий запуск

### 1. Віртуальне середовище

```bash
cd clinic-demo
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Заповнення змінних середовища

Скопіюйте приклад:

```bash
cp .env.example .env
```

### 3. Запуск API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API доступне на:
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 4. Запуск через Docker

```bash
docker compose up --build
```

## Seed-дані

Seed-скрипт створює базу даних і наповнює її синтетичними даними.

```bash
python seed.py
```

## Тестові облікові записи

Після seed-скрипта доступні такі користувачі:

- admin@clinic.demo / admin123
- doctor.seed@example.com / doctor123
- doctor2.seed@example.com / doctor123
- doctor3.seed@example.com / doctor123
- patient1@example.com / pass123
- patient2@example.com / pass123
- patient3@example.com / pass123
- patient4@example.com / pass123
- patient5@example.com / pass123

## Тести

```bash
pytest -q
```

Це вимагає, щоб тестовий набір використовував SQLite test DB і перевіряв основні сценарії API.

## Структура проєкту

```text
clinic-demo/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── services.py
│   └── mock_llm_adapter.py
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── mock_llm.py
├── PROMPTS.md
├── README.md
├── requirements.txt
├── seed.py
├── SPEC.md
└── pytest.ini
```

## Примітки

- У репозиторії немає реальних секретів або API-ключів.
- Усі чутливі значення повинні передаватися через `.env` або змінні середовища.
- ШІ-асистент використовує модуль `mock_llm.py` без змін.
