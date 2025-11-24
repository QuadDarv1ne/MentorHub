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

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
python -c "
import time
import psycopg2
from urllib.parse import urlparse

db_url = '$DATABASE_URL'
result = urlparse(db_url)

max_retries = 30
retry_count = 0

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
        time.sleep(2)
        if retry_count >= max_retries:
            print('❌ PostgreSQL connection timeout!')
            raise
"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || {
    echo "⚠️  Migrations failed, but continuing..."
}

# Start application
echo "Starting FastAPI application..."
echo "Port: 8000"
echo "Workers: 2"
echo "========================================="

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
