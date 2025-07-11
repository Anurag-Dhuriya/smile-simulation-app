from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Landmark(Base):
    __tablename__ = 'landmarks'
    id = Column(Integer, primary_key=True)
    face_id = Column(String)
    x = Column(Float)
    y = Column(Float)

engine = create_engine('sqlite:///landmarks.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
