# reviewagentai

ReviewAgentAI is a review-gating and customer-feedback platform for business-specific NFC/QR entry points.

## Current implementation

- SQLite + SQLAlchemy database foundation
- Business and social-link management
- Review session creation
- 1–5 star rating flow
- 1–3 star private feedback flow
- Groq-powered positive review suggestions with safe fallback text
- Google review selection/handoff
- Social-link click tracking
- Review/customer journey event tracking
- NFC/QR customer access validation and session creation
- Automatic database table creation with `Base.metadata.create_all()`
- **Alembic is not used**

## Customer access flow

A business-specific NFC/QR entry point uses the business slug:

```text
POST /api/v1/access/{business_slug}
```

Request:

```json
{
  "source": "nfc"
}
```

Supported `source` values:

- `nfc`
- `qr`
- `direct`

The endpoint:

1. Validates that the business exists.
2. Validates that the business is active.
3. Creates a new review session.
4. Records a `LANDING_PAGE_VIEW` event in the existing `review_events` table.
5. Stores the access channel and `session_id` in event metadata.
6. Returns the session information required by the customer review flow.

Example:

```text
POST /api/v1/access/reviewagentai
```

```json
{
  "source": "qr"
}
```

The endpoint does **not** submit a Google review automatically. Google review submission remains a manual customer action.

## Run locally

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run tests:

```powershell
pytest -q
```

Run the API:

```powershell
uvicorn backend.app.main:app --reload
```

Default API documentation:

```text
http://127.0.0.1:8000/docs
```

## Demo seed and SQLite reset

The demo seed is idempotent. On application startup it keeps the canonical five demo social links for `reviewagentai` and `abc-restaurant`, repairs their URL/order/enabled values, and removes obsolete or duplicate demo social-link records.

During development, if an older database contains stale test data, stop the API and delete the SQLite database file configured by `DATABASE_URL` (normally `reviewagentai.db`). Restarting the API recreates the tables and seeds clean demo data automatically.

No Alembic migration workflow is required for this development setup.
