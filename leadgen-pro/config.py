import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-this-local-development-key")
    GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY", "")
    DATABASE_PATH = BASE_DIR / "database" / "leads.db"
    JSON_SORT_KEYS = False
