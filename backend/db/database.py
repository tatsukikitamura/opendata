from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

from dotenv import load_dotenv
from pathlib import Path

# Build path relative to this file's location to ensure consistency
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = Path(BASE_DIR).parent.parent

# Load .env explicitly to ensure DATABASE_URL is available
load_dotenv(PROJECT_ROOT / ".env")

# Priority: Environment Variable > Local SQLite
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    # The DB is located in the backend root (one level up from db package)
    DB_PATH = os.path.join(BASE_DIR, "..", "data.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
