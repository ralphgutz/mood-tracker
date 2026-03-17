import sqlite3
from datetime import datetime, date

import config


def get_db():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    if not config.IS_VERCEL:
        conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mood_rating INTEGER NOT NULL CHECK (mood_rating BETWEEN 1 AND 5),
            note TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            sentiment_label TEXT NOT NULL,
            entry_date DATE NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_entries_user_date ON entries(user_id, entry_date);
        CREATE INDEX IF NOT EXISTS idx_entries_entry_date ON entries(entry_date);
    """)
    conn.close()


def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


# --- Entry CRUD ---

def create_entry(mood_rating, note, sentiment_score, sentiment_label, entry_date, user_id=None):
    conn = get_db()
    try:
        cursor = conn.execute(
            """INSERT INTO entries (user_id, mood_rating, note, sentiment_score, sentiment_label, entry_date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, mood_rating, note, sentiment_score, sentiment_label, entry_date),
        )
        conn.commit()
        entry = conn.execute("SELECT * FROM entries WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return row_to_dict(entry)
    finally:
        conn.close()


def get_entry(entry_id, user_id=None):
    conn = get_db()
    try:
        if user_id is not None:
            row = conn.execute("SELECT * FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id)).fetchone()
        else:
            row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def get_entry_by_date(entry_date, user_id=None):
    conn = get_db()
    try:
        if user_id is not None:
            row = conn.execute(
                "SELECT * FROM entries WHERE entry_date = ? AND user_id = ?", (entry_date, user_id)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM entries WHERE entry_date = ? AND user_id IS NULL", (entry_date,)
            ).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def list_entries(start_date=None, end_date=None, limit=50, offset=0, user_id=None):
    conn = get_db()
    try:
        query = "SELECT * FROM entries WHERE 1=1"
        params = []

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)
        else:
            query += " AND user_id IS NULL"

        if start_date:
            query += " AND entry_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND entry_date <= ?"
            params.append(end_date)

        query += " ORDER BY entry_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()


def update_entry(entry_id, mood_rating, note, sentiment_score, sentiment_label, user_id=None):
    conn = get_db()
    try:
        now = datetime.utcnow().isoformat()
        if user_id is not None:
            conn.execute(
                """UPDATE entries SET mood_rating=?, note=?, sentiment_score=?, sentiment_label=?, updated_at=?
                   WHERE id=? AND user_id=?""",
                (mood_rating, note, sentiment_score, sentiment_label, now, entry_id, user_id),
            )
        else:
            conn.execute(
                """UPDATE entries SET mood_rating=?, note=?, sentiment_score=?, sentiment_label=?, updated_at=?
                   WHERE id=?""",
                (mood_rating, note, sentiment_score, sentiment_label, now, entry_id),
            )
        conn.commit()
        return get_entry(entry_id, user_id)
    finally:
        conn.close()


def delete_entry(entry_id, user_id=None):
    conn = get_db()
    try:
        if user_id is not None:
            conn.execute("DELETE FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id))
        else:
            conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()
    finally:
        conn.close()


# --- Analytics ---

def get_trend_data(days=None, user_id=None):
    conn = get_db()
    try:
        query = "SELECT entry_date, mood_rating, sentiment_score, note FROM entries WHERE 1=1"
        params = []

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)
        else:
            query += " AND user_id IS NULL"

        if days:
            query += " AND entry_date >= date('now', ?)"
            params.append(f"-{days} days")

        query += " ORDER BY entry_date ASC"
        rows = conn.execute(query, params).fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_heatmap_data(year, month, user_id=None):
    conn = get_db()
    try:
        start = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end = f"{year + 1:04d}-01-01"
        else:
            end = f"{year:04d}-{month + 1:02d}-01"

        query = "SELECT entry_date, mood_rating FROM entries WHERE entry_date >= ? AND entry_date < ?"
        params = [start, end]

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)
        else:
            query += " AND user_id IS NULL"

        rows = conn.execute(query, params).fetchall()
        return {r["entry_date"]: r["mood_rating"] for r in rows}
    finally:
        conn.close()


def get_wordcloud_data(start_date=None, end_date=None, user_id=None):
    conn = get_db()
    try:
        query = "SELECT note FROM entries WHERE 1=1"
        params = []

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)
        else:
            query += " AND user_id IS NULL"

        if start_date:
            query += " AND entry_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND entry_date <= ?"
            params.append(end_date)

        rows = conn.execute(query, params).fetchall()
        return [r["note"] for r in rows]
    finally:
        conn.close()


def get_summary_data(user_id=None):
    """Get the last 7 days of entries for the weekly summary."""
    conn = get_db()
    try:
        query = """SELECT entry_date, mood_rating, sentiment_score, note
                   FROM entries WHERE entry_date >= date('now', '-7 days')"""
        params = []

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)
        else:
            query += " AND user_id IS NULL"

        query += " ORDER BY entry_date ASC"
        rows = conn.execute(query, params).fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()
