-- Database Indexes for Performance Optimization
-- MentorHub - Production Database Optimization
-- Generated: 2026-03-10

-- ==================== USERS ====================
-- Already has indexes on email and username (unique)
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- ==================== MENTORS ====================
CREATE INDEX IF NOT EXISTS idx_mentors_user_id ON mentors(user_id);
CREATE INDEX IF NOT EXISTS idx_mentors_specialization ON mentors(specialization);
CREATE INDEX IF NOT EXISTS idx_mentors_price ON mentors(price_per_hour);
CREATE INDEX IF NOT EXISTS idx_mentors_rating ON mentors(rating);
CREATE INDEX IF NOT EXISTS idx_mentors_created_at ON mentors(created_at);

-- ==================== COURSES ====================
CREATE INDEX IF NOT EXISTS idx_courses_mentor_id ON courses(mentor_id);
CREATE INDEX IF NOT EXISTS idx_courses_category ON courses(category);
CREATE INDEX IF NOT EXISTS idx_courses_level ON courses(level);
CREATE INDEX IF NOT EXISTS idx_courses_price ON courses(price);
CREATE INDEX IF NOT EXISTS idx_courses_rating ON courses(rating);
CREATE INDEX IF NOT EXISTS idx_courses_created_at ON courses(created_at);
CREATE INDEX IF NOT EXISTS idx_courses_enrolled_count ON courses(enrolled_count);

-- ==================== SESSIONS ====================
CREATE INDEX IF NOT EXISTS idx_sessions_student_id ON sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_sessions_mentor_id ON sessions(mentor_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_scheduled_at ON sessions(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);
-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sessions_student_status ON sessions(student_id, status);
CREATE INDEX IF NOT EXISTS idx_sessions_mentor_status ON sessions(mentor_id, status);
CREATE INDEX IF NOT EXISTS idx_sessions_mentor_scheduled ON sessions(mentor_id, scheduled_at);

-- ==================== MESSAGES ====================
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_receiver_id ON messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
-- Composite indexes for chat queries
CREATE INDEX IF NOT EXISTS idx_messages_session_created ON messages(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_messages_sender_receiver ON messages(sender_id, receiver_id);

-- ==================== PAYMENTS ====================
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_session_id ON payments(session_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_provider ON payments(provider);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);
-- Composite indexes
CREATE INDEX IF NOT EXISTS idx_payments_user_status ON payments(user_id, status);
CREATE INDEX IF NOT EXISTS idx_payments_session_status ON payments(session_id, status);

-- ==================== COURSE_ENROLLMENTS ====================
CREATE INDEX IF NOT EXISTS idx_enrollments_user_id ON course_enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON course_enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_status ON course_enrollments(status);
CREATE INDEX IF NOT EXISTS idx_enrollments_created_at ON course_enrollments(created_at);
-- Composite indexes
CREATE INDEX IF NOT EXISTS idx_enrollments_user_course ON course_enrollments(user_id, course_id);

-- ==================== PROGRESS ====================
CREATE INDEX IF NOT EXISTS idx_progress_user_id ON progress(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_course_id ON progress(course_id);
CREATE INDEX IF NOT EXISTS idx_progress_completed ON progress(completed);
CREATE INDEX IF NOT EXISTS idx_progress_updated_at ON progress(updated_at);
-- Composite indexes
CREATE INDEX IF NOT EXISTS idx_progress_user_course ON progress(user_id, course_id);
CREATE INDEX IF NOT EXISTS idx_progress_user_completed ON progress(user_id, completed);

-- ==================== REVIEWS ====================
CREATE INDEX IF NOT EXISTS idx_reviews_mentor_id ON reviews(mentor_id);
CREATE INDEX IF NOT EXISTS idx_reviews_course_id ON reviews(course_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at);
-- Composite indexes
CREATE INDEX IF NOT EXISTS idx_reviews_mentor_rating ON reviews(mentor_id, rating);

-- ==================== NOTIFICATIONS ====================
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
-- Composite indexes for unread notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);

-- ==================== ACHIEVEMENTS ====================
CREATE INDEX IF NOT EXISTS idx_achievements_user_id ON user_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_achievements_achievement_id ON user_achievements(achievement_id);
CREATE INDEX IF NOT EXISTS idx_achievements_unlocked_at ON user_achievements(unlocked_at);

-- ==================== DEVICE_TOKENS ====================
CREATE INDEX IF NOT EXISTS idx_device_tokens_user_id ON device_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_device_tokens_token ON device_tokens(device_token);

-- ==================== PERFORMANCE ANALYSIS ====================
-- Analyze tables after creating indexes
ANALYZE users;
ANALYZE mentors;
ANALYZE courses;
ANALYZE sessions;
ANALYZE messages;
ANALYZE payments;
ANALYZE course_enrollments;
ANALYZE progress;
ANALYZE reviews;
ANALYZE notifications;
ANALYZE user_achievements;
ANALYZE device_tokens;

-- ==================== VERIFICATION ====================
-- Verify indexes created
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- ==================== NOTES ====================
-- Run this script during low-traffic period
-- Index creation may take time on large tables
-- Monitor disk space during index creation
-- Consider using CONCURRENTLY for production:
--   CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_name ON table(column);
