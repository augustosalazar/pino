# 🔐 Environment Variables - Quick Reference

## The Process in 3 Steps

### 1️⃣ Define Variables

Create `.env.production`:
```bash
EXPO_PUBLIC_API_URL=https://api.yourserver.com
EXPO_PUBLIC_ROBLE_PROJECT_ID=prod-123
```

### 2️⃣ Build Docker Image

**Option A: Using .env file (automatic)**
```bash
# Expo reads .env.production automatically
docker-compose up --build
```

**Option B: Using build arguments (explicit)**
```bash
docker build \
  --build-arg EXPO_PUBLIC_API_URL=https://api.yourserver.com \
  --build-arg EXPO_PUBLIC_ROBLE_PROJECT_ID=prod-123 \
  -t pino-web .
```

### 3️⃣ What Happens

```
Before Build (your code):
┌─────────────────────────────────────┐
│ const url =                         │
│   process.env.EXPO_PUBLIC_API_URL   │
└─────────────────────────────────────┘

        ↓ Docker build

After Build (bundled JS):
┌─────────────────────────────────────┐
│ const url =                         │
│   "https://api.yourserver.com"      │
└─────────────────────────────────────┘
```

## 🎯 Visual Flow

```
┌──────────────────┐
│ .env.production  │
│ or               │
│ --build-arg      │
└────────┬─────────┘
         │
         ↓
┌────────────────────────────────┐
│ Docker Build Stage             │
│                                │
│ 1. npm ci (install deps)       │
│ 2. Copy source code            │
│ 3. npx expo export:web         │ ← Reads EXPO_PUBLIC_* vars
│    └→ Replaces in code         │
│    └→ Bundles JavaScript       │
└────────┬───────────────────────┘
         │
         ↓
┌────────────────────────────────┐
│ Static Files (dist/)           │
│                                │
│ • index.html                   │
│ • bundle.js  ← vars hardcoded  │
│ • assets/                      │
└────────┬───────────────────────┘
         │
         ↓
┌────────────────────────────────┐
│ Nginx Container                │
│                                │
│ Serves static files            │
│ No runtime env loading         │
└────────────────────────────────┘
```

## 🔧 Common Scenarios

### Development
```bash
# .env.local (gitignored)
EXPO_PUBLIC_API_URL=http://localhost:8000
```

### Staging
```bash
docker build \
  --build-arg EXPO_PUBLIC_API_URL=https://api-staging.com \
  -t pino-web:staging .
```

### Production
```bash
docker build \
  --build-arg EXPO_PUBLIC_API_URL=https://api-prod.com \
  -t pino-web:prod .
```

## ⚠️ Key Differences vs Server Apps

| Server App (Node.js) | Expo Web Build |
|----------------------|----------------|
| Reads .env at RUNTIME | Reads .env at BUILD time |
| Can change without rebuild | Requires rebuild to change |
| .env file needed on server | .env file NOT needed in container |
| process.env works normally | process.env replaced with values |

## 📝 Checklist

- [ ] Prefix all variables with `EXPO_PUBLIC_`
- [ ] Create `.env.example` documenting variables
- [ ] Add `.env.local` to `.gitignore`
- [ ] Never commit real values to git
- [ ] Never put secrets in EXPO_PUBLIC_ variables
- [ ] Build separate images for staging/production
- [ ] Test that values are correct in final bundle

## 🔍 How to Verify

After building, check if variables were baked in:

```bash
# Run container
docker run -p 3000:80 pino-web

# Open browser DevTools → Sources
# Search for your API URL in bundle.js
# You'll see: const url = "https://api.yourserver.com"
```

## 💡 Pro Tips

1. **Default values in code:**
   ```typescript
   const apiUrl = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
   ```

2. **Different builds for environments:**
   ```bash
   docker build --build-arg EXPO_PUBLIC_API_URL=... -t pino:staging .
   docker build --build-arg EXPO_PUBLIC_API_URL=... -t pino:prod .
   ```

3. **Use build args for CI/CD:**
   ```yaml
   # GitHub Actions
   - run: |
       docker build \
         --build-arg EXPO_PUBLIC_API_URL=${{ secrets.API_URL }} \
         -t my-app .
   ```

## 📚 Full Documentation

See `ENV_VARIABLES_GUIDE.md` for complete details.
