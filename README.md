# reviewagentai — Phase 1: Database Foundation

This phase establishes the database layer for the reviewagentai MVP.

Included:
- SQLite database
- SQLAlchemy ORM
- Six initial tables
- Automatic creation of missing tables
- Idempotent demo seed data
- Alembic migration foundation
- Basic database tests

Run:
```bash
pip install -r requirements.txt
python -m backend.app.db.init_db
pytest -q
```

Default database: `./reviewagentai.db`

The MVP bootstrap uses SQLAlchemy `Base.metadata.create_all()` so missing tables
are created automatically. Alembic is included for controlled future schema changes.
