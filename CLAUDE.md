# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
pip install -r requirements.txt
python3 app.py
```

Runs on http://localhost:5000 with debug mode. No test suite exists yet.

## Architecture

Flask app serving a JSON API + a single HTML page with vanilla JS. SQLite database (`mood_tracker.db`) is auto-created on startup via `init_db()`.

**Data flow for mood entries:** Frontend → `routes/entries.py` → `services/sentiment.py` (TextBlob analysis) → `models/database.py` → SQLite. Sentiment is computed on every create/update, never stored independently.

**Key layers:**
- `models/database.py` — All SQL queries as plain functions (no ORM). Each function opens/closes its own connection. Manages both CRUD and analytics queries.
- `services/sentiment.py` — Single function wrapping TextBlob. Returns `(polarity_float, label_string)`. Thresholds: < -0.1 = Negative, > 0.1 = Positive, else Neutral.
- `routes/entries.py` — CRUD blueprint at `/api/entries`. Enforces one entry per calendar day (409 on duplicate).
- `routes/analytics.py` — Read-only blueprint at `/api/analytics/*`. Includes word frequency counting with a hardcoded stop-word set.

**Frontend** (`static/js/`): Three JS files map to three nav sections — `app.js` (Log view + entry CRUD), `charts.js` (Chart.js trend chart), `heatmap.js` (calendar rendering). All state is in module-level variables; no framework.

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/entries` | Create entry (`{mood, note, date}`) |
| GET | `/api/entries` | List entries (`start_date`, `end_date`, `limit`, `offset`) |
| GET/PUT/DELETE | `/api/entries/<id>` | Single entry operations |
| GET | `/api/analytics/trends` | Chart data (`days=7|30|90|all`) |
| GET | `/api/analytics/heatmap` | Monthly mood map (`year`, `month`) |
| GET | `/api/analytics/wordcloud` | Word frequencies (`start_date`, `end_date`) |
| GET | `/api/analytics/summary` | Last-7-days summary stats |

## Database

Single-user mode by default (`user_id` is NULL). Auth support (`users` table, `AUTH_ENABLED` env var) is schema-ready but route logic is stubbed in `routes/auth.py`. All database functions accept an optional `user_id` parameter for future multi-user support.

## Configuration

All config is in `config.py` via environment variables: `SECRET_KEY`, `DATABASE_PATH`, `AUTH_ENABLED`.
