#!/bin/bash
set -e

echo "========================================="
echo "MentorHub Backend - Starting Application"
echo "========================================="

# Validate required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is not set!"
    echo "Please configure DATABASE_URL in Amvera dashboard"
    exit 1
fi

echo "✅ DATABASE_URL: ${DATABASE_URL%%:*}://***:***@${DATABASE_URL##*@}"

# Wait for database to be ready with exponential backoff
echo "Waiting for PostgreSQL..."
python -c "
import time
import psycopg2
from urllib.parse import urlparse

db_url = '$DATABASE_URL'
result = urlparse(db_url)

max_retries = 30
retry_count = 0
backoff_time = 1

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        conn.close()
        print('✅ PostgreSQL is ready!')
        break
    except Exception as e:
        retry_count += 1
        print(f'Waiting for PostgreSQL... ({retry_count}/{max_retries})')
        time.sleep(backoff_time)
        backoff_time = min(backoff_time * 1.5, 10)  # Exponential backoff, max 10s
        if retry_count >= max_retries:
            print('❌ PostgreSQL connection timeout!')
            raise
"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || {
    echo "⚠️  Migrations failed, but continuing..."
}

# Start application with optimized settings
echo "Starting FastAPI application..."
echo "Port: 8000"
echo "Workers: 4"
echo "========================================="

# Use gunicorn for better performance in production
if [ "$ENVIRONMENT" = "production" ]; then
    exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 app.main:app
else
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
fi