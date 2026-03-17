# Product Requirements Document: Mood Tracker with Sentiment Analysis

**Version:** 1.0  
**Date:** March 17, 2026  
**Author:** Product Team  
**Status:** Draft

---

## 1. Overview

The Mood Tracker with Sentiment Analysis is a web application that enables users to log their daily mood using a simple rating scale and a short text note. The system automatically analyzes each text entry using natural language processing (NLP) to determine its emotional sentiment, then visualizes mood trends over time through interactive graphs and a calendar heatmap.

The project is scoped as a solo developer effort suitable for a beginner-to-intermediate Python developer. It uses a lightweight tech stack — Python backend, SQLite database, and vanilla HTML/CSS/JavaScript frontend — to keep deployment and maintenance simple.

---

## 2. Goals and Objectives

**Primary Goal:** Give users a simple, private tool to track their emotional well-being daily and surface patterns they might not notice on their own.

**Objectives:**

- Let users log a mood entry in under 30 seconds (low friction).
- Automatically extract sentiment from free-text notes so users get an objective second data point alongside their self-reported rating.
- Visualize mood data across days, weeks, and months so users can identify recurring patterns, triggers, or improvement trends.
- Keep the tech stack simple enough that a single developer can build, deploy, and maintain the application.

**Non-Goals (Out of Scope for v1):**

- Social features (sharing moods, community feeds).
- Therapist or clinician dashboards.
- Mobile-native applications (responsive web only).
- Real-time notifications or push alerts.

---

## 3. User Personas

### Persona 1: Maya — The Self-Improvement Journaler

- **Age:** 26
- **Tech Comfort:** Intermediate (uses apps daily, no coding background)
- **Motivation:** Maya journals sporadically and wants a structured way to track her mood without committing to long-form writing. She values quick entry and visual feedback.
- **Pain Points:** Forgets to journal, doesn't notice patterns without data, finds most mood apps too complex or gamified.
- **Key Need:** A fast daily entry flow and clear trend visualizations.

### Persona 2: Ravi — The Data-Curious Student

- **Age:** 21
- **Tech Comfort:** High (CS student, comfortable with technical tools)
- **Motivation:** Ravi wants to understand the relationship between his written reflections and his actual mood. He's curious whether sentiment analysis can reveal blind spots in his self-assessment.
- **Pain Points:** Existing apps either lack data export or don't provide analytical features.
- **Key Need:** Sentiment analysis comparison, data visualizations, and eventually data export.

### Persona 3: Linda — The Wellness Beginner

- **Age:** 45
- **Tech Comfort:** Low-to-moderate (uses email and basic web apps)
- **Motivation:** Linda's therapist suggested she start tracking her mood. She needs something straightforward with no learning curve.
- **Pain Points:** Overwhelmed by feature-heavy apps, needs clear visual cues (colors, simple charts).
- **Key Need:** Minimal interface, calendar heatmap for at-a-glance understanding, no mandatory sign-up.

---

## 4. Features and Requirements

### 4.1 Core Features

#### F1: Daily Mood Logging

| Attribute | Detail |
|-----------|--------|
| **Description** | User selects a mood rating and writes a short text note. |
| **Mood Scale** | 1–5 integer scale: 1 = Very Bad, 2 = Bad, 3 = Neutral, 4 = Good, 5 = Very Good. |
| **Text Note** | Free-text field, 1–500 characters. Required but can be as short as one word. |
| **Timestamp** | Automatically recorded as the user's local date and time. |
| **Edit/Delete** | Users can edit or delete any past entry. |
| **Validation** | Mood rating is required. Text note is required. One entry per calendar day (editing replaces the existing entry for that day). |

#### F2: Sentiment Analysis of Text Entries

| Attribute | Detail |
|-----------|--------|
| **Description** | Each text note is analyzed for emotional sentiment automatically on submission. |
| **Library** | TextBlob (default) or VADER from NLTK. Both run locally with no external API calls. |
| **Output** | A polarity score from -1.0 (very negative) to +1.0 (very positive) stored alongside the entry. |
| **Display** | Sentiment is shown as a label (Negative / Neutral / Positive) and a numeric score next to each entry. |
| **Thresholds** | Negative: polarity < -0.1, Neutral: -0.1 ≤ polarity ≤ 0.1, Positive: polarity > 0.1. |

#### F3: Mood Trend Visualization

| Attribute | Detail |
|-----------|--------|
| **Description** | Line chart showing mood rating and sentiment score over time. |
| **Library** | Chart.js (frontend) via CDN. |
| **X-Axis** | Date (day granularity). |
| **Y-Axis** | Dual axis — mood rating (1–5, left) and sentiment polarity (-1 to +1, right). |
| **Filters** | Time range selector: Last 7 days, Last 30 days, Last 90 days, All time. |
| **Interaction** | Hover tooltips showing exact values and the text note for that day. |

#### F4: Calendar Heatmap

| Attribute | Detail |
|-----------|--------|
| **Description** | A month-view calendar where each day is color-coded by mood rating. |
| **Color Scale** | Red (1) → Orange (2) → Yellow (3) → Light Green (4) → Green (5). Unlogged days are gray. |
| **Navigation** | Previous/Next month buttons. |
| **Interaction** | Clicking a day opens that day's entry for viewing or editing. |

### 4.2 Bonus Features

#### B1: Word Cloud from User Entries

| Attribute | Detail |
|-----------|--------|
| **Description** | Generates a word cloud from all text notes within a selected date range. |
| **Library** | A lightweight JavaScript word cloud library (e.g., wordcloud2.js) or server-side generation with Python's wordcloud library rendered as an image. |
| **Stop Words** | Common English stop words are filtered out. |
| **Refresh** | Regenerated on demand when the user selects a date range and clicks "Generate." |

#### B2: Weekly Summary Report

| Attribute | Detail |
|-----------|--------|
| **Description** | Auto-generated text summary of the past 7 days, including average mood, sentiment trend direction, most frequent words, and best/worst days. |
| **Trigger** | Available on-demand via a "View Weekly Summary" button. |
| **Content** | Average mood rating, average sentiment score, day with highest/lowest mood, dominant sentiment trend (improving, declining, stable), top 5 most-used words. |

#### B3: Simple User Authentication

| Attribute | Detail |
|-----------|--------|
| **Description** | Optional username/password authentication so multiple users can maintain separate logs on the same instance. |
| **Implementation** | Flask-Login or session-based auth. Passwords hashed with bcrypt. |
| **Scope** | Registration, login, logout. No email verification, no password reset in v1. |
| **Default** | If auth is disabled, the app runs in single-user mode with no login screen. |

---

## 5. User Stories

### Mood Logging

- **US-1:** As a user, I want to select a mood rating (1–5) and write a short note so that I can record how I feel today.
- **US-2:** As a user, I want to edit a past entry so that I can correct mistakes or add detail.
- **US-3:** As a user, I want to delete an entry so that I can remove something I logged by mistake.
- **US-4:** As a user, I want to see all my past entries in a scrollable list (newest first) so that I can review my history.

### Sentiment Analysis

- **US-5:** As a user, I want to see a sentiment label (Positive / Neutral / Negative) next to each entry so that I can compare my self-reported mood with the analyzed tone of my writing.
- **US-6:** As a user, I want to see the numeric sentiment score so that I can track subtle shifts in tone over time.

### Visualization

- **US-7:** As a user, I want to view a line chart of my mood ratings over the last 30 days so that I can see whether my mood is trending up or down.
- **US-8:** As a user, I want to overlay the sentiment score on the same chart so that I can compare my self-reported mood with the text analysis.
- **US-9:** As a user, I want to see a monthly calendar heatmap colored by mood so that I can get an at-a-glance picture of good and bad stretches.
- **US-10:** As a user, I want to click a day on the calendar to view or edit that day's entry.

### Bonus

- **US-11:** As a user, I want to generate a word cloud from my entries so that I can see which words and topics I write about most.
- **US-12:** As a user, I want to view an auto-generated weekly summary so that I can quickly understand my recent emotional trends without reviewing every entry.
- **US-13:** As a user, I want to create an account and log in so that my mood data is private to me on a shared instance.

---

## 6. Technical Architecture

### 6.1 High-Level Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Frontend** | HTML5, CSS3, vanilla JavaScript | Single-page feel with dynamic content loading via fetch API. |
| **Charting** | Chart.js (via CDN) | Used for line charts and potentially bar charts. |
| **Backend** | Python 3.12, Flask | Lightweight web framework. Serves both API endpoints and HTML templates. |
| **NLP** | TextBlob (or NLTK VADER) | Runs locally; no external API dependency. |
| **Database** | SQLite | File-based, zero-configuration. Stored as `mood_tracker.db` in the project root. |
| **Auth (optional)** | Flask-Login + bcrypt | Session-based authentication. |

### 6.2 Project Structure

```
mood-tracker/
├── app.py                  # Flask application entry point
├── config.py               # Configuration (DB path, secret key, auth toggle)
├── requirements.txt        # Python dependencies
├── mood_tracker.db         # SQLite database (auto-created)
├── models/
│   └── database.py         # Database initialization and query functions
├── services/
│   └── sentiment.py        # Sentiment analysis wrapper
├── routes/
│   ├── entries.py           # CRUD API for mood entries
│   ├── analytics.py         # Trend data, heatmap data, word cloud, summary
│   └── auth.py              # Login/register/logout (optional)
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js           # Main application logic
│       ├── charts.js         # Chart.js initialization and updates
│       └── heatmap.js        # Calendar heatmap rendering
└── templates/
    └── index.html           # Main (and only) HTML page
```

### 6.3 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/entries` | Create a new mood entry. Body: `{ mood: int, note: string }`. Returns the created entry with sentiment score. |
| `GET` | `/api/entries` | List entries. Query params: `start_date`, `end_date`, `limit`, `offset`. |
| `GET` | `/api/entries/<id>` | Get a single entry by ID. |
| `PUT` | `/api/entries/<id>` | Update an existing entry. Body: `{ mood: int, note: string }`. Re-runs sentiment analysis. |
| `DELETE` | `/api/entries/<id>` | Delete an entry. |
| `GET` | `/api/analytics/trends` | Returns mood + sentiment arrays for charting. Query params: `days` (7, 30, 90, all). |
| `GET` | `/api/analytics/heatmap` | Returns `{ date: mood_rating }` for a given month. Query params: `year`, `month`. |
| `GET` | `/api/analytics/wordcloud` | Returns word frequency data. Query params: `start_date`, `end_date`. |
| `GET` | `/api/analytics/summary` | Returns the weekly summary object (averages, best/worst day, top words, trend direction). |
| `POST` | `/api/auth/register` | Register a new user (optional). |
| `POST` | `/api/auth/login` | Log in (optional). |
| `POST` | `/api/auth/logout` | Log out (optional). |

---

## 7. Data Model

### 7.1 entries

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique entry identifier. |
| `user_id` | INTEGER | FOREIGN KEY → users.id, nullable | Owner (null in single-user mode). |
| `mood_rating` | INTEGER | NOT NULL, CHECK (1–5) | Self-reported mood on 1–5 scale. |
| `note` | TEXT | NOT NULL, max 500 chars | Free-text reflection. |
| `sentiment_score` | REAL | NOT NULL | Polarity from -1.0 to +1.0. |
| `sentiment_label` | TEXT | NOT NULL | "Negative", "Neutral", or "Positive". |
| `entry_date` | DATE | NOT NULL, UNIQUE per user | Calendar date of the entry. |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation timestamp. |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp. |

### 7.2 users (optional, only when auth is enabled)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user identifier. |
| `username` | TEXT | NOT NULL, UNIQUE | Login username. |
| `password_hash` | TEXT | NOT NULL | bcrypt-hashed password. |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp. |

### 7.3 Indexes

- `idx_entries_user_date` on `(user_id, entry_date)` — fast lookups for calendar heatmap and duplicate prevention.
- `idx_entries_entry_date` on `(entry_date)` — fast range queries for trend charts.

---

## 8. UI/UX Considerations

### 8.1 Layout

The application uses a single-page layout with three main sections accessible via a top navigation bar:

- **Log** (default view): Mood entry form at the top, recent entries list below.
- **Trends**: Line chart with time-range selector.
- **Calendar**: Monthly heatmap with navigation arrows.

Bonus views (Word Cloud, Weekly Summary) are accessible from a secondary menu or as expandable panels within the Trends section.

### 8.2 Design Principles

- **Speed over polish:** The entry form should be the first thing users see. Mood buttons should be large, tappable, and visually distinct (color-coded to match the heatmap scale).
- **Responsive:** The layout should work on screens from 360px (mobile) to 1440px (desktop). Use CSS Grid or Flexbox — no CSS framework required.
- **Color accessibility:** Heatmap colors should pass WCAG AA contrast against white text. Provide a tooltip with the numeric mood value as a fallback for color-blind users.
- **Immediate feedback:** After submitting an entry, the sentiment label and score appear instantly on the page without a full reload. Use fetch + DOM manipulation.
- **Empty states:** When no data exists, charts and calendars display a friendly message ("No entries yet — log your first mood above!") rather than a blank area or error.

### 8.3 Mood Input Design

The mood selector should use five large buttons arranged horizontally, each showing the numeric value and a simple emoji or text label:

| Button | Label | Color |
|--------|-------|-------|
| 1 | Very Bad | #E74C3C (red) |
| 2 | Bad | #E67E22 (orange) |
| 3 | Neutral | #F1C40F (yellow) |
| 4 | Good | #2ECC71 (light green) |
| 5 | Very Good | #27AE60 (green) |

---

## 9. Success Metrics

These metrics help determine whether the application is meeting its goals. For a solo/student project, tracking can be as simple as SQLite queries or log analysis.

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Daily Active Entries** | At least 1 entry per active user per day | Count of entries per user per day. |
| **Entry Completion Rate** | >90% of started entries are submitted | Track form open events vs. successful POST calls (simple frontend counter). |
| **Average Entry Time** | Under 30 seconds from page load to submission | Timestamp difference between page load and form submit (logged in JS). |
| **Return Rate** | User logs entries on 5+ of 7 days in a week | Weekly query: count distinct entry_dates per user. |
| **Sentiment vs. Mood Correlation** | Positive correlation (r > 0.3) between mood_rating and sentiment_score over 30+ entries | Pearson correlation computed in the weekly summary. |
| **Feature Engagement** | Trends page viewed at least once per week by active users | Simple page-view counter per section. |

---

## 10. Future Enhancements

The following features are explicitly out of scope for v1 but represent natural next steps:

- **Data Export:** Allow users to download their entries as CSV or JSON for use in external tools (spreadsheets, Jupyter notebooks).
- **Tagging System:** Let users add custom tags (e.g., "work", "health", "relationship") to entries and filter visualizations by tag.
- **Mood Reminders:** Optional daily notification (email or browser push) reminding the user to log their mood at a preferred time.
- **Multi-Language Sentiment:** Support sentiment analysis in languages beyond English using multilingual NLP models.
- **Advanced Analytics:** Rolling averages, day-of-week patterns ("Mondays are consistently low"), and correlation with external data (weather API, sleep tracker import).
- **Progressive Web App (PWA):** Add a manifest and service worker so users can install the app on mobile home screens and use it offline with sync-on-reconnect.
- **Therapist Sharing:** Generate a read-only shareable link to a date range of entries that a user can send to a therapist or counselor.
- **Dark Mode:** A toggle for dark/light theme with mood colors adjusted for both palettes.

---

*End of Document*