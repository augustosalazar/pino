# Environment Variables in Expo Web Builds

## 🔑 Key Concept: Build-Time vs Runtime

**Important:** Expo web builds are **static files** (HTML, CSS, JS). Environment variables are **baked into the JavaScript bundle at BUILD time**, not loaded at runtime.

## 📋 How It Works

### Step 1: Create Environment File

Expo supports multiple environment files:

```
.env                 # Default (all environments)
.env.local          # Local overrides (gitignored)
.env.development    # Development mode
.env.production     # Production builds
```

### Step 2: Prefix Variables

**Critical:** Only variables prefixed with `EXPO_PUBLIC_` are accessible in your code.

**.env.production:**
```bash
# ❌ This won't work (no prefix)
API_URL=https://api.example.com

# ✅ This works (EXPO_PUBLIC_ prefix)
EXPO_PUBLIC_API_URL=https://api.example.com
EXPO_PUBLIC_ENABLE_ANALYTICS=true
```

### Step 3: Access in Code

**config.ts:**
```typescript
export const config = {
  api: {
    baseUrl: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000'
  },
  analytics: {
    enabled: process.env.EXPO_PUBLIC_ENABLE_ANALYTICS === 'true'
  }
};
```

### Step 4: Build Process

When you run `npx expo export:web`:

1. Expo reads `.env.production` (or `.env`)
2. Replaces all `process.env.EXPO_PUBLIC_*` with actual values
3. Bundles into JavaScript files
4. **Variables are now hardcoded in the JS**

**Before build (source code):**
```javascript
const apiUrl = process.env.EXPO_PUBLIC_API_URL;
```

**After build (bundled JS):**
```javascript
const apiUrl = "https://api.example.com";
```

## 🐳 Docker Integration

### Option 1: Build-Time Variables (Recommended for Production)

Use **build arguments** to pass values during image build:

**Dockerfile:**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Accept build arguments
ARG EXPO_PUBLIC_API_URL
ARG EXPO_PUBLIC_ENABLE_ANALYTICS

# Set as environment variables for the build
ENV EXPO_PUBLIC_API_URL=$EXPO_PUBLIC_API_URL
ENV EXPO_PUBLIC_ENABLE_ANALYTICS=$EXPO_PUBLIC_ENABLE_ANALYTICS

COPY package*.json ./
RUN npm ci --legacy-peer-deps

COPY . .

# Build with environment variables
RUN npx expo export:web

# ... rest of Dockerfile
```

**Build command:**
```bash
docker build \
  --build-arg EXPO_PUBLIC_API_URL=https://api.production.com \
  --build-arg EXPO_PUBLIC_ENABLE_ANALYTICS=true \
  -t pino-web .
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        EXPO_PUBLIC_API_URL: https://api.production.com
        EXPO_PUBLIC_ENABLE_ANALYTICS: "true"
    ports:
      - "3000:80"
```

### Option 2: .env Files (Simpler, Less Flexible)

**Project structure:**
```
r_pino/
├── .env.production      # Your production values
├── Dockerfile
└── ...
```

**.env.production:**
```bash
EXPO_PUBLIC_API_URL=https://api.production.com
EXPO_PUBLIC_ENABLE_ANALYTICS=true
```

**Dockerfile** (no changes needed - it copies all files):
```dockerfile
COPY . .
RUN npx expo export:web  # Automatically reads .env.production
```

**Build:**
```bash
docker build -t pino-web .
```

The values from `.env.production` are automatically used during the build.

## 🎯 Recommended Approach for Your Project

### Development
Use `.env.local` (gitignored):
```bash
EXPO_PUBLIC_API_URL=http://localhost:8000
```

### Production
Use **build arguments** for flexibility:

**Updated Dockerfile:**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Default values (can be overridden)
ARG EXPO_PUBLIC_API_URL=https://api.yourserver.com
ENV EXPO_PUBLIC_API_URL=$EXPO_PUBLIC_API_URL

COPY package*.json ./
RUN npm ci --legacy-peer-deps

COPY . .
RUN npx expo export:web

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Build for different environments:**

```bash
# Staging
docker build --build-arg EXPO_PUBLIC_API_URL=https://api-staging.com -t pino-web:staging .

# Production
docker build --build-arg EXPO_PUBLIC_API_URL=https://api-prod.com -t pino-web:prod .
```

## 🔐 Security Considerations

### ⚠️ Important Warnings

1. **Never put secrets in EXPO_PUBLIC_ variables**
   - They're visible in the browser's JavaScript
   - Anyone can inspect your bundled code
   - Use backend API calls for sensitive operations

2. **Safe to include:**
   - ✅ API endpoints (public URLs)
   - ✅ Feature flags
   - ✅ Analytics IDs (public)
   - ✅ Public configuration

3. **Never include:**
   - ❌ API keys/secrets
   - ❌ Database credentials
   - ❌ Private tokens
   - ❌ Encryption keys

### Example - What Users Can See

After build, users can open DevTools and search for your values:
```javascript
// In bundled JavaScript:
const API_URL = "https://api.example.com";  // ← Visible to everyone
```

## 📝 Complete Example

### 1. Create config.ts

**r_pino/config.ts:**
```typescript
export const config = {
  api: {
    baseUrl: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',
  },
  roble: {
    projectId: process.env.EXPO_PUBLIC_ROBLE_PROJECT_ID || 'default-project',
    baseUrl: process.env.EXPO_PUBLIC_ROBLE_BASE_URL || 'http://localhost:3001',
  },
  features: {
    analytics: process.env.EXPO_PUBLIC_ENABLE_ANALYTICS === 'true',
    debugMode: process.env.EXPO_PUBLIC_DEBUG_MODE === 'true',
  }
};
```

### 2. Create .env files

**.env.development:**
```bash
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_ROBLE_PROJECT_ID=dev-project
EXPO_PUBLIC_ROBLE_BASE_URL=http://localhost:3001
EXPO_PUBLIC_ENABLE_ANALYTICS=false
EXPO_PUBLIC_DEBUG_MODE=true
```

**.env.production:**
```bash
EXPO_PUBLIC_API_URL=https://api.yourserver.com
EXPO_PUBLIC_ROBLE_PROJECT_ID=prod-project
EXPO_PUBLIC_ROBLE_BASE_URL=https://roble.yourserver.com
EXPO_PUBLIC_ENABLE_ANALYTICS=true
EXPO_PUBLIC_DEBUG_MODE=false
```

### 3. Update Dockerfile

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Accept all public env variables
ARG EXPO_PUBLIC_API_URL
ARG EXPO_PUBLIC_ROBLE_PROJECT_ID
ARG EXPO_PUBLIC_ROBLE_BASE_URL
ARG EXPO_PUBLIC_ENABLE_ANALYTICS
ARG EXPO_PUBLIC_DEBUG_MODE

# Set as environment variables
ENV EXPO_PUBLIC_API_URL=$EXPO_PUBLIC_API_URL
ENV EXPO_PUBLIC_ROBLE_PROJECT_ID=$EXPO_PUBLIC_ROBLE_PROJECT_ID
ENV EXPO_PUBLIC_ROBLE_BASE_URL=$EXPO_PUBLIC_ROBLE_BASE_URL
ENV EXPO_PUBLIC_ENABLE_ANALYTICS=$EXPO_PUBLIC_ENABLE_ANALYTICS
ENV EXPO_PUBLIC_DEBUG_MODE=$EXPO_PUBLIC_DEBUG_MODE

COPY package*.json ./
RUN npm ci --legacy-peer-deps

COPY . .
RUN npx expo export:web

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 4. Build Commands

**Using .env.production (simple):**
```bash
docker build -t pino-web .
```

**Using build args (flexible):**
```bash
docker build \
  --build-arg EXPO_PUBLIC_API_URL=https://api.prod.com \
  --build-arg EXPO_PUBLIC_ROBLE_PROJECT_ID=prod-123 \
  --build-arg EXPO_PUBLIC_ROBLE_BASE_URL=https://roble.prod.com \
  --build-arg EXPO_PUBLIC_ENABLE_ANALYTICS=true \
  --build-arg EXPO_PUBLIC_DEBUG_MODE=false \
  -t pino-web:prod .
```

## 🔄 Runtime vs Build-Time Comparison

### Traditional Server App (Node.js)
```javascript
// Reads .env at RUNTIME
const apiUrl = process.env.API_URL;  
// Different value per deployment
```

### Expo Web App (Static)
```javascript
// Replaces at BUILD time
const apiUrl = "https://api.example.com";  
// Same value for all deployments of this build
```

## 🎯 Best Practices

1. **Use different builds for different environments**
   ```bash
   # Build staging
   docker build -f Dockerfile --build-arg EXPO_PUBLIC_API_URL=https://api-staging.com -t pino:staging .
   
   # Build production
   docker build -f Dockerfile --build-arg EXPO_PUBLIC_API_URL=https://api-prod.com -t pino:prod .
   ```

2. **Add defaults in code**
   ```typescript
   const apiUrl = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
   ```

3. **Document required variables**
   Create `.env.example`:
   ```bash
   # Required for build
   EXPO_PUBLIC_API_URL=
   EXPO_PUBLIC_ROBLE_PROJECT_ID=
   ```

4. **Use TypeScript for type safety**
   ```typescript
   declare global {
     namespace NodeJS {
       interface ProcessEnv {
         EXPO_PUBLIC_API_URL: string;
         EXPO_PUBLIC_ENABLE_ANALYTICS: string;
       }
     }
   }
   ```

## 📚 Summary

1. **Prefix:** Use `EXPO_PUBLIC_` for all client-side variables
2. **Build-Time:** Values are baked into JavaScript at build time
3. **Docker:** Pass via build args or .env files during build
4. **Security:** Never put secrets in EXPO_PUBLIC_ variables
5. **Multiple Builds:** Create separate builds for staging/production

The key takeaway: **It's not like a server where .env is read at runtime** - it's **compiled into your JavaScript bundle during the build**.
