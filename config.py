import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
DATABASE_PATH = os.path.join(BASE_DIR, "mood_tracker.db")
AUTH_ENABLED = os.environ.get("AUTH_ENABLED", "false").lower() == "true"
