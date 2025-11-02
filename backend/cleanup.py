from app.database import SessionLocal
from app.models.user import User

# Delete test users
db = SessionLocal()
users = db.query(User).filter(User.email.like('test%@example.com')).all()
for user in users:
    print(f"Deleting user: {user.email}")
    db.delete(user)

db.commit()
db.close()
print("Test users cleaned up")