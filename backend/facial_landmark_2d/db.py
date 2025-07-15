# db.py

from sqlalchemy import create_engine, Column, Integer, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .config import DATABASE_URL

Base = declarative_base()

class Landmark(Base):
    __tablename__ = 'landmarks'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    coordinates = Column(JSON)

# Database setup
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def create_tables():
    Base.metadata.create_all(engine)
