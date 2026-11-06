import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dyumnanegi@localhost:5432/resume_analyzer"
)

# JWT Authentication
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "resume-analyzer-secure-jwt-secret-key-change-in-prod-2026")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# Cookie Settings
COOKIE_NAME = "access_token"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "False").lower() in ("true", "1", "t")
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")

# File Storage Configuration
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", str(BASE_DIR / "storage" / "resumes")))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", str(BASE_DIR / "storage" / "reports")))
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))  # 10 MB limit

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# CORS Origins
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

