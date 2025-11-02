from app.database import Base, engine
from app.models import User, Mentor, Session, Message, Payment, Review, Progress

# Create all tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully")
except Exception as e:
    print(f"❌ Error creating tables: {e}")