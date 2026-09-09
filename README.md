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

## AI vs database fallback review comments

Each business has a Boolean database column named `PreferAIComments` (exposed by the API as `prefer_ai_comments`). It controls the positive-review generation strategy:

- `true`: call Groq first. If Groq succeeds, the response has `generation_source: "groq"`.
- `false`: do not call Groq; use the business's database fallback comments and return `generation_source: "fallback"`.
- If `PreferAIComments=true` but Groq fails for any reason (API key, quota, network, model error, invalid response, etc.), the backend automatically uses the database fallback comments and still returns a successful response with `generation_source: "fallback"`.

Fallback comments are stored in the `fallback_review_comments` table. The table supports business-specific comments, 4/5-star variants, display order, and enabled/disabled status. The fallback comments are therefore configurable database data rather than hard-coded response strings.

The positive-review response now includes:

```json
{
  "session_id": "...",
  "business_id": "1",
  "rating": 5,
  "generation_source": "groq",
  "reviews": []
}
```

When AI is unavailable:

```json
{
  "session_id": "...",
  "business_id": "1",
  "rating": 5,
  "generation_source": "fallback",
  "reviews": []
}
```

The fallback templates can contain `{customer_input}`. At runtime that placeholder is replaced with the customer's own comments, without asking AI to generate the fallback text.

### Database reset after this schema change

Because this development project intentionally does not use Alembic, recreate the SQLite database after applying this change:

```powershell
# Stop the API first with CTRL+C
Remove-Item .\reviewagentai.db -ErrorAction SilentlyContinue
uvicorn backend.app.main:app --reload
```

Startup will recreate the `PreferAIComments` column and `fallback_review_comments` table and seed the demo fallback comments.

### Verification

Run:

```powershell
pytest -q
```

Then test:

```text
POST /api/v1/reviews/session
POST /api/v1/reviews/session/{session_id}/rating
POST /api/v1/reviews/session/{session_id}/positive-reviews
```

For `reviewagentai`, `prefer_ai_comments=true`, so a successful Groq request should return `generation_source="groq"`. To test the fallback path, temporarily set the business's `PreferAIComments` value to false or simulate a Groq failure; the frontend must still receive three review comments with `generation_source="fallback"`.
