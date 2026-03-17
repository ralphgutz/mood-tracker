# Mood Tracker with Sentiment Analysis

A web app for tracking daily mood with automatic sentiment analysis of text notes, trend visualizations, and Spotify music recommendations based on how you feel.

## Features

- **Mood Logging** — Rate your mood 1-5 and write a short note. One entry per day, editable anytime.
- **Sentiment Analysis** — Each note is analyzed with TextBlob to produce a polarity score (-1.0 to +1.0) and a label (Negative / Neutral / Positive).
- **Trend Chart** — Dual-axis line chart (Chart.js) showing mood rating and sentiment score over 7, 30, 90 days, or all time. Hover for note previews.
- **Calendar Heatmap** — Month view color-coded by mood. Click any day to view or edit that entry.
- **Music Recommendations** — After logging a mood, get Spotify track suggestions matched to how you're feeling, with embedded players.
- **Word Cloud** — Visualize your most-used words over a date range.
- **Weekly Summary** — Average mood, sentiment trend, best/worst days, and top words from the last 7 days.

## Tech Stack

- **Backend:** Python 3 / Flask
- **Database:** SQLite (auto-created, zero config)
- **NLP:** TextBlob (runs locally, no external API)
- **Music:** Spotify Web API (Client Credentials Flow)
- **Frontend:** Vanilla HTML/CSS/JS + Chart.js via CDN
- **Deployment:** Vercel-ready

## Getting Started

### Prerequisites

- Python 3.10+

### Install and Run

```bash
pip install -r requirements.txt
cp .env.example .env   # then add your Spotify credentials
python3 app.py
```

Open http://localhost:5000

### Spotify Setup (optional)

Music recommendations require a Spotify developer app:

1. Go to https://developer.spotify.com/dashboard
2. Create an app and copy the Client ID and Client Secret
3. Add them to your `.env` file:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   ```

The app works fully without Spotify — the music card simply won't appear.

## Deploying to Vercel

The repo includes a `vercel.json` ready for deployment. Add your environment variables (`SECRET_KEY`, `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`) in the Vercel dashboard under Settings > Environment Variables.

> **Note:** SQLite on Vercel is ephemeral — data resets on cold starts. For persistent data, swap to an external database.

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/entries` | Create entry (`{mood, note, date}`) |
| `GET` | `/api/entries` | List entries (supports `start_date`, `end_date`, `limit`, `offset`) |
| `GET` | `/api/entries/<id>` | Get single entry |
| `PUT` | `/api/entries/<id>` | Update entry (`{mood, note}`) |
| `DELETE` | `/api/entries/<id>` | Delete entry |
| `GET` | `/api/analytics/trends` | Trend data (`days=7\|30\|90\|all`) |
| `GET` | `/api/analytics/heatmap` | Monthly heatmap (`year`, `month`) |
| `GET` | `/api/analytics/wordcloud` | Word frequencies (`start_date`, `end_date`) |
| `GET` | `/api/analytics/summary` | Weekly summary stats |
| `GET` | `/api/music` | Spotify recommendations (`mood=1-5`) |

## License

MIT
