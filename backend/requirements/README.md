# MentorHub Backend Requirements

This directory contains multiple requirements files for different environments and use cases.

## File Structure

```
requirements.txt          # Main file - includes all production dependencies
requirements-base.txt     # Core dependencies for all environments
requirements-prod.txt     # Production dependencies (includes base)
requirements-dev.txt      # Development dependencies (includes base + testing tools)
requirements-cloud.txt    # Optional cloud platform dependencies
```

## Installation

### Production Deployment (any platform)
```bash
pip install -r requirements.txt
```

### Development
```bash
pip install -r requirements-dev.txt
```

### Minimal Installation
```bash
pip install -r requirements-base.txt
```

## Platform-Specific Notes

### Render
- Automatically sets `DATABASE_URL` and `PORT`
- Uses `requirements.txt` by default
- No additional configuration needed

### Railway
- Automatically sets `DATABASE_URL`, `PORT`, `RAILWAY_*` variables
- Uses `requirements.txt` by default
- No additional configuration needed

### Fly.io
- Uses `FLY_*` environment variables
- No additional packages needed

### Amvera
- Uses custom volume mounts and environment variables
- No additional packages needed

### Google Cloud Run
- For Cloud SQL connections, uncomment in `requirements-cloud.txt`:
  ```
  cloud-sql-python-connector[pg8000]>=1.0.0
  ```

### AWS (ECS/App Runner/Lambda)
- `boto3` is already included
- For Secrets Manager integration, uncomment in `requirements-cloud.txt`

### Heroku
- Sets `DATABASE_URL` automatically
- No additional packages needed

### DigitalOcean App Platform
- Sets `DATABASE_URL` automatically
- No additional packages needed

## Version Policy

- **Minimum versions** (`>=`) are used for compatibility
- **Maximum versions** (`<`) are used only when necessary (e.g., `urllib3>=2.0.0,<3.0.0`)
- No strict version pinning (`==`) except for security-critical packages

## Optional Dependencies

Some features require optional packages. Uncomment them in `requirements-prod.txt` or `requirements-cloud.txt` as needed:

- **Agora Video**: `agora-token>=2.0.0`
- **SBP Payments (Russia)**: `sbp-qr>=0.2.0`
- **Cloud SQL Auth Proxy**: `cloud-sql-python-connector[pg8000]>=1.0.0`

## Troubleshooting

### psycopg2 installation fails on Windows
Use `psycopg2-binary` (already included in `requirements-base.txt`)

### uvloop/httptools on Windows
These are Unix-only packages. They are conditionally excluded using `sys_platform != 'win32'`

### Missing package on specific platform
Check `requirements-cloud.txt` for platform-specific dependencies
