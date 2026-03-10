# MentorHub Architecture

## System Overview

```mermaid
graph TB
    subgraph Client Layer
        Web[Web Browser]
        Mobile[Mobile App]
        Admin[Admin Dashboard]
    end

    subgraph CDN
        Cloudflare[Cloudflare CDN]
    end

    subgraph Load Balancer
        Nginx[Nginx Reverse Proxy]
    end

    subgraph Application Layer
        Frontend[Next.js Frontend<br/>Port 3000]
        Backend[FastAPI Backend<br/>Port 8000]
    end

    subgraph Data Layer
        PostgreSQL[(PostgreSQL<br/>Database)]
        Redis[(Redis<br/>Cache)]
        S3[AWS S3<br/>File Storage]
    end

    subgraph External Services
        Stripe[Stripe Payments]
        Agora[Agora Video]
        SMTP[Email Service]
        Sentry[Sentry Monitoring]
    end

    Web --> Cloudflare
    Mobile --> Cloudflare
    Admin --> Cloudflare
    Cloudflare --> Nginx
    Nginx --> Frontend
    Nginx --> Backend
    Frontend --> Backend
    Backend --> PostgreSQL
    Backend --> Redis
    Backend --> S3
    Backend --> Stripe
    Backend --> Agora
    Backend --> SMTP
    Backend --> Sentry
```

---

## Application Flow

### User Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database
    participant R as Redis

    U->>F: Enter credentials
    F->>B: POST /api/v1/auth/login
    B->>DB: Validate user
    DB-->>B: User data
    B->>B: Generate JWT tokens
    B->>R: Store session (optional)
    B-->>F: Return tokens
    F->>F: Store tokens
    F->>U: Redirect to dashboard
    U->>F: Access protected route
    F->>B: Request with JWT
    B->>B: Verify JWT
    B->>R: Check session (optional)
    R-->>B: Session valid
    B-->>F: Return data
    F->>U: Display data
```

---

## Database Schema

```mermaid
erDiagram
    USER ||--o{ MENTOR : "can be"
    USER ||--o{ SESSION : "books"
    USER ||--o{ MESSAGE : "sends"
    USER ||--o{ PAYMENT : "makes"
    USER ||--o{ PROGRESS : "has"
    USER ||--o{ REVIEW : "writes"
    USER ||--o{ ACHIEVEMENT : "earns"
    USER ||--o{ NOTIFICATION : "receives"

    MENTOR ||--o{ SESSION : "conducts"
    MENTOR ||--o{ REVIEW : "receives"
    MENTOR ||--o{ COURSE : "creates"

    COURSE ||--o{ PROGRESS : "tracked in"
    COURSE ||--o{ REVIEW : "has"
    COURSE ||--o{ ENROLLMENT : "has"

    SESSION ||--o{ MESSAGE : "contains"
    SESSION ||--o{ PAYMENT : "generates"

    USER {
        int id PK
        string email
        string password_hash
        string full_name
        string role
        datetime created_at
    }

    MENTOR {
        int id PK
        int user_id FK
        string specialization
        float price_per_hour
        string availability
    }

    COURSE {
        int id PK
        int mentor_id FK
        string title
        string description
        string level
        float price
    }

    SESSION {
        int id PK
        int user_id FK
        int mentor_id FK
        datetime scheduled_at
        string status
    }

    PAYMENT {
        int id PK
        int user_id FK
        int session_id FK
        float amount
        string status
        string provider
    }
```

---

## Component Architecture

### Frontend Architecture

```mermaid
graph TB
    subgraph Next.js App
        Pages[Pages/Routes]
        Components[Components]
        Store[Redux Store]
        API[API Client]
    end

    subgraph Key Components
        Auth[Auth Components]
        Dashboard[Dashboard]
        Booking[Booking System]
        Chat[Chat Widget]
        Courses[Course Player]
    end

    subgraph External
        Backend[Backend API]
        WebSocket[WebSocket]
    end

    Pages --> Components
    Pages --> Store
    Components --> Store
    Store --> API
    API --> Backend
    Components --> WebSocket
    Auth --> Booking
    Dashboard --> Courses
    Chat --> WebSocket
```

### Backend Architecture

```mermaid
graph TB
    subgraph API Layer
        Routes[API Routes]
        Middleware[Middleware]
        Auth[Authentication]
    end

    subgraph Business Logic
        Services[Services]
        Validators[Validators]
        Tasks[Celery Tasks]
    end

    subgraph Data Access
        Models[SQLAlchemy Models]
        Repositories[Repositories]
        Cache[Cache Layer]
    end

    subgraph External
        DB[Database]
        Redis[Redis]
        Queue[Celery Queue]
    end

    Routes --> Middleware
    Middleware --> Auth
    Auth --> Services
    Services --> Validators
    Services --> Models
    Services --> Cache
    Models --> DB
    Cache --> Redis
    Tasks --> Queue
    Tasks --> Services
```

---

## Deployment Architecture

### Render Cloud Platform

```mermaid
graph TB
    subgraph Render
        WebService[Web Service<br/>Backend + Frontend]
        PostgreSQL[(PostgreSQL<br/>Managed DB)]
        Redis[(Redis<br/>Managed Cache)]
    end

    subgraph External
        Users[Users]
        GitHub[GitHub Repository]
        Monitor[Monitoring]
    end

    Users --> WebService
    GitHub --> WebService
    WebService --> PostgreSQL
    WebService --> Redis
    WebService --> Monitor
```

### Docker Compose (Local/Production)

```mermaid
graph TB
    subgraph Docker Containers
        Nginx[Nginx<br/>:80/:443]
        Frontend[Frontend<br/>:3000]
        Backend[Backend<br/>:8000]
        DB[(PostgreSQL<br/>:5432)]
        Cache[(Redis<br/>:6379]
        Worker[Celery Worker]
    end

    Nginx --> Frontend
    Nginx --> Backend
    Frontend --> Backend
    Backend --> DB
    Backend --> Cache
    Worker --> Backend
    Worker --> DB
    Worker --> Cache
```

---

## Security Architecture

```mermaid
graph TB
    subgraph Security Layers
        HTTPS[HTTPS/TLS]
        CORS[CORS Policy]
        RateLimit[Rate Limiting]
        Auth[JWT Authentication]
        Input[Input Validation]
    end

    subgraph Data Protection
        Hash[Password Hashing<br/>bcrypt]
        Encrypt[Data Encryption]
        Sanitize[SQL Injection<br/>Protection]
    end

    subgraph Monitoring
        Sentry[Error Tracking]
        Logs[Audit Logs]
        Alerts[Security Alerts]
    end

    HTTPS --> CORS
    CORS --> RateLimit
    RateLimit --> Auth
    Auth --> Input
    Input --> Hash
    Hash --> Encrypt
    Encrypt --> Sanitize
    Sanitize --> Sentry
    Sentry --> Logs
    Logs --> Alerts
```

---

## Data Flow

### Booking Session Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database
    participant P as Payment
    participant N as Notification

    U->>F: Select mentor & time
    F->>B: POST /api/v1/sessions
    B->>DB: Check availability
    DB-->>B: Available
    B->>DB: Create session
    B->>P: Process payment
    P-->>B: Payment success
    B->>N: Send confirmation
    N->>U: Email notification
    N->>M: Notify mentor
    B-->>F: Session created
    F->>U: Show confirmation
```

---

## Monitoring & Observability

```mermaid
graph TB
    subgraph Application
        App[Backend + Frontend]
    end

    subgraph Metrics
        Prometheus[Prometheus<br/>Metrics]
        Grafana[Grafana<br/>Dashboards]
    end

    subgraph Logging
        ELK[ELK Stack<br/>Logs]
    end

    subgraph Tracing
        Sentry[Sentry<br/>Errors]
    end

    subgraph Alerts
        PagerDuty[PagerDuty<br/>Alerts]
    end

    App --> Prometheus
    App --> ELK
    App --> Sentry
    Prometheus --> Grafana
    Sentry --> PagerDuty
    Grafana --> PagerDuty
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 | React framework |
| **State** | Redux Toolkit | State management |
| **Data Fetching** | TanStack Query | API caching |
| **Backend** | FastAPI | Python API framework |
| **Database** | PostgreSQL 16 | Primary database |
| **Cache** | Redis 7 | Caching & sessions |
| **Queue** | Celery | Background tasks |
| **Auth** | JWT | Token-based auth |
| **Payments** | Stripe | Payment processing |
| **Video** | Agora | Video calls |
| **Monitoring** | Sentry + Prometheus | Error tracking & metrics |
| **Deployment** | Render | Cloud platform |

---

## Scalability Considerations

### Current Architecture
- Single instance deployment
- Vertical scaling (Render plans)
- Database connection pooling
- Redis caching

### Future Scaling
- Horizontal scaling (multiple instances)
- Load balancing
- Database read replicas
- CDN for static assets
- Microservices architecture
- Kubernetes orchestration

---

## Disaster Recovery

```mermaid
graph TB
    subgraph Backup Strategy
        Daily[Daily Backups<br/>7 days retention]
        Weekly[Weekly Backups<br/>4 weeks retention]
        Monthly[Monthly Backups<br/>6 months retention]
    end

    subgraph Recovery
        RPO[RPO: 24 hours<br/>Recovery Point Objective]
        RTO[RTO: 4 hours<br/>Recovery Time Objective]
    end

    Daily --> RPO
    Weekly --> RPO
    Monthly --> RPO
    RPO --> RTO
```

---

## API Gateway Pattern

```mermaid
graph TB
    subgraph Gateway
        Nginx[Nginx Gateway]
        RateLimit[Rate Limiting]
        Auth[Auth Check]
        Routing[Request Routing]
    end

    subgraph Services
        AuthSvc[Auth Service]
        UserSvc[User Service]
        CourseSvc[Course Service]
        PaymentSvc[Payment Service]
    end

    Client --> Nginx
    Nginx --> RateLimit
    RateLimit --> Auth
    Auth --> Routing
    Routing --> AuthSvc
    Routing --> UserSvc
    Routing --> CourseSvc
    Routing --> PaymentSvc
```

---

**Last Updated:** 2026-03-10
**Version:** 1.0.0
