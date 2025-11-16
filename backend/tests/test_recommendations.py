from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.review import Review
from app.models.user import User, UserRole


def seed_reviews(db: Session):
    # create sample users and capture IDs
    users = []
    for i in range(1, 8):
        u = User(email=f"u{i}@ex.com", username=f"u{i}", hashed_password="x", full_name=f"User {i}")
        db.add(u)
        users.append(u)
    db.commit()
    for u in users:
        db.refresh(u)

    # course 101
    db.add_all([
        Review(user_id=users[0].id, course_id=101, rating=5),
        Review(user_id=users[1].id, course_id=101, rating=4),
    ])
    # course 102
    db.add_all([
        Review(user_id=users[2].id, course_id=102, rating=4),
        Review(user_id=users[3].id, course_id=102, rating=4),
    ])
    # course 103
    db.add_all([
        Review(user_id=users[4].id, course_id=103, rating=5),
        Review(user_id=users[5].id, course_id=103, rating=5),
    ])
    # course 104
    db.add(Review(user_id=users[6].id, course_id=104, rating=3))
    db.commit()


def test_similar_courses_excludes_current_and_sorted(client: TestClient, db_session: Session):
    seed_reviews(db_session)
    resp = client.get("/api/v1/courses/101/similar?limit=3")
    assert resp.status_code == 200
    data = resp.json()
    # expect 103 (avg 5), 102 (avg 4), 104 (avg 3)
    assert [item["course_id"] for item in data] == [103, 102, 104]
    assert data[0]["average_rating"] >= data[1]["average_rating"] >= data[2]["average_rating"]
    # current course not present
    assert 101 not in [item["course_id"] for item in data]
