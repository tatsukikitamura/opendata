"""
Centralized configuration management.

This module consolidates all environment variables and settings
to avoid scattered load_dotenv() calls across the codebase.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file once from project root
_BASE_DIR = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _BASE_DIR.parent
load_dotenv(_PROJECT_ROOT / ".env")


# ==============================================================================
# Database Configuration
# ==============================================================================
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please set it in .env file (e.g., postgresql://user:pass@host:port/dbname)"
    )


# ==============================================================================
# API Keys
# ==============================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ODPT_ACCESS_TOKEN = os.getenv("ODPT_ACCESS_TOKEN", "")


# ==============================================================================
# External API URLs
# ==============================================================================
ODPT_BASE_URL = "https://api-challenge.odpt.org/api/v4"
GTFS_RT_URL = "https://api-challenge.odpt.org/api/v4/gtfs/realtime/jreast_odpt_train_trip_update"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


# ==============================================================================
# CORS Configuration
# ==============================================================================
def get_allowed_origins() -> list[str]:
    """Get CORS allowed origins from environment or default to all."""
    allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
    if allowed_origins_env:
        return [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
    return ["*"]


# ==============================================================================
# Application Settings
# ==============================================================================
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
