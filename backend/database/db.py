# backend/database/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database
DATABASE_URL = "sqlite:///backend/database/snapshots.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(bind=engine)

# Create a Session instance
session = SessionLocal()

# Base class for models
Base = declarative_base()
