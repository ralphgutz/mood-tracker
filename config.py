import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_VERCEL = os.environ.get("VERCEL", "") == "1"

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
AUTH_ENABLED = os.environ.get("AUTH_ENABLED", "false").lower() == "true"

# Vercel's filesystem is read-only except /tmp
if IS_VERCEL:
    DATABASE_PATH = "/tmp/mood_tracker.db"
else:
    DATABASE_PATH = os.path.join(BASE_DIR, "mood_tracker.db")
