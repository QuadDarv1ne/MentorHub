# API Documentation

## Overview

This directory contains API service modules for interacting with the MentorHub backend.

## Modules

### Authentication (`auth.ts`)

Handles user authentication operations:
- `login(email, password)` - User login
- `register(userData)` - User registration
- `getCurrentUser()` - Get current authenticated user
- `updateProfile(userData)` - Update user profile

### Mentors (`mentors.ts`)

Manages mentor-related operations:

```typescript
// Get list of mentors with filters
getMentors(filters?: MentorsFilters): Promise<MentorsResponse>

// Get single mentor by ID
getMentor(id: number): Promise<Mentor>

// Get mentor reviews
getMentorReviews(mentorId: number): Promise<Review[]>
```

**Filters:**
- `search` - Search by name or skills
- `specialization` - Filter by specialization
- `experience` - Filter by years of experience
- `priceRange` - Filter by hourly rate
- `page`, `limit` - Pagination

### Sessions (`sessions.ts`)

Manages mentoring sessions:

```typescript
// Get user's sessions
getMySessions(status?: 'upcoming' | 'past'): Promise<Session[]>

// Get session by ID
getSession(id: number): Promise<Session>

// Create new session
createSession(data: CreateSessionRequest): Promise<Session>

// Update session
updateSession(id: number, data: UpdateSessionRequest): Promise<Session>

// Cancel session
cancelSession(id: number): Promise<Session>

// Confirm session
confirmSession(id: number): Promise<Session>
```

**Session statuses:**
- `pending` - Awaiting confirmation
- `confirmed` - Confirmed and scheduled
- `completed` - Finished
- `cancelled` - Cancelled

### Dashboard (`dashboard.ts`)

Provides dashboard data:

```typescript
// Get complete dashboard data
getDashboardData(): Promise<DashboardData>

// Get user statistics
getUserStats(): Promise<DashboardStats>
```

**Dashboard includes:**
- Course statistics (total, in progress, completed)
- Session statistics (total, upcoming, completed)
- Recent activities
- Upcoming sessions

### Courses (`courses.ts`)

Manages course operations:
- Course listing with filters
- Course details
- Course enrollment
- Progress tracking

### Progress (`progress.ts`)

Tracks learning progress:
- Get course progress
- Update progress percentage
- Mark lessons as completed

## Usage Examples

### Fetching mentors with filters

```typescript
import { getMentors } from '@/lib/api/mentors';

const mentors = await getMentors({
  search: 'react',
  specialization: 'frontend',
  priceRange: '30-50',
  page: 1,
  limit: 10
});
```

### Creating a session

```typescript
import { createSession } from '@/lib/api/sessions';

const session = await createSession({
  mentor_id: 1,
  topic: 'React Hooks Deep Dive',
  scheduled_time: '2024-02-20T15:00:00',
  duration: 60,
  notes: 'Please prepare examples'
});
```

### Getting dashboard data

```typescript
import { getDashboardData } from '@/lib/api/dashboard';

const dashboard = await getDashboardData();
console.log(dashboard.stats.total_courses);
console.log(dashboard.upcoming_sessions);
```

## Error Handling

All API functions throw errors that should be caught:

```typescript
try {
  const mentors = await getMentors();
  // Handle success
} catch (error) {
  console.error('Failed to fetch mentors:', error);
  // Show error to user
}
```

## Authentication

Most endpoints require authentication. The access token is automatically retrieved from `localStorage`:

```typescript
const token = localStorage.getItem('access_token');
```

If not authenticated, functions will throw an error: `"Authentication required"`

## Environment Variables

Configure the API base URL:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

Default: `http://localhost:8000/api/v1`
