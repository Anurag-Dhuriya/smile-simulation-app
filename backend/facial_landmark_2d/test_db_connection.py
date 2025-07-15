# test_db_connection.py

from sqlalchemy import create_engine, text
from .config import DATABASE_URL  # Make sure this points to your config

def test_connection():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful:", result.scalar())
    except Exception as e:
        print("❌ Database connection failed:")
        print(e)

if __name__ == "__main__":
    test_connection()
