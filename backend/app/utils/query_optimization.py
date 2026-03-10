"""
Database Query Optimization Guide
N+1 Problem Solutions and Best Practices
"""

from sqlalchemy.orm import joinedload, selectinload, contains_eager
from typing import List, Optional


# ==================== N+1 PROBLEM EXAMPLES ====================

# ❌ BAD: N+1 query problem
def get_users_with_mentors_bad(db):
    """Fetches users then makes N queries for mentors"""
    users = db.query(User).all()
    for user in users:
        # N additional queries!
        print(user.mentor_profile.specialization)
    return users


# ✅ GOOD: Using joinedload (eager loading)
def get_users_with_mentors_good(db):
    """Single query with JOIN"""
    users = db.query(User).options(
        joinedload(User.mentor_profile)
    ).all()
    for user in users:
        print(user.mentor_profile.specialization)
    return users


# ==================== OPTIMIZED QUERY FUNCTIONS ====================

class OptimizedQueries:
    """Optimized database queries to avoid N+1 problem"""

    @staticmethod
    def get_user_with_relations(db, user_id: int):
        """
        Get user with all related data in minimal queries
        Uses: joinedload for one-to-one, selectinload for one-to-many
        """
        from app.models import User, Mentor, Session, Enrollment, Progress
        
        user = db.query(User).options(
            joinedload(User.mentor_profile),
            selectinload(User.sessions_as_student),
            selectinload(User.enrollments).joinedload(CourseEnrollment.course),
            selectinload(User.progress_records).joinedload(Progress.course),
        ).filter(User.id == user_id).first()
        
        return user

    @staticmethod
    def get_mentors_with_ratings(db, limit: int = 20):
        """Get mentors with their ratings and reviews"""
        from app.models import Mentor, Review
        
        mentors = db.query(Mentor).options(
            joinedload(Mentor.user),
            selectinload(Mentor.reviews),
            selectinload(Mentor.sessions),
        ).limit(limit).all()
        
        return mentors

    @staticmethod
    def get_courses_with_details(db, category: str = None):
        """Get courses with mentor and enrollment info"""
        from app.models import Course, Mentor, User
        
        query = db.query(Course).options(
            joinedload(Course.mentor).joinedload(Mentor.user),
            selectinload(Course.enrollments),
            selectinload(Course.reviews),
        )
        
        if category:
            query = query.filter(Course.category == category)
        
        return query.all()

    @staticmethod
    def get_sessions_with_participants(db, user_id: int):
        """Get sessions with user and mentor details"""
        from app.models import Session, User, Mentor
        
        sessions = db.query(Session).options(
            joinedload(Session.student).joinedload(User.mentor_profile),
            joinedload(Session.mentor).joinedload(Mentor.user),
        ).filter(
            (Session.student_id == user_id) | (Session.mentor_id == user_id)
        ).all()
        
        return sessions

    @staticmethod
    def get_user_progress_with_courses(db, user_id: int):
        """Get user progress with course details"""
        from app.models import Progress, Course
        
        progress = db.query(Progress).options(
            joinedload(Progress.course),
            joinedload(Progress.user),
        ).filter(Progress.user_id == user_id).all()
        
        return progress

    @staticmethod
    def get_notifications_with_users(db, user_id: int, unread_only: bool = True):
        """Get notifications with user details"""
        from app.models import Notification
        
        query = db.query(Notification).options(
            joinedload(Notification.user),
        ).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).all()


# ==================== PAGINATION WITH OPTIMIZATION ====================

class PaginatedQueries:
    """Optimized paginated queries"""

    @staticmethod
    def get_paginated_courses(db, page: int = 1, limit: int = 20):
        """Get paginated courses with counts"""
        from app.models import Course
        
        offset = (page - 1) * limit
        
        # Get total count
        total = db.query(Course).count()
        
        # Get paginated results with optimizations
        courses = db.query(Course).options(
            joinedload(Course.mentor),
        ).offset(offset).limit(limit).all()
        
        return {
            "items": courses,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }

    @staticmethod
    def get_paginated_mentors(db, page: int = 1, limit: int = 20, specialization: str = None):
        """Get paginated mentors with filters"""
        from app.models import Mentor
        
        offset = (page - 1) * limit
        
        query = db.query(Mentor).options(
            joinedload(Mentor.user),
            selectinload(Mentor.reviews),
        )
        
        if specialization:
            query = query.filter(Mentor.specialization.ilike(f"%{specialization}%"))
        
        total = query.count()
        mentors = query.offset(offset).limit(limit).all()
        
        return {
            "items": mentors,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }


# ==================== BULK OPERATIONS ====================

class BulkOperations:
    """Efficient bulk operations"""

    @staticmethod
    def bulk_create_notifications(db, notifications_data: List[dict]):
        """Bulk create notifications"""
        from app.models import Notification
        
        notifications = [Notification(**data) for data in notifications_data]
        db.bulk_save_objects(notifications)
        db.commit()
        
        return notifications

    @staticmethod
    def bulk_update_progress(db, progress_updates: List[dict]):
        """Bulk update progress records"""
        for update in progress_updates:
            db.query(Progress).filter(
                Progress.user_id == update["user_id"],
                Progress.course_id == update["course_id"]
            ).update({
                "progress_percent": update["progress_percent"],
                "updated_at": func.now()
            })
        
        db.commit()


# ==================== QUERY PROFILING ====================

def analyze_query_performance(db, query_func, *args, **kwargs):
    """Analyze query performance"""
    import time
    from sqlalchemy import event
    
    queries_executed = []
    
    @event.listens_for(db.bind, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        queries_executed.append(statement)
    
    start_time = time.time()
    result = query_func(db, *args, **kwargs)
    end_time = time.time()
    
    print(f"⏱️  Execution time: {end_time - start_time:.4f}s")
    print(f"📊 Queries executed: {len(queries_executed)}")
    for i, query in enumerate(queries_executed, 1):
        print(f"   {i}. {query[:100]}...")
    
    return result, queries_executed, end_time - start_time


# ==================== BEST PRACTICES ====================

"""
## N+1 Prevention Checklist:

1. ✅ Use joinedload() for one-to-one relationships
2. ✅ Use selectinload() for one-to-many relationships
3. ✅ Use contains_eager() when you manually JOIN
4. ✅ Avoid accessing relationships in loops
5. ✅ Use bulk operations for mass updates
6. ✅ Implement pagination with count optimization
7. ✅ Use database indexes on foreign keys
8. ✅ Profile queries in development

## Loading Strategies:

| Relationship Type | Strategy | Example |
|------------------|----------|---------|
| One-to-One | joinedload | User.mentor_profile |
| One-to-Many | selectinload | User.sessions |
| Many-to-Many | selectinload | Course.students |
| Nested | joinedload + selectinload | Course.mentor.user |

## Performance Tips:

1. Limit result sets with .limit()
2. Use .count() before fetching large datasets
3. Avoid SELECT * - specify columns
4. Use database-side filtering (.filter())
5. Implement cursor-based pagination for large datasets
6. Cache frequently accessed data with Redis
7. Use connection pooling (already configured)
8. Monitor slow queries with logging
"""
