# Microservices: DRF + FastAPI

Two services that talk to each other over REST (synchronous communication), run together with Docker Compose.

| Service | Framework | Port | Owns |
|---|---|---|---|
| `drf` | Django REST Framework | 8000 | Students |
| `fastapi` | FastAPI | 8001 | Employees, mentors |
| `db` | PostgreSQL 17 | 5433 (on your PC) | Databases `drf` and `fastapi_db` |

DRF calls FastAPI (for example, `POST /assign_mentor/<id>/` asks FastAPI's `/mentor/<id>`).

## Run it

1. Install Docker Desktop and start it.
2. Copy `.env.example` to `.env` and set your own values.
3. From this folder:

```
docker compose up --build
```

- DRF: http://127.0.0.1:8000
- FastAPI docs: http://127.0.0.1:8001/docs

Stop with `Ctrl+C`, or `docker compose down`.

## Useful commands

| Command | What it does |
|---|---|
| `docker compose up --build` | Build images and start everything (use after changing requirements.txt) |
| `docker compose up -d` | Start in the background |
| `docker compose logs -f drf` | Follow one service's logs |
| `docker compose ps` | See what's running |
| `docker compose restart fastapi` | Restart one service |
| `docker compose exec drf python manage.py makemigrations` | Run a Django command inside the container |
| `docker compose exec drf python manage.py createsuperuser` | Create a Django admin user |
| `docker compose down` | Stop and remove containers (data is kept) |
| `docker compose down -v` | Stop and delete the database data too |
