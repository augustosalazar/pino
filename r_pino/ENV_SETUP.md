# R_PINE Environment Variables Setup

## Overview
Sensitive configuration values (Roble Project ID, API URLs) have been moved to environment variables for better security.

## Quick Setup

### Step 1: Create .env File

Create a file named `.env` in the `r_pino` root directory:

**Option A: PowerShell (Windows)**
```powershell
cd c:\desarrollo\pino\r_pino

@"
EXPO_PUBLIC_ROBLE_PROJECT_ID=tracking_7d2ad2db74
EXPO_PUBLIC_ROBLE_BASE_URL=https://roble-api.openlab.uninorte.edu.co
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api
"@ | Out-File -FilePath .env -Encoding UTF8
```

**Option B: Copy from Sample**
```bash
cd r_pino
cp .env.sample .env
```
Then edit `.env` and replace placeholder values.

**Option C: Manual Creation**
Create `.env` file with this content:
```env
EXPO_PUBLIC_ROBLE_PROJECT_ID=tracking_7d2ad2db74
EXPO_PUBLIC_ROBLE_BASE_URL=https://roble-api.openlab.uninorte.edu.co
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### Step 2: Adjust API URL for Your Platform

Edit the `EXPO_PUBLIC_API_BASE_URL` based on where you're testing:

```env
# Web / iOS Simulator
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api

# Android Emulator
EXPO_PUBLIC_API_BASE_URL=http://10.0.2.2:8000/api

# Physical Device (replace with your computer's IP)
EXPO_PUBLIC_API_BASE_URL=http://192.168.1.100:8000/api
```

### Step 3: Restart Development Server

**Important:** After creating/modifying `.env`, restart the dev server:

```bash
# Stop current server (Ctrl+C)
# Then restart:
npm start
# or
npm run web
```

## How It Works

### Environment Variable Prefix
Expo requires `EXPO_PUBLIC_` prefix for client-accessible variables:
- ✅ `EXPO_PUBLIC_API_BASE_URL` - Accessible in app
- ❌ `API_BASE_URL` - Not accessible (would be undefined)

### Configuration System
All environment variables are centralized in `config/index.ts`:

```typescript
import { config } from './config';

// Access configuration
console.log(config.roble.projectId);  // 'tracking_7d2ad2db74'
console.log(config.api.baseUrl);      // 'http://localhost:8000/api'
```

### Fallback Values
If `.env` is missing, the app uses default values:
```typescript
robleProjectId: process.env.EXPO_PUBLIC_ROBLE_PROJECT_ID || 'tracking_7d2ad2db74'
```

## Files Modified

### New Files
- ✅ `config/index.ts` - Centralized configuration
- ✅ `.env.sample` - Template for environment variables
- ✅ `.gitignore` - Updated to ignore `.env`

### Updated Files
- ✅ `services/auth.ts` - Uses `config.roble.*`
- ✅ `services/api.ts` - Uses `config.api.baseUrl`

## Before vs After

### Before (auth.ts):
```typescript
const ROBLE_PROJECT_ID = 'tracking_7d2ad2db74';
const ROBLE_BASE_URL = 'https://roble-api.openlab.uninorte.edu.co';
```

### After (auth.ts):
```typescript
import { config } from '../config';
// Uses config.roble.projectId and config.roble.baseUrl
```

### Before (api.ts):
```typescript
const API_BASE_URL = 'http://localhost:8000/api';
```

### After (api.ts):
```typescript
import { config } from '../config';
// Uses config.api.baseUrl
```

## Debugging Configuration

To see what configuration is loaded:

```typescript
import { logConfig } from './config';

// In your component or anywhere
logConfig();
```

This will print:
```
🔧 App Configuration:
  Roble Project ID: tracking_7d2ad2db74
  Roble Base URL: https://roble-api.openlab.uninorte.edu.co
  API Base URL: http://localhost:8000/api
```

## Security Benefits

### ✅ DO:
- Keep `.env` local only
- Never commit `.env` to Git
- Use different values per environment
- Share `.env.sample` instead

### ❌ DON'T:
- Commit `.env` to version control
- Share `.env` file publicly
- Hardcode credentials in source code
- Use production credentials in development

## Troubleshooting

### Issue: Environment variables are undefined
**Solution:** 
1. Check file is named `.env` (with dot)
2. Ensure variables have `EXPO_PUBLIC_` prefix
3. Restart dev server completely
4. Check `.env` is in project root (not in subdirectory)

### Issue: Changes not reflecting
**Solution:**
```bash
# Clear cache and restart
npx expo start -c
```

### Issue: Cannot find module '../config'
**Solution:**
Ensure `config/index.ts` exists in your project

## Different Environments

### Development
```env
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### Staging
```env
EXPO_PUBLIC_API_BASE_URL=https://staging-api.example.com/api
```

### Production
```env
EXPO_PUBLIC_API_BASE_URL=https://api.example.com/api
```

## Notes

- `.env` is protected by `.gitignore` ✅
- `.env.sample` is safe to commit ✅
- Config has sensible defaults ✅
- All services centralized through `config/` ✅

---

**Status**: ✅ Environment variables configured and secured
