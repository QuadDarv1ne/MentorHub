"""
Constants module for MentorHub Backend
Centralized constants for maintainability and consistency
"""

import string

# ==================== TIME CONSTANTS (SECONDS) ====================
# Cache TTLs
CACHE_TTL_DEFAULT = 300  # 5 minutes
CACHE_TTL_USER = 600  # 10 minutes
CACHE_TTL_MENTOR = 900  # 15 minutes
CACHE_TTL_COURSE = 1800  # 30 minutes
CACHE_TTL_REVIEW = 300  # 5 minutes
CACHE_TTL_STATS = 300  # 5 minutes
CACHE_TTL_ANALYTICS = 600  # 10 minutes
CACHE_TTL_SUBSCRIPTION = 3600  # 1 hour

# Timeouts
TIMEOUT_STATEMENT = 30000  # 30 seconds (milliseconds)
TIMEOUT_API_REQUEST = 30000  # 30 seconds (milliseconds)
TIMEOUT_HTTP_REQUEST = 10000  # 10 seconds (milliseconds)
TIMEOUT_DB_CONNECT = 10  # 10 seconds

# Session & Auth
SESSION_EXPIRE_SECONDS = 7 * 24 * 60 * 60  # 7 days
OAUTH_STATE_EXPIRE_SECONDS = 600  # 10 minutes
LOCKOUT_DURATION = 900  # 15 minutes
CLEANUP_INTERVAL = 3600  # 1 hour

# Celery
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

# HSTS
HSTS_MAX_AGE = 31536000  # 1 year in seconds


# ==================== SIZE CONSTANTS (BYTES) ====================
# File uploads
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_FILE_SIZE_CHAT = 10 * 1024 * 1024  # 10 MB for chat attachments

# Request/Response
MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_BODY_LENGTH_LOG = 1000  # 1000 bytes for logging
MAX_TRUNCATE_LOG_LENGTH = 1000  # 1000 characters

# Database
DB_POOL_SIZE_DEFAULT = 5
DB_POOL_SIZE_MAX = 20
DB_MAX_OVERFLOW = 10
DB_POOL_RECYCLE = 1800  # 30 minutes
DB_POOL_TIMEOUT = 30  # 30 seconds

# Cache
MAX_MEMORY_CACHE_ITEMS = 1000
MAX_CACHE_TTL = 3600  # 1 hour


# ==================== RATE LIMITING ====================
RATE_LIMIT_DEFAULT_REQUESTS = 100
RATE_LIMIT_DEFAULT_WINDOW = 60  # 1 minute
RATE_LIMIT_AUTHENTICATED_REQUESTS = 1000
RATE_LIMIT_AUTHENTICATED_WINDOW = 60  # 1 minute
RATE_LIMIT_ANONYMOUS_REQUESTS = 20
RATE_LIMIT_ANONYMOUS_WINDOW = 60  # 1 minute
RATE_LIMIT_MAX_ATTEMPTS = 100
RATE_LIMIT_DISABLED = 999999


# ==================== PAGINATION ====================
DEFAULT_PAGE_SIZE = 20
DEFAULT_PAGE = 1
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1
DEFAULT_LIMIT = 50
MAX_LIMIT = 100
MIN_LIMIT = 1


# ==================== VALIDATION ====================
# Email
EMAIL_MAX_LENGTH = 254  # RFC 5321

# Username
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 100

# Password
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

# Text fields
TEXT_FIELD_MAX_LENGTH = 255
DESCRIPTION_MAX_LENGTH = 1000
COMMENT_MAX_LENGTH = 2000
SANITIZE_TEXT_MAX_LENGTH = 5000
URL_MAX_LENGTH = 2048
AGORA_TOKEN_MAX_LENGTH = 2048
ACCESS_TOKEN_MAX_LENGTH = 2048

# ==================== OAUTH VALIDATION ====================
# OAuth secrets minimum length for security
OAUTH_SECRET_MIN_LENGTH = 10  # Minimum length for OAuth client secrets
OAUTH_TOKEN_EXPIRE_SECONDS = 3600  # 1 hour

# Google OAuth
GOOGLE_SCOPE_DEFAULT = "https://www.googleapis.com/auth/calendar"

# Microsoft OAuth
MICROSOFT_TENANT_DEFAULT = "common"
MICROSOFT_SCOPE_DEFAULT = "Calendars.ReadWrite"

# ==================== AGORA VALIDATION ====================
AGORA_TOKEN_EXPIRE_DEFAULT = 3600  # 1 hour in seconds
AGORA_TOKEN_EXPIRE_MAX = 86400  # 24 hours in seconds
AGORA_ROLE_PUBLISHER = "publisher"
AGORA_ROLE_SUBSCRIBER = "subscriber"
REFRESH_TOKEN_MAX_LENGTH = 2048

# Phone
PHONE_MAX_LENGTH = 20


# ==================== SECURITY ====================
# Brute force protection
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900  # 15 minutes
BRUTE_FORCE_CLEANUP_INTERVAL = 3600  # 1 hour

# Password strength
PASSWORD_MIN_LENGTH_STRENGTH = 12

# Security headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

# Allowed hosts wildcard check
ALLOWED_HOSTS_WILDCARD = "*"


# ==================== DATABASE ====================
# Connection pool settings
DB_MIN_POOL_SIZE = 2
DB_MAX_POOL_SIZE = 10
DB_POOL_OVERFLOW = 20
DB_ECHO_DEBUG = False

# Statement timeout
STATEMENT_TIMEOUT_MS = 30000  # 30 seconds


# ==================== REDIS ====================
REDIS_DEFAULT_DB = 0
REDIS_DEFAULT_PORT = 6379


# ==================== WEBSOCKET ====================
WS_CLEANUP_INTERVAL = 900  # 15 minutes
WS_STATUS_POLICY_VIOLATION = 1008
WS_STATUS_INTERNAL_ERROR = 1011


# ==================== EMAIL ====================
SMTP_PORT_TLS = 587
SMTP_PORT_SSL = 465
EMAIL_FOOTER_FONT_SIZE = 12


# ==================== MONITORING ====================
# Prometheus histogram buckets (milliseconds)
PROMETHEUS_BUCKETS = (
    100, 500, 1000, 5000, 10000,
    50000, 100000, 500000, 1000000,
    float("inf")
)
PROMETHEUS_DB_BUCKETS = (
    60, 300, 600, 1800, 3600, 7200,
    float("inf")
)

# Request rate monitoring
MAX_REQUEST_TIMES_STORED = 1000


# ==================== LOGGING ====================
LOG_MAX_BYTES_DEFAULT = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT_DEFAULT = 3
LOG_ROTATION_SIZE = 5 * 1024 * 1024  # 5 MB


# ==================== PORTS ====================
DEFAULT_BACKEND_PORT = 8001
DEFAULT_FRONTEND_PORT = 3000
DEFAULT_REDIS_PORT = 6379
DEFAULT_POSTGRES_PORT = 5432
DEFAULT_PGBOUNCER_PORT = 6432

# Exclude ports (known services)
EXCLUDE_PORTS = [3000, 12600, 19001, 19005, 19006, 6060, 6061, 81]


# ==================== RETRIES ====================
MAX_RETRIES = 5
MAX_RECONNECT_ATTEMPTS = 5


# ==================== MISC ====================
# Video calls
AGORA_TOKEN_EXPIRATION = 3600  # 1 hour

# Export
EXPORT_BATCH_SIZE = 100

# Search
SEARCH_QUERY_MAX_LENGTH = 100

# Two-factor auth
TOTP_CODE_LENGTH = 6
TOTP_CODE_EXPIRY = 30  # 30 seconds

# Backup codes
BACKUP_CODES_COUNT = 10
BACKUP_CODES_LENGTH = 12

# Achievements
ACHIEVEMENTS_DEFAULT_LIMIT = 100
ACHIEVEMENTS_MAX_LIMIT = 100

# Messages
MESSAGES_DEFAULT_LIMIT = 50
MESSAGES_MAX_LIMIT = 100

# Chat rooms
CHAT_ROOMS_DEFAULT_LIMIT = 50
CHAT_ROOMS_MAX_LIMIT = 100

# Video calls
VIDEO_CALLS_DEFAULT_LIMIT = 50
VIDEO_CALLS_MAX_LIMIT = 100

# Notifications
NOTIFICATIONS_DEFAULT_LIMIT = 50
NOTIFICATIONS_MAX_LIMIT = 100

# Payments
PAYMENTS_DEFAULT_LIMIT = 100
PAYMENTS_MAX_LIMIT = 100
PAYMENTS_USER_LIMIT = 20

# Sessions
SESSIONS_DEFAULT_LIMIT = 100
SESSIONS_MAX_LIMIT = 100

# Mentors
MENTORS_DEFAULT_LIMIT = 100
MENTORS_MAX_LIMIT = 100

# Courses
COURSES_DEFAULT_LIMIT = 100
COURSES_MAX_LIMIT = 100

# SBP Service
SBP_PAYMENT_DEFAULT_AMOUNT = 5000  # 50 rubles in kopecks
SBP_REQUEST_TIMEOUT = 30  # 30 seconds

# Stripe mock
STRIPE_MOCK_TRIAL_PERIOD_DAYS = 14
STRIPE_MOCK_TIMESTAMP = 1234567890
SECONDS_PER_DAY = 86400

# Allowed extensions
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"]

# Common passwords list (truncated for brevity - full list in security.py)
COMMON_PASSWORDS = [
    "password", "123456", "12345678", "qwerty", "abc123", "monkey",
    "1234567", "letmein", "trustno1", "dragon", "baseball", "iloveyou",
    "123123", "654321",
]

# Password alphabet for generation (built from string constants)
PASSWORD_ALPHABET = string.ascii_letters + string.digits + "!@#$%^&*()"

# Typing indicator timeout
TYPING_INDICATOR_TIMEOUT = 3000  # 3 seconds

# Loading delay
LOADING_DELAY = 300  # 300ms
LOADING_DELAY_LONG = 500  # 500ms
LOADING_DELAY_VERY_LONG = 2000  # 2 seconds

# Copy to clipboard timeout
COPY_TIMEOUT = 2000  # 2 seconds

# Cache minimum TTL
CACHE_MIN_TTL = 60  # 1 minute

# Throttle
THROTTLE_MS = 1000  # 1 second

# Disk/Memory units
BYTES_PER_MB = 1024 * 1024
BYTES_PER_GB = 1024 * 1024 * 1024

# Calendar
CALENDAR_EMPTY_DAYS = 7  # Show 7 empty days in week view
CALENDAR_CELL_MIN_HEIGHT = 100  # pixels

# Performance
PERFORMANCE_CHECK_INTERVAL = 100  # ms
PERFORMANCE_WARNING_THRESHOLD = 1000  # ms

# Toast
TOAST_CLOSE_DELAY = 300  # ms

# Test timeouts
TEST_TIMEOUT = 2000  # 2 seconds

# Form validation
FORM_SAVE_TIMEOUT = 2000  # 2 seconds

# Payment processing
PAYMENT_PROCESSING_DELAY = 1500  # 1.5 seconds
PAYMENT_SUCCESS_DISPLAY_TIME = 3000  # 3 seconds

# Reconnection
RECONNECT_DELAY = 5000  # 5 seconds

# Message history
MESSAGE_HISTORY_DEFAULT_LIMIT = 50

# Pagination
MAX_VISIBLE_PAGES = 5

# File size validation
FILE_SIZE_1MB = 1024 * 1024
FILE_SIZE_5MB = 5 * 1024 * 1024
FILE_SIZE_10MB = 10 * 1024 * 1024

# Request rate monitoring buckets
REQUEST_RATE_BUCKETS = (100, 500, 1000, 5000, 10000)

# Minimum pool size for database
MINIMUM_POOL_SIZE = 10

# Default rate limit for setup
DEFAULT_RATE_LIMIT_REQUESTS = 100
DEFAULT_RATE_LIMIT_PERIOD = 60  # seconds (1 minute, consistent with RATE_LIMIT_DEFAULT_WINDOW)
DEFAULT_MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB
