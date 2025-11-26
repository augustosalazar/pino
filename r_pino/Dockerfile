# Multi-stage build for Expo Web App
# Stage 1: Build the application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Accept build arguments for public environment variables
# These will be baked into the JavaScript bundle at build time
ARG EXPO_PUBLIC_API_URL
ARG EXPO_PUBLIC_ROBLE_PROJECT_ID
ARG EXPO_PUBLIC_ROBLE_BASE_URL

# Set as environment variables so Expo can read them during build
ENV EXPO_PUBLIC_API_URL=$EXPO_PUBLIC_API_URL
ENV EXPO_PUBLIC_ROBLE_PROJECT_ID=$EXPO_PUBLIC_ROBLE_PROJECT_ID
ENV EXPO_PUBLIC_ROBLE_BASE_URL=$EXPO_PUBLIC_ROBLE_BASE_URL

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy source code
COPY . .

# Build for web production
# Environment variables will be baked into the bundle
RUN npx expo export --platform web

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
