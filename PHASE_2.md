# reviewagentai — Phase 2: Backend/API Foundation

## Goal
Build a small, testable FastAPI backend on top of the Phase 1 database.

## Endpoints
- GET /
- GET /api/v1/health
- GET /api/v1/businesses/{slug}

Example:
GET /api/v1/businesses/abc-restaurant

## Run
```bash
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Swagger:
http://127.0.0.1:8000/docs

Health:
http://127.0.0.1:8000/api/v1/health

Business:
http://127.0.0.1:8000/api/v1/businesses/abc-restaurant

Tests:
```bash
pytest -q
```

## Architecture
HTTP Request
 -> FastAPI Router
 -> Pydantic Schema
 -> Service
 -> SQLAlchemy ORM
 -> SQLite
