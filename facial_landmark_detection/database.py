from sqlalchemy import create_engine, Column, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()
DATABASE_URL = "sqlite:///landmarks.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class Landmark(Base):
    __tablename__ = 'landmarks'
    id = Column(String, primary_key=True)
    face_id = Column(String)
    x = Column(Float)
    y = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
