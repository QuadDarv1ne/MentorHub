# Components Documentation

## UI Components

### Alert

Displays contextual feedback messages.

**Props:**
- `type`: 'success' | 'error' | 'warning' | 'info'
- `title?`: Optional heading
- `message`: Main message text
- `onClose?`: Callback for dismissal
- `dismissible?`: Show close button (default: true)

**Usage:**
```tsx
<Alert 
  type="success"
  title="Success!"
  message="Profile updated successfully"
  onClose={() => setAlert(null)}
/>
```

### LoadingSpinner

Shows loading state with optional text.

**Props:**
- `size?`: 'sm' | 'md' | 'lg' (default: 'md')
- `fullScreen?`: Cover entire screen (default: false)
- `text?`: Optional loading text

**Usage:**
```tsx
<LoadingSpinner size="lg" text="Loading mentors..." />

{/* Full screen loading */}
<LoadingSpinner fullScreen text="Please wait..." />
```

### ErrorBoundary

Catches React errors and displays fallback UI.

**Props:**
- `children`: React nodes to wrap
- `fallback?`: Custom error UI (optional)

**Usage:**
```tsx
<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>

{/* With custom fallback */}
<ErrorBoundary fallback={<CustomErrorPage />}>
  <YourComponent />
</ErrorBoundary>
```

## Feature Components

### Header

Main navigation header with authentication state.

**Features:**
- Logo and branding
- Navigation links
- User menu (when authenticated)
- Login/Register buttons (when not authenticated)

### Footer

Site footer with links and information.

**Sections:**
- Platform information
- Quick links
- Support links
- Social media

### Hero

Landing page hero section.

**Features:**
- Main headline and description
- Call-to-action buttons
- Background gradient

### Features

Highlights platform features with icons.

**Features displayed:**
- Expert mentors
- Flexible scheduling
- Interactive learning
- Progress tracking

### MentorsPreview

Shows featured mentors on homepage.

**Features:**
- Mentor cards with avatars
- Ratings and specializations
- "View all mentors" link

### SimilarCourses

Displays recommended courses based on user data.

**Features:**
- Course cards with images
- Loading skeletons
- Hover effects
- Stepik integration

### ProgressTracker

Interactive course progress component.

**Features:**
- Visual progress bar
- Adjustable slider
- Save/Cancel/Complete buttons
- Authentication checks

**Usage:**
```tsx
<ProgressTracker courseId={123} />
```

### StepikCourseCard

Card component for Stepik courses.

**Props:**
- `id`: Course ID
- `title`: Course title
- `description`: Course description
- `stepikUrl`: Link to Stepik
- `price`: Course price
- `studentsCount`: Number of students
- `rating`: Course rating
- `category`: Course category

## Best Practices

### Loading States

Always show loading indicators:

```tsx
{loading ? (
  <LoadingSpinner />
) : (
  <YourContent />
)}
```

### Error Handling

Wrap error-prone components:

```tsx
<ErrorBoundary>
  <DataFetchingComponent />
</ErrorBoundary>
```

### Alerts

Use appropriate alert types:

```tsx
// Success
<Alert type="success" message="Changes saved!" />

// Error
<Alert type="error" message="Failed to save" />

// Warning
<Alert type="warning" message="Unsaved changes" />

// Info
<Alert type="info" message="New features available" />
```

### Accessibility

All components include:
- Proper ARIA labels
- Keyboard navigation
- Screen reader support
- Semantic HTML

## Styling

Components use Tailwind CSS utility classes:

```tsx
className="bg-white shadow-md rounded-lg p-6"
```

Custom styles in `globals.css` for progress bars and animations.
