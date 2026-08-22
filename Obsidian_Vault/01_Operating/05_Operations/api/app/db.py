import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../data/torus_local.db")

# Ensure SQLite absolute path resolves relative to this file
if DATABASE_URL.startswith("sqlite:///"):
    rel_path = DATABASE_URL.replace("sqlite:///", "")
    if not os.path.isabs(rel_path):
        base_dir = Path(__file__).resolve().parent.parent
        abs_path = base_dir / rel_path
        abs_path = abs_path.resolve()
        DATABASE_URL = f"sqlite:///{abs_path}"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
