#!/usr/bin/env python3
"""
Seed script for courses and lessons
Initializes the database with sample course data
"""

import os
import sys
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models.course import Course, Lesson
from app.models.user import User
from app.models.mentor import Mentor
from app.database import Base, engine, SessionLocal

def seed_courses(db: Session):
    """Seed the database with sample courses and lessons"""
    
    # Check if we already have courses
    existing_courses = db.query(Course).count()
    if existing_courses > 0:
        print("_courses already exist in the database. Skipping seeding.")
        return

    # Create sample instructors (assuming we have users with IDs 1 and 2 as mentors)
    try:
        # Try to get existing mentors
        mentor1 = db.query(Mentor).filter(Mentor.id == 1).first()
        mentor2 = db.query(Mentor).filter(Mentor.id == 2).first()
        
        if not mentor1 or not mentor2:
            print("Mentors not found. Please run user seeding first.")
            return
            
        # Create sample courses
        courses_data = [
            {
                "title": "React для профессионалов",
                "description": "Полный курс по современному React 18. Хуки, контекст, оптимизация производительности и лучшие практики.",
                "category": "Frontend",
                "difficulty": "intermediate",
                "duration_hours": 40,
                "price": 299900,  # in cents
                "thumbnail_url": None,
                "instructor_id": mentor1.id,
                "lessons": [
                    {
                        "title": "Введение в React 18",
                        "description": "Основы React, JSX, компоненты",
                        "content": "Содержание урока...",
                        "duration_minutes": 60,
                        "order": 1,
                        "is_preview": True
                    },
                    {
                        "title": "Хуки в React",
                        "description": "useState, useEffect, useContext",
                        "content": "Содержание урока...",
                        "duration_minutes": 90,
                        "order": 2,
                        "is_preview": False
                    }
                ]
            },
            {
                "title": "TypeScript с нуля до мастера",
                "description": "Глубокое изучение TypeScript. Типы, интерфейсы, дженерики, типизация и промышленные практики.",
                "category": "Frontend",
                "difficulty": "beginner",
                "duration_hours": 35,
                "price": 199900,  # in cents
                "thumbnail_url": None,
                "instructor_id": mentor2.id,
                "lessons": [
                    {
                        "title": "Основы TypeScript",
                        "description": "Типы, интерфейсы, перечисления",
                        "content": "Содержание урока...",
                        "duration_minutes": 75,
                        "order": 1,
                        "is_preview": True
                    }
                ]
            }
        ]
        
        # Insert courses and lessons
        for course_data in courses_data:
            lessons_data = course_data.pop("lessons", [])
            
            # Create course
            course = Course(**course_data)
            db.add(course)
            db.flush()  # Get the course ID
            
            # Create lessons
            for lesson_data in lessons_data:
                lesson_data["course_id"] = course.id
                lesson = Lesson(**lesson_data)
                db.add(lesson)
        
        db.commit()
        print(f"Successfully seeded {len(courses_data)} courses with lessons")
        
    except IntegrityError as e:
        db.rollback()
        print(f"Error seeding courses: {e}")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")

def main():
    """Main function to run the seeding"""
    print("Seeding courses and lessons...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = SessionLocal()
    
    try:
        seed_courses(db)
    finally:
        db.close()
    
    print("Course seeding completed!")

if __name__ == "__main__":
    main()