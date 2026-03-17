# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
pip install -r requirements.txt
python3 app.py
```

Runs on http://localhost:5000 with debug mode. No test suite exists yet. Environment variables are loaded from `.env` via python-dotenv (see `.env.example`).

## Architecture

Flask app serving a JSON API + a single HTML page with vanilla JS. SQLite database (`mood_tracker.db`) is auto-created on startup via `init_db()`.

**Data flow for mood entries:** Frontend → `routes/entries.py` → `services/sentiment.py` (TextBlob analysis) → `models/database.py` → SQLite. Sentiment is computed on every create/update, never stored independently.

**Key layers:**
- `models/database.py` — All SQL queries as plain functions (no ORM). Each function opens/closes its own connection. Manages both CRUD and analytics queries.
- `services/sentiment.py` — Single function wrapping TextBlob. Returns `(polarity_float, label_string)`. Thresholds: < -0.1 = Negative, > 0.1 = Positive, else Neutral.
- `services/spotify.py` — Spotify Web API integration using stdlib `urllib` (no external HTTP library). Uses Client Credentials Flow with in-memory token caching. Maps mood ratings 1-5 to search queries.
- `routes/entries.py` — CRUD blueprint at `/api/entries`. Enforces one entry per calendar day (409 on duplicate).
- `routes/analytics.py` — Read-only blueprint at `/api/analytics/*`. Includes word frequency counting with a hardcoded stop-word set.
- `routes/music.py` — Music recommendation blueprint at `/api/music`. Returns 503 if Spotify credentials are missing.

**Frontend** (`static/js/`): Three JS files map to three nav sections — `app.js` (Log view + entry CRUD + music recommendations), `charts.js` (Chart.js trend chart), `heatmap.js` (calendar rendering). All state is in module-level variables; no framework. Music recommendations are fetched automatically after submitting a mood entry.

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/entries` | Create entry (`{mood, note, date}`) |
| GET | `/api/entries` | List entries (`start_date`, `end_date`, `limit`, `offset`) |
| GET/PUT/DELETE | `/api/entries/<id>` | Single entry operations |
| GET | `/api/analytics/trends` | Chart data (`days=7\|30\|90\|all`) |
| GET | `/api/analytics/heatmap` | Monthly mood map (`year`, `month`) |
| GET | `/api/analytics/wordcloud` | Word frequencies (`start_date`, `end_date`) |
| GET | `/api/analytics/summary` | Last-7-days summary stats |
| GET | `/api/music` | Spotify track recommendations (`mood=1-5`) |

## Database

Single-user mode by default (`user_id` is NULL). Auth support (`users` table, `AUTH_ENABLED` env var) is schema-ready but route logic is stubbed in `routes/auth.py`. All database functions accept an optional `user_id` parameter for future multi-user support.

## Configuration

All config is in `config.py` via environment variables (loaded from `.env` by python-dotenv):
- `SECRET_KEY` — Flask secret key
- `AUTH_ENABLED` — Enable multi-user auth (default: false)
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` — Required for music recommendations; get from https://developer.spotify.com/dashboard

## Deployment

Configured for Vercel via `vercel.json`. Key adaptations:
- `config.IS_VERCEL` detects the Vercel environment automatically
- SQLite writes to `/tmp` on Vercel (read-only filesystem elsewhere)
- WAL journal mode is disabled on Vercel
- Static files are served via `@vercel/static` build
- SQLite data is ephemeral on Vercel (resets on cold start)
