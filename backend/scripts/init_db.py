from dotenv import load_dotenv
import os
from pathlib import Path
from sqlalchemy import create_engine
import sys

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Load .env
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from db.database import Base, engine
from db import models

def init_db():
    print(f"Connecting to {engine.url}...")
    try:
        # Warning: This deletes all data!
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    init_db()
