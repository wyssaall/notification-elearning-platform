# Notification microservice

REST API (Django + Django REST Framework) that stores **per-user notifications** in **PostgreSQL** and can create notifications from **RabbitMQ** messages (e.g. when the Course Service publishes an enrollment event).

Colleagues only need: **Python 3**, **Docker** (for Postgres + RabbitMQ in dev), and this repo.

---

## What this service does

| Piece | Role |
|--------|------|
| **HTTP API** | CRUD-style access to notifications, scoped by `user_id` (no shared user DB — IDs come from other services). |
| **PostgreSQL** | Persists `Notification` rows. |
| **RabbitMQ + consumer** | Background worker reads JSON messages and inserts notifications (decoupled from the Course Service). |

---

## Repository layout

```
notif-micro/
├── README.md                      ← this file
├── .gitignore
└── notification_service/
    ├── manage.py
    ├── requirements.txt           # pip install -r requirements.txt
    ├── docker-compose.yml         # Postgres + RabbitMQ for local dev
    ├── notification_service/      # Django project (settings, urls)
    ├── notifications/             # App: models, API, RabbitMQ consumer
    └── examples/
        └── course_service_producer.py   # Demo publisher (stand-in for Course Service)
```

Do **not** commit `venv/` or `.env` — use `.gitignore`.

---

## Quick start (local)

**1. Start Postgres and RabbitMQ**

```bash
cd notification_service
docker compose up -d
```

Defaults match `settings.py`: Postgres `localhost:5432` (`notifications_db` / `postgres` / `yourpassword`), RabbitMQ `localhost:5672` (`guest` / `guest`). RabbitMQ management UI: http://localhost:15672

**2. Python environment**

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

**3. Database**

```bash
python manage.py migrate
```

**4. Run three processes** (three terminals, same `notification_service` folder)

| Terminal | Command |
|----------|---------|
| API | `python manage.py runserver` |
| Consumer | `python manage.py run_rabbitmq_consumer` |
| Test publish | `python examples/course_service_producer.py 42 "My course"` |

**5. Verify**

- Health: `GET http://127.0.0.1:8000/health/` → `{"status":"ok"}`
- List: `GET http://127.0.0.1:8000/api/v1/notifications/?user_id=42`

---

## HTTP API (v1)

Base URL: `/api/v1/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health/` | Liveness probe (`{"status":"ok"}`) |
| GET | `/api/v1/notifications/?user_id=<id>` | Paginated list for that user |
| POST | `/api/v1/notifications/` | Create (body: `user_id`, `title`, `message`) |
| PUT | `/api/v1/notifications/<pk>/mark-read/` | Body: `{"is_read": true}` |

`user_id` in the query is for **development**; in production an API gateway should pass a trusted user identity (e.g. JWT).

---

## RabbitMQ contract

- **Queue name** (default): `notifications.enrollment` — set `RABBITMQ_QUEUE` if you change it (producer and consumer must match).
- **Message body**: JSON UTF-8, for example:

```json
{
  "user_id": 42,
  "title": "Enrollment confirmed",
  "message": "You are now enrolled in \"Intro to Django\"."
}
```

The consumer runs as a **separate process** (`run_rabbitmq_consumer`), not inside the web request cycle.

---

## Environment variables (optional)

| Variable | Purpose | Default |
|----------|---------|---------|
| `SECRET_KEY` | Django secret | dev placeholder |
| `DEBUG` | Debug mode | `true` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | Database | see `settings.py` |
| `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD`, `RABBITMQ_QUEUE` | RabbitMQ | `localhost`, `5672`, `guest`, `guest`, `notifications.enrollment` |

---

## Design notes (for reports / slides)

- **Loose coupling**: `user_id` is stored as an integer, not a foreign key to another service’s database.
- **Versioned API**: `/api/v1/` allows future `/api/v2/` without breaking old clients.
- **Pagination**: DRF `PAGE_SIZE` limits list response size.
- **Indexes**: `(user_id, is_read)` supports “unread for user” queries efficiently.

---

## License / context

Student / internal project — adjust as needed for your institution.
