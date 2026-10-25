# Клініка-демо — навчальний застосунок

> **Увага.** Це навчальний застосунок курсу «Secure Software Development and Integration» (Neoversity).
> Код згенеровано ШІ за технічним завданням і **свідомо не перевірявся на безпеку**: він містить вразливості.
> Не розгортайте його в інтернеті та не використовуйте з реальними даними. Усі дані й облікові записи — синтетичні.
>
> *Intentionally insecure training application: AI-generated and not security-reviewed. Do not deploy it publicly. Synthetic data only.*

## Навіщо він

Протягом курсу ви шукаєте й виправляєте вразливості в коді, який написав ШІ: вручну, сканерами (SAST, SCA, контейнери), у CI/CD і в ШІ-асистенті. Застосунок — спільна точка відліку для всіх лабораторних.

## Як користуватися в курсі

1. **Основний варіант — свій застосунок.** Згенеруйте власний застосунок за [`SPEC.md`](SPEC.md) будь-яким ШІ-асистентом і працюйте з ним.
2. **Запасний варіант — цей репозиторій.** Якщо не встигаєте зробити свій, створіть fork або скопіюйте код і працюйте у своїй копії.
3. Тег **`ai-baseline`** — перша робоча версія від ШІ без жодних правок безпеки (у лабах її називають **baseline-застосунок**). З нею порівнюються всі ваші виправлення.
4. Виправлення робіть **у своїй копії**. Не надсилайте pull request і issues із знайденими вразливостями в цей репозиторій — див. [`SECURITY.md`](SECURITY.md).

## Безпечний запуск

- Запускайте тільки локально або в GitHub Codespaces. У Codespaces порт залишайте **Private**.
- Для локального запуску без Docker використовуйте `--host 127.0.0.1` замість `0.0.0.0`.
- Облікові дані нижче — тестові й існують лише в локальній базі після seed-скрипта.

## Файли курсу

| Файл | Що це |
| --- | --- |
| [`SPEC.md`](SPEC.md) | Технічне завдання, за яким згенеровано застосунок |
| [`mock_llm.py`](mock_llm.py) | Навчальна заглушка LLM: працює без API-ключа, поводиться передбачувано і **навмисно наївна**. Не змінюйте її |
| [`PROMPTS.md`](PROMPTS.md) | Промпти, якими створено застосунок |

---

## Опис від ШІ (не перевірено)

Нижче — README, який згенерував ШІ разом із кодом. Ми залишили його без змін: не всі твердження в ньому правдиві, і перевірити їх — теж частина курсу.

Навчальний сервіс запису до клініки з FastAPI, SQLite, JWT та ШІ-асистентом на базі `mock_llm.py`.

### Опис

Проєкт реалізує сценарій клініки:
- реєстрація та логін користувачів;
- профіль пацієнта;
- пошук лікарів і перегляд вільних слотів;
- запис пацієнта на прийом;
- нотатки лікаря після візиту;
- завантаження та перегляд документів пацієнта;
- адмін-панель для управління ролями;
- асистент `/assistant/chat` зі 5 інструментами та захистом від prompt-injection.

### Технології

- Python 3.12
- FastAPI
- SQLite
- SQLAlchemy
- JWT
- pytest
- Docker + Docker Compose

### Швидкий запуск

#### 1. Віртуальне середовище

```bash
cd clinic-demo
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. Заповнення змінних середовища

Скопіюйте приклад:

```bash
cp .env.example .env
```

#### 3. Запуск API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API доступне на:
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

#### 4. Запуск через Docker

```bash
docker compose up --build
```

### Seed-дані

Seed-скрипт створює базу даних і наповнює її синтетичними даними.

```bash
python seed.py
```

### Тестові облікові записи

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

### Тести

```bash
pytest -q
```

Це вимагає, щоб тестовий набір використовував SQLite test DB і перевіряв основні сценарії API.

### Структура проєкту

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

### Примітки

- У репозиторії немає реальних секретів або API-ключів.
- Усі чутливі значення повинні передаватися через `.env` або змінні середовища.
- ШІ-асистент використовує модуль `mock_llm.py` без змін.
