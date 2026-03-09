#!/bin/bash
# Wrapper script for Next.js standalone server
# Ensures PORT is properly set

# Use PORT from environment or default to 3000
PORT=${PORT:-3000}

echo "🚀 Starting Next.js on port $PORT..."
export PORT=$PORT
export HOSTNAME="0.0.0.0"

# Start the standalone server
exec node server.js
