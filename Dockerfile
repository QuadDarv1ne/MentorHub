# ==================== FRONTEND BUILD STAGE ====================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files for dependency installation
COPY frontend/package*.json ./

# Install dependencies with frozen lockfile for reproducible builds
RUN npm ci --prefer-offline --no-audit --no-fund

# Copy frontend source
COPY frontend/ ./

# Build frontend with telemetry disabled for faster builds
RUN NEXT_TELEMETRY_DISABLED=1 npm run build

# ==================== MAIN RUNTIME ====================
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Install system dependencies with cleanup
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libpq5 \
    curl \
    supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/appuser/.local/bin:$PATH \
    NODE_ENV=production \
    PORT=80

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app
USER appuser

# ==================== BACKEND SETUP ====================
WORKDIR /app/backend

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies with user flag and no cache
RUN pip install --user --no-cache-dir --disable-pip-version-check -r requirements.txt

# Copy backend code
COPY --chown=appuser:appgroup backend/ .

# ==================== FRONTEND SETUP ====================
WORKDIR /app/frontend

# Install Next.js globally
RUN npm install -g next

# Copy built frontend from builder
COPY --from=frontend-builder --chown=appuser:appgroup /app/frontend/.next/standalone ./
COPY --from=frontend-builder --chown=appuser:appgroup /app/frontend/.next/static ./.next/static
COPY --from=frontend-builder --chown=appuser:appgroup /app/frontend/public ./public

# ==================== SUPERVISOR CONFIGURATION ====================
WORKDIR /app

# Create log directories with proper permissions
RUN mkdir -p /home/appuser/logs/supervisor

# Supervisor configuration
RUN echo '[supervisord]' > /home/appuser/supervisord.conf && \
    echo 'nodaemon=true' >> /home/appuser/supervisord.conf && \
    echo 'logfile=/home/appuser/logs/supervisor/supervisord.log' >> /home/appuser/supervisord.conf && \
    echo 'pidfile=/home/appuser/logs/supervisor/supervisord.pid' >> /home/appuser/supervisord.conf && \
    echo '' >> /home/appuser/supervisord.conf && \
    echo '[program:backend]' >> /home/appuser/supervisord.conf && \
    echo 'command=/home/appuser/.local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2' >> /home/appuser/supervisord.conf && \
    echo 'directory=/app/backend' >> /home/appuser/supervisord.conf && \
    echo 'autostart=true' >> /home/appuser/supervisord.conf && \
    echo 'autorestart=true' >> /home/appuser/supervisord.conf && \
    echo 'stderr_logfile=/home/appuser/logs/backend.err.log' >> /home/appuser/supervisord.conf && \
    echo 'stdout_logfile=/home/appuser/logs/backend.out.log' >> /home/appuser/supervisord.conf && \
    echo '' >> /home/appuser/supervisord.conf && \
    echo '[program:frontend]' >> /home/appuser/supervisord.conf && \
    echo 'command=node server.js' >> /home/appuser/supervisord.conf && \
    echo 'directory=/app/frontend' >> /home/appuser/supervisord.conf && \
    echo 'autostart=true' >> /home/appuser/supervisord.conf && \
    echo 'autorestart=true' >> /home/appuser/supervisord.conf && \
    echo 'environment=PORT="3000",NEXT_PUBLIC_API_URL="http://localhost:8000"' >> /home/appuser/supervisord.conf && \
    echo 'stderr_logfile=/home/appuser/logs/frontend.err.log' >> /home/appuser/supervisord.conf && \
    echo 'stdout_logfile=/home/appuser/logs/frontend.out.log' >> /home/appuser/supervisord.conf

# Health check with reduced timeout
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 80 8000 3000

# Start supervisor with config file
CMD ["/usr/bin/supervisord", "-c", "/home/appuser/supervisord.conf"]