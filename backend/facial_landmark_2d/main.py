# main.py

from .db import create_tables
from .facial_detection import detect_and_store

if __name__ == "__main__":
    create_tables()
    detect_and_store()
