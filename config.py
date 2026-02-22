import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    # IMPORTANT: later, put this in an environment variable
    SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_to_a_strong_secret")

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + str(BASE_DIR / "database" / "english_coach.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Where you'll store uploads later (PDFs, videos, etc.)
    UPLOAD_FOLDER = str(BASE_DIR / "static" / "uploads")

    # New: Allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {'pdf', 'mp4', 'mov', 'avi', 'webm'} # Add common video formats
