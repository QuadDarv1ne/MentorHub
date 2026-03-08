# frontend/Dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
# Install dependencies with frozen lockfile for reproducible builds
#RUN npm ci --prefer-offline --no-audit --no-fund
RUN npm install --legacy-peer-deps
COPY . .
# Build with telemetry disabled for faster builds
RUN NEXT_TELEMETRY_DISABLED=1 npm run build

FROM node:18-alpine
WORKDIR /app
# Copy built assets from builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/public ./public
# Install only production dependencies
RUN npm ci --production --prefer-offline --no-audit --no-fund
EXPOSE 3000
CMD ["npm", "start"]