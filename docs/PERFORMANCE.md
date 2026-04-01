# Performance Optimization Guide

## Overview

This document describes performance optimizations implemented in MentorHub and best practices for maintaining high performance.

---

## Database Optimization

### 1. PgBouncer Connection Pooling

**Configuration:** `docker-compose.prod.yml`

```yaml
pgbouncer:
  environment:
    POOL_MODE: transaction
    DEFAULT_POOL_SIZE: 25
    MAX_DB_CONNECTIONS: 100
```

**Benefits:**
- Reduces connection overhead by 70-80%
- Handles 1000+ concurrent clients with 100 DB connections
- Transaction-level pooling for optimal performance

**Monitoring:**
```bash
# Check PgBouncer stats
docker-compose exec pgbouncer psql -p 6432 -U pgbouncer pgbouncer -c "SHOW STATS;"
```

### 2. PostgreSQL Tuning

**Key Settings:**
```
shared_buffers = 512MB          # 25% of RAM
effective_cache_size = 2GB      # 50-75% of RAM
work_mem = 32MB                 # Per operation
maintenance_work_mem = 256MB    # For VACUUM, CREATE INDEX
max_connections = 200           # With PgBouncer
```

**Query Optimization:**
- Use indexes on frequently queried columns
- Avoid N+1 queries with eager loading
- Use `EXPLAIN ANALYZE` for slow queries

### 3. Database Indexes

**Existing Indexes:**
```sql
-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Sessions
CREATE INDEX idx_sessions_mentor_id ON sessions(mentor_id);
CREATE INDEX idx_sessions_student_id ON sessions(student_id);
CREATE INDEX idx_sessions_status ON sessions(status);

-- Composite indexes for common queries
CREATE INDEX idx_sessions_mentor_status ON sessions(mentor_id, status);
```

---

## Caching Strategy

### 1. Redis Configuration

**Production Settings:** `redis.conf`

```conf
maxmemory 512mb
maxmemory-policy allkeys-lru
appendonly yes
save 900 1
save 300 10
save 60 10000
```

**Cache Layers:**

1. **Application Cache** (Redis)
   - User sessions: 7 days TTL
   - API responses: 5 minutes TTL
   - Static data: 1 hour TTL

2. **HTTP Cache** (Nginx)
   - Static assets: 1 year
   - API responses: 5 minutes
   - No cache for auth endpoints

### 2. Cache Invalidation

**Strategies:**
- Time-based expiration (TTL)
- Event-based invalidation (on data update)
- Cache warming for frequently accessed data

**Example:**
```python
# Cache user profile
@cache.memoize(timeout=300)  # 5 minutes
def get_user_profile(user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Invalidate on update
def update_user_profile(user_id: int, data: dict):
    user = update_user(user_id, data)
    cache.delete(f"user_profile_{user_id}")
    return user
```

---

## API Optimization

### 1. Response Compression

**Nginx Gzip:**
```nginx
gzip on;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript;
```

**Benefits:**
- 60-80% size reduction for text responses
- Faster page loads
- Reduced bandwidth costs

### 2. Rate Limiting

**Configuration:**
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;
```

**Endpoints:**
- API: 10 requests/second
- Auth: 5 requests/minute
- WebSocket: No limit

### 3. Pagination

**Best Practices:**
```python
# Use cursor-based pagination for large datasets
@router.get("/mentors")
async def get_mentors(
    cursor: Optional[int] = None,
    limit: int = Query(20, le=100)
):
    query = db.query(Mentor)
    if cursor:
        query = query.filter(Mentor.id > cursor)
    return query.limit(limit).all()
```

---

## Frontend Optimization

### 1. Code Splitting

**Next.js Dynamic Imports:**
```typescript
// Lazy load heavy components
const VideoCall = dynamic(() => import('@/components/VideoCall'), {
  loading: () => <Spinner />,
  ssr: false
});
```

### 2. Image Optimization

**Next.js Image Component:**
```tsx
import Image from 'next/image';

<Image
  src="/mentor-avatar.jpg"
  width={200}
  height={200}
  alt="Mentor"
  loading="lazy"
  placeholder="blur"
/>
```

### 3. Bundle Size

**Current Metrics:**
- First Load JS: ~150KB (gzipped)
- Total Bundle: ~500KB (gzipped)

**Optimization:**
```bash
# Analyze bundle
npm run analyze

# Check bundle size
npm run build
```

---

## Load Testing

### 1. k6 Load Tests

**Run Tests:**
```bash
# Local testing
k6 run k6-load-test.js

# Production testing (be careful!)
k6 run k6-load-test.js --env BASE_URL=https://api.mentorhub.com
```

**Performance Targets:**
- p95 response time: < 500ms
- p99 response time: < 1000ms
- Error rate: < 1%
- Throughput: 100+ RPS

### 2. Lighthouse Scores

**Target Scores:**
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 90
- SEO: > 90

**Run Audit:**
```bash
cd frontend
npm run lighthouse
```

---

## Monitoring

### 1. Prometheus Metrics

**Key Metrics:**
- `http_request_duration_seconds` - Request latency
- `http_requests_total` - Request count
- `db_connections_active` - Active DB connections
- `redis_commands_total` - Redis operations

**Access:**
```
http://localhost:9090
```

### 2. Grafana Dashboards

**Dashboards:**
- Application Performance
- Database Performance
- Redis Performance
- System Resources

**Access:**
```
http://localhost:3001
Username: admin
Password: admin
```

---

## Performance Checklist

### Backend
- [ ] Use PgBouncer for connection pooling
- [ ] Enable Redis caching for frequently accessed data
- [ ] Add database indexes for common queries
- [ ] Use async/await for I/O operations
- [ ] Implement pagination for large datasets
- [ ] Enable response compression
- [ ] Set up rate limiting

### Frontend
- [ ] Use Next.js Image component
- [ ] Implement code splitting
- [ ] Enable lazy loading for heavy components
- [ ] Optimize bundle size (< 200KB first load)
- [ ] Use CDN for static assets
- [ ] Implement service worker for offline support

### Infrastructure
- [ ] Use Nginx for reverse proxy and caching
- [ ] Configure proper cache headers
- [ ] Enable HTTP/2
- [ ] Use CDN (Cloudflare/CloudFront)
- [ ] Set up monitoring and alerting

---

## Troubleshooting

### Slow Database Queries

1. **Identify slow queries:**
```sql
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

2. **Analyze query plan:**
```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

3. **Add missing indexes:**
```sql
CREATE INDEX idx_users_email ON users(email);
```

### High Memory Usage

1. **Check Redis memory:**
```bash
docker-compose exec redis redis-cli INFO memory
```

2. **Check PostgreSQL connections:**
```bash
docker-compose exec postgres psql -U mentorhub_user -c "SELECT count(*) FROM pg_stat_activity;"
```

3. **Monitor with Grafana:**
```
http://localhost:3001
```

### Slow API Responses

1. **Check Nginx cache:**
```bash
docker-compose exec nginx cat /var/log/nginx/access.log | grep "X-Cache-Status"
```

2. **Profile Python code:**
```python
import cProfile
cProfile.run('your_function()')
```

3. **Use APM tools:**
- Sentry for error tracking
- New Relic/Datadog for APM

---

## Best Practices

1. **Always use connection pooling** (PgBouncer)
2. **Cache aggressively** but invalidate properly
3. **Monitor everything** with Prometheus + Grafana
4. **Load test regularly** before deployments
5. **Optimize database queries** with indexes
6. **Use CDN** for static assets
7. **Enable compression** for all text responses
8. **Implement rate limiting** to prevent abuse

---

**Last Updated:** 2025-01-16
