"""
Analytics Service
Сбор и анализ статистики платформы
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import func, desc, and_
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.session import Session as MentorSession, SessionStatus
from app.models.course import Course, CourseEnrollment
from app.models.progress import Progress
from app.models.review import Review
from app.models.payment import Payment

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Сервис для сбора аналитики"""

    def __init__(self, db: Session):
        self.db = db

    def get_platform_stats(self) -> Dict:
        """
        Общая статистика платформы
        
        Returns:
            Dict с ключевыми метриками
        """
        try:
            # Пользователи
            total_users = self.db.query(User).count()
            total_students = self.db.query(User).filter(User.role == UserRole.STUDENT).count()
            total_mentors = self.db.query(User).filter(User.role == UserRole.MENTOR).count()
            verified_users = self.db.query(User).filter(User.is_verified == True).count()

            # Сессии
            total_sessions = self.db.query(MentorSession).count()
            completed_sessions = self.db.query(MentorSession).filter(
                MentorSession.status == SessionStatus.COMPLETED
            ).count()
            scheduled_sessions = self.db.query(MentorSession).filter(
                MentorSession.status == SessionStatus.SCHEDULED
            ).count()

            # Курсы
            total_courses = self.db.query(Course).count()
            published_courses = self.db.query(Course).filter(Course.is_published == True).count()
            total_enrollments = self.db.query(CourseEnrollment).count()

            # Отзывы
            total_reviews = self.db.query(Review).count()
            avg_rating = self.db.query(func.avg(Review.rating)).scalar() or 0.0

            # Платежи
            total_revenue = self.db.query(func.sum(Payment.amount)).scalar() or 0.0

            return {
                "users": {
                    "total": total_users,
                    "students": total_students,
                    "mentors": total_mentors,
                    "verified": verified_users,
                    "verification_rate": round((verified_users / total_users * 100) if total_users > 0 else 0, 2)
                },
                "sessions": {
                    "total": total_sessions,
                    "completed": completed_sessions,
                    "scheduled": scheduled_sessions,
                    "completion_rate": round((completed_sessions / total_sessions * 100) if total_sessions > 0 else 0, 2)
                },
                "courses": {
                    "total": total_courses,
                    "published": published_courses,
                    "enrollments": total_enrollments,
                    "avg_enrollments_per_course": round(total_enrollments / total_courses if total_courses > 0 else 0, 2)
                },
                "reviews": {
                    "total": total_reviews,
                    "average_rating": round(avg_rating, 2)
                },
                "revenue": {
                    "total": float(total_revenue),
                    "currency": "RUB"
                }
            }

        except Exception as e:
            logger.error(f"Error getting platform stats: {e}")
            raise

    def get_user_growth(self, days: int = 30) -> List[Dict]:
        """
        График роста пользователей
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            List[Dict] с датами и количеством новых пользователей
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Группируем по дням
            growth_data = self.db.query(
                func.date(func.from_unixtime(User.created_at)).label('date'),
                func.count(User.id).label('count')
            ).filter(
                User.created_at >= int(start_date.timestamp())
            ).group_by(
                func.date(func.from_unixtime(User.created_at))
            ).order_by('date').all()

            return [
                {
                    "date": str(row.date),
                    "new_users": row.count
                }
                for row in growth_data
            ]

        except Exception as e:
            logger.error(f"Error getting user growth: {e}")
            raise

    def get_session_analytics(self, days: int = 30) -> Dict:
        """
        Аналитика по сессиям
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Dict с метриками сессий
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            start_timestamp = int(start_date.timestamp())

            # Сессии за период
            sessions = self.db.query(MentorSession).filter(
                MentorSession.created_at >= start_timestamp
            ).all()

            if not sessions:
                return {
                    "total": 0,
                    "by_status": {},
                    "avg_duration": 0,
                    "top_mentors": []
                }

            # По статусам
            by_status = {}
            for status in SessionStatus:
                count = sum(1 for s in sessions if s.status == status)
                by_status[status.value] = count

            # Средняя длительность
            durations = [s.duration_minutes for s in sessions if s.duration_minutes]
            avg_duration = sum(durations) / len(durations) if durations else 0

            # Топ менторов по сессиям
            top_mentors = self.db.query(
                MentorSession.mentor_id,
                func.count(MentorSession.id).label('session_count')
            ).filter(
                MentorSession.created_at >= start_timestamp
            ).group_by(
                MentorSession.mentor_id
            ).order_by(
                desc('session_count')
            ).limit(10).all()

            return {
                "total": len(sessions),
                "by_status": by_status,
                "avg_duration_minutes": round(avg_duration, 2),
                "top_mentors": [
                    {"mentor_id": row.mentor_id, "sessions": row.session_count}
                    for row in top_mentors
                ]
            }

        except Exception as e:
            logger.error(f"Error getting session analytics: {e}")
            raise

    def get_course_performance(self, course_id: Optional[int] = None) -> Dict:
        """
        Анализ производительности курсов
        
        Args:
            course_id: ID курса (опционально, для конкретного курса)
            
        Returns:
            Dict с метриками курса/курсов
        """
        try:
            query = self.db.query(Course)
            if course_id:
                query = query.filter(Course.id == course_id)

            courses = query.all()

            if not courses:
                return {}

            results = []
            for course in courses:
                # Количество студентов
                enrollment_count = self.db.query(CourseEnrollment).filter(
                    CourseEnrollment.course_id == course.id
                ).count()

                # Прогресс
                avg_progress = self.db.query(
                    func.avg(Progress.progress_percentage)
                ).filter(
                    Progress.course_id == course.id
                ).scalar() or 0.0

                # Завершили курс
                completed_count = self.db.query(Progress).filter(
                    and_(
                        Progress.course_id == course.id,
                        Progress.progress_percentage >= 100
                    )
                ).count()

                # Средний рейтинг
                avg_rating = self.db.query(
                    func.avg(Review.rating)
                ).filter(
                    Review.course_id == course.id
                ).scalar() or 0.0

                results.append({
                    "course_id": course.id,
                    "course_title": course.title,
                    "enrollments": enrollment_count,
                    "avg_progress": round(avg_progress, 2),
                    "completed": completed_count,
                    "completion_rate": round((completed_count / enrollment_count * 100) if enrollment_count > 0 else 0, 2),
                    "avg_rating": round(avg_rating, 2)
                })

            return results[0] if course_id else {"courses": results}

        except Exception as e:
            logger.error(f"Error getting course performance: {e}")
            raise

    def get_revenue_analytics(self, days: int = 30) -> Dict:
        """
        Аналитика по доходам
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Dict с финансовыми метриками
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            start_timestamp = int(start_date.timestamp())

            # Платежи за период
            payments = self.db.query(Payment).filter(
                Payment.created_at >= start_timestamp,
                Payment.status == "completed"
            ).all()

            if not payments:
                return {
                    "total_revenue": 0,
                    "transaction_count": 0,
                    "avg_transaction": 0,
                    "daily_revenue": []
                }

            total_revenue = sum(p.amount for p in payments)
            avg_transaction = total_revenue / len(payments)

            # По дням
            daily_revenue = self.db.query(
                func.date(func.from_unixtime(Payment.created_at)).label('date'),
                func.sum(Payment.amount).label('revenue')
            ).filter(
                Payment.created_at >= start_timestamp,
                Payment.status == "completed"
            ).group_by(
                func.date(func.from_unixtime(Payment.created_at))
            ).order_by('date').all()

            return {
                "total_revenue": float(total_revenue),
                "transaction_count": len(payments),
                "avg_transaction": round(avg_transaction, 2),
                "daily_revenue": [
                    {
                        "date": str(row.date),
                        "revenue": float(row.revenue)
                    }
                    for row in daily_revenue
                ]
            }

        except Exception as e:
            logger.error(f"Error getting revenue analytics: {e}")
            raise

    def get_user_engagement(self, user_id: int) -> Dict:
        """
        Анализ вовлеченности пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict с метриками активности
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")

            # Сессии
            sessions_count = self.db.query(MentorSession).filter(
                MentorSession.student_id == user_id
            ).count()

            # Курсы
            enrollments_count = self.db.query(CourseEnrollment).filter(
                CourseEnrollment.user_id == user_id
            ).count()

            # Прогресс
            avg_progress = self.db.query(
                func.avg(Progress.progress_percentage)
            ).filter(
                Progress.user_id == user_id
            ).scalar() or 0.0

            # Отзывы
            reviews_count = self.db.query(Review).filter(
                Review.user_id == user_id
            ).count()

            # Последняя активность
            last_session = self.db.query(MentorSession).filter(
                MentorSession.student_id == user_id
            ).order_by(desc(MentorSession.created_at)).first()

            last_activity = None
            if last_session:
                last_activity = datetime.fromtimestamp(last_session.created_at).isoformat()

            return {
                "user_id": user_id,
                "username": user.username,
                "sessions_attended": sessions_count,
                "courses_enrolled": enrollments_count,
                "avg_progress": round(avg_progress, 2),
                "reviews_written": reviews_count,
                "last_activity": last_activity,
                "engagement_score": self._calculate_engagement_score(
                    sessions_count, enrollments_count, avg_progress, reviews_count
                )
            }

        except Exception as e:
            logger.error(f"Error getting user engagement: {e}")
            raise

    def _calculate_engagement_score(
        self, 
        sessions: int, 
        enrollments: int, 
        avg_progress: float, 
        reviews: int
    ) -> int:
        """
        Вычисление engagement score (0-100)
        
        Args:
            sessions: Количество сессий
            enrollments: Количество курсов
            avg_progress: Средний прогресс
            reviews: Количество отзывов
            
        Returns:
            int: Engagement score
        """
        score = 0
        
        # Сессии (до 30 баллов)
        score += min(sessions * 3, 30)
        
        # Курсы (до 25 баллов)
        score += min(enrollments * 5, 25)
        
        # Прогресс (до 30 баллов)
        score += min(avg_progress * 0.3, 30)
        
        # Отзывы (до 15 баллов)
        score += min(reviews * 5, 15)
        
        return min(int(score), 100)
