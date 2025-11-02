from app.database import engine
from sqlalchemy import text

# Check if tables exist
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
except Exception as e:
    print(f"Error: {e}")