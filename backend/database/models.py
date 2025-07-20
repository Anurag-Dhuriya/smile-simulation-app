# backend/database/models.py

from sqlalchemy import Column, Integer, String, DateTime
from backend.database.db import Base
import datetime

class Snapshot(Base):
    __tablename__ = 'snapshots'

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    landmark_csv = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
