"""
Tests for lesson completion functionality
Integration tests using real SQLite database via TestClient
"""

from fastapi import status

from app.models.course import Course, CourseEnrollment, Lesson
from app.models.mentor import Mentor
from app.models.progress import Progress
from app.models.user import UserRole


class TestLessonCompletion:
    """Integration tests for lesson completion endpoint"""

    def test_complete_lesson_success(self, sync_authenticated_client, db_session, create_user):
        """Test successful lesson completion updates progress and enrollment"""
        client, headers = sync_authenticated_client

        # Create instructor (mentor)
        instructor = create_user(
            email="instructor_lesson@test.com",
            username="instructor_lesson",
            password="InstructorPass123!",
            role=UserRole.MENTOR,
        )
        mentor = Mentor(id=instructor.id, user_id=instructor.id, specialization="Python")
        db_session.add(mentor)
        db_session.commit()

        # Create course
        course = Course(
            title="Test Course",
            description="Test Description",
            difficulty="beginner",
            duration_hours=10,
            price=0,
            instructor_id=mentor.id,
        )
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        # Create lessons
        lesson1 = Lesson(course_id=course.id, title="Lesson 1", order=1, duration_minutes=30)
        lesson2 = Lesson(course_id=course.id, title="Lesson 2", order=2, duration_minutes=45)
        db_session.add_all([lesson1, lesson2])
        db_session.commit()
        db_session.refresh(lesson1)
        db_session.refresh(lesson2)

        # Enroll user in course
        enrollment = CourseEnrollment(user_id=instructor.id, course_id=course.id)
        db_session.add(enrollment)
        db_session.commit()

        # Complete lesson 1
        response = client.post(
            f"/api/v1/courses/lessons/{lesson1.id}/complete",
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["lesson_id"] == lesson1.id
        assert data["course_id"] == course.id
        assert data["course_progress"] == 50
        assert data["completed_lessons"] == 1
        assert data["total_lessons"] == 2
        assert data["course_completed"] is False

        # Verify progress record was created
        progress = db_session.query(Progress).filter(
            Progress.user_id == instructor.id,
            Progress.lesson_id == lesson1.id,
        ).first()
        assert progress is not None
        assert progress.completed is True
        assert progress.progress_percent == 100

    def test_complete_lesson_not_enrolled(self, sync_authenticated_client, db_session, create_user):
        """Test that completing lesson without enrollment returns 403"""
        client, headers = sync_authenticated_client

        # Create instructor (mentor)
        instructor = create_user(
            email="instructor_noe@test.com",
            username="instructor_noe",
            password="InstructorPass123!",
            role=UserRole.MENTOR,
        )
        mentor = Mentor(id=instructor.id, user_id=instructor.id, specialization="Python")
        db_session.add(mentor)
        db_session.commit()

        # Create course (user is NOT enrolled)
        course = Course(
            title="Test Course No Enrollment",
            description="Test Description",
            difficulty="beginner",
            duration_hours=10,
            price=0,
            instructor_id=mentor.id,
        )
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        lesson = Lesson(course_id=course.id, title="Lesson 1", order=1, duration_minutes=30)
        db_session.add(lesson)
        db_session.commit()
        db_session.refresh(lesson)

        # Try to complete lesson without enrollment
        response = client.post(
            f"/api/v1/courses/lessons/{lesson.id}/complete",
            headers=headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "не записаны" in response.json()["detail"]

    def test_complete_lesson_updates_progress(self, sync_authenticated_client, db_session, create_user):
        """Test that completing multiple lessons updates course progress correctly"""
        client, headers = sync_authenticated_client

        # Create instructor
        instructor = create_user(
            email="instructor_prog@test.com",
            username="instructor_prog",
            password="InstructorPass123!",
            role=UserRole.MENTOR,
        )
        mentor = Mentor(id=instructor.id, user_id=instructor.id, specialization="Python")
        db_session.add(mentor)
        db_session.commit()

        # Create course with 4 lessons
        course = Course(
            title="Test Course Progress",
            description="Test Description",
            difficulty="beginner",
            duration_hours=10,
            price=0,
            instructor_id=mentor.id,
        )
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        lessons = [
            Lesson(course_id=course.id, title=f"Lesson {i}", order=i, duration_minutes=30)
            for i in range(1, 5)
        ]
        db_session.add_all(lessons)
        db_session.commit()
        for lesson in lessons:
            db_session.refresh(lesson)

        # Enroll user
        enrollment = CourseEnrollment(user_id=instructor.id, course_id=course.id)
        db_session.add(enrollment)
        db_session.commit()

        # Complete 2 out of 4 lessons (50%)
        response = client.post(
            f"/api/v1/courses/lessons/{lessons[0].id}/complete",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["course_progress"] == 25

        response = client.post(
            f"/api/v1/courses/lessons/{lessons[1].id}/complete",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["course_progress"] == 50

        # Verify enrollment progress was updated
        db_session.refresh(enrollment)
        assert enrollment.progress_percent == 50

    def test_complete_all_lessons_completes_course(self, sync_authenticated_client, db_session, create_user):
        """Test that completing all lessons marks course as completed"""
        client, headers = sync_authenticated_client

        # Create instructor
        instructor = create_user(
            email="instructor_complete@test.com",
            username="instructor_complete",
            password="InstructorPass123!",
            role=UserRole.MENTOR,
        )
        mentor = Mentor(id=instructor.id, user_id=instructor.id, specialization="Python")
        db_session.add(mentor)
        db_session.commit()

        # Create course with 2 lessons
        course = Course(
            title="Test Course Complete",
            description="Test Description",
            difficulty="beginner",
            duration_hours=10,
            price=0,
            instructor_id=mentor.id,
        )
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        lessons = [
            Lesson(course_id=course.id, title=f"Lesson {i}", order=i, duration_minutes=30)
            for i in range(1, 3)
        ]
        db_session.add_all(lessons)
        db_session.commit()
        for lesson in lessons:
            db_session.refresh(lesson)

        # Enroll user
        enrollment = CourseEnrollment(user_id=instructor.id, course_id=course.id)
        db_session.add(enrollment)
        db_session.commit()

        # Complete all lessons
        for lesson in lessons:
            response = client.post(
                f"/api/v1/courses/lessons/{lesson.id}/complete",
                headers=headers,
            )
            assert response.status_code == status.HTTP_200_OK

        # Last lesson should mark course as completed
        final_response = client.post(
            f"/api/v1/courses/lessons/{lessons[-1].id}/complete",
            headers=headers,
        )
        data = final_response.json()
        assert data["course_progress"] == 100
        assert data["course_completed"] is True

        # Verify enrollment
        db_session.refresh(enrollment)
        assert enrollment.completed is True
        assert enrollment.completed_at is not None
        assert enrollment.progress_percent == 100

    def test_complete_lesson_idempotent(self, sync_authenticated_client, db_session, create_user):
        """Test that completing the same lesson twice doesn't create duplicate progress records"""
        client, headers = sync_authenticated_client

        # Create instructor
        instructor = create_user(
            email="instructor_idem@test.com",
            username="instructor_idem",
            password="InstructorPass123!",
            role=UserRole.MENTOR,
        )
        mentor = Mentor(id=instructor.id, user_id=instructor.id, specialization="Python")
        db_session.add(mentor)
        db_session.commit()

        # Create course with 1 lesson
        course = Course(
            title="Test Course Idempotent",
            description="Test Description",
            difficulty="beginner",
            duration_hours=10,
            price=0,
            instructor_id=mentor.id,
        )
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        lesson = Lesson(course_id=course.id, title="Lesson 1", order=1, duration_minutes=30)
        db_session.add(lesson)
        db_session.commit()
        db_session.refresh(lesson)

        # Enroll user
        enrollment = CourseEnrollment(user_id=instructor.id, course_id=course.id)
        db_session.add(enrollment)
        db_session.commit()

        # Complete lesson twice
        response1 = client.post(
            f"/api/v1/courses/lessons/{lesson.id}/complete",
            headers=headers,
        )
        assert response1.status_code == status.HTTP_200_OK

        response2 = client.post(
            f"/api/v1/courses/lessons/{lesson.id}/complete",
            headers=headers,
        )
        assert response2.status_code == status.HTTP_200_OK

        # Verify only one progress record exists
        progress_count = db_session.query(Progress).filter(
            Progress.user_id == instructor.id,
            Progress.lesson_id == lesson.id,
        ).count()
        assert progress_count == 1

        # Both responses should report the same progress
        assert response1.json()["course_progress"] == response2.json()["course_progress"]


class TestProgressCalculation:
    """Tests for course progress calculation"""

    def test_progress_calculation_empty(self, sync_authenticated_client, db_session, create_user):
        """Test 0% progress when no lessons completed"""
        client, headers = sync_authenticated_client

        # Create instructor
        instructor = create_user(
            email="instructor_empty@test.com",
            username="instructor_empty",
            password="InstructorPass123!",
            role=UserRole.MENTOR,
        )
        mentor = Mentor(id=instructor.id, user_id=instructor.id, specialization="Python")
        db_session.add(mentor)
        db_session.commit()

        # Create course with lessons but no completions
        course = Course(
            title="Test Course Empty",
            description="Test Description",
            difficulty="beginner",
            duration_hours=10,
            price=0,
            instructor_id=mentor.id,
        )
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        lessons = [
            Lesson(course_id=course.id, title=f"Lesson {i}", order=i, duration_minutes=30)
            for i in range(1, 4)
        ]
        db_session.add_all(lessons)
        db_session.commit()
        for lesson in lessons:
            db_session.refresh(lesson)

        # Enroll user
        enrollment = CourseEnrollment(user_id=instructor.id, course_id=course.id)
        db_session.add(enrollment)
        db_session.commit()

        # Enrollment should have 0% progress
        db_session.refresh(enrollment)
        assert enrollment.progress_percent == 0
        assert enrollment.completed is False

    def test_progress_calculation_partial(self, sync_authenticated_client, db_session, create_user):
        """Test partial progress (e.g., 66% when 2 of 3 lessons completed)"""
        client, headers = sync_authenticated_client

        # Create instructor
        instructor = create_user(
            email="instructor_partial@test.com",
            username="instructor_partial",
            password="InstructorPass123!",
            role=UserRole.MENTOR,
        )
        mentor = Mentor(id=instructor.id, user_id=instructor.id, specialization="Python")
        db_session.add(mentor)
        db_session.commit()

        # Create course with 3 lessons
        course = Course(
            title="Test Course Partial",
            description="Test Description",
            difficulty="beginner",
            duration_hours=10,
            price=0,
            instructor_id=mentor.id,
        )
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        lessons = [
            Lesson(course_id=course.id, title=f"Lesson {i}", order=i, duration_minutes=30)
            for i in range(1, 4)
        ]
        db_session.add_all(lessons)
        db_session.commit()
        for lesson in lessons:
            db_session.refresh(lesson)

        # Enroll user
        enrollment = CourseEnrollment(user_id=instructor.id, course_id=course.id)
        db_session.add(enrollment)
        db_session.commit()

        # Complete 2 out of 3 lessons
        for lesson in lessons[:2]:
            response = client.post(
                f"/api/v1/courses/lessons/{lesson.id}/complete",
                headers=headers,
            )
            assert response.status_code == status.HTTP_200_OK

        # Check progress is 66% (2/3 = 66.6... -> int = 66)
        db_session.refresh(enrollment)
        assert enrollment.progress_percent == 66
        assert enrollment.completed is False

    def test_progress_calculation_complete(self, sync_authenticated_client, db_session, create_user):
        """Test 100% progress when all lessons completed"""
        client, headers = sync_authenticated_client

        # Create instructor
        instructor = create_user(
            email="instructor_full@test.com",
            username="instructor_full",
            password="InstructorPass123!",
            role=UserRole.MENTOR,
        )
        mentor = Mentor(id=instructor.id, user_id=instructor.id, specialization="Python")
        db_session.add(mentor)
        db_session.commit()

        # Create course with 5 lessons
        course = Course(
            title="Test Course Full",
            description="Test Description",
            difficulty="beginner",
            duration_hours=10,
            price=0,
            instructor_id=mentor.id,
        )
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)

        lessons = [
            Lesson(course_id=course.id, title=f"Lesson {i}", order=i, duration_minutes=30)
            for i in range(1, 6)
        ]
        db_session.add_all(lessons)
        db_session.commit()
        for lesson in lessons:
            db_session.refresh(lesson)

        # Enroll user
        enrollment = CourseEnrollment(user_id=instructor.id, course_id=course.id)
        db_session.add(enrollment)
        db_session.commit()

        # Complete all 5 lessons
        for lesson in lessons:
            response = client.post(
                f"/api/v1/courses/lessons/{lesson.id}/complete",
                headers=headers,
            )
            assert response.status_code == status.HTTP_200_OK

        # Final progress should be 100%
        final_response = client.post(
            f"/api/v1/courses/lessons/{lessons[-1].id}/complete",
            headers=headers,
        )
        data = final_response.json()
        assert data["course_progress"] == 100
        assert data["completed_lessons"] == 5
        assert data["total_lessons"] == 5
        assert data["course_completed"] is True

        db_session.refresh(enrollment)
        assert enrollment.progress_percent == 100
        assert enrollment.completed is True
