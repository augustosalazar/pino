# Environment Setup Instructions

## Creating the .env File

The `.env` file is blocked by `.gitignore` (for security), so you need to create it manually.

### Option 1: Copy from Sample
```bash
cd pineServer
cp .env.sample .env
```

Then edit `.env` and replace the placeholder values with your actual credentials.

### Option 2: Create Manually

Create a file named `.env` in the `pineServer` directory with this **exact** content:

```env
# Pine Server Environment Variables
# WARNING: This file contains sensitive information. Do not commit to version control!

# Roble API Configuration
ROBLE_PROJECT_ID=tracking_7d2ad2db74
ROBLE_BASE_URL=https://roble-api.openlab.uninorte.edu.co

# Admin Credentials
ADMIN_EMAIL=admin@pine.com
ADMIN_PASSWORD=ThePassword!1
```

### Option 3: Using PowerShell (Windows)

```powershell
cd pineServer

@"
# Pine Server Environment Variables
ROBLE_PROJECT_ID=tracking_7d2ad2db74
ROBLE_BASE_URL=https://roble-api.openlab.uninorte.edu.co
ADMIN_EMAIL=admin@pine.com
ADMIN_PASSWORD=ThePassword!1
"@ | Out-File -FilePath .env -Encoding UTF8
```

### Option 4: Using Command Prompt (Windows)

```cmd
cd pineServer
(
echo # Pine Server Environment Variables
echo ROBLE_PROJECT_ID=tracking_7d2ad2db74
echo ROBLE_BASE_URL=https://roble-api.openlab.uninorte.edu.co
echo ADMIN_EMAIL=admin@pine.com
echo ADMIN_PASSWORD=ThePassword!1
) > .env
```

## Verify Setup

After creating the `.env` file, verify it exists:

```bash
# List files including hidden ones
dir /a    # Windows
ls -la    # Linux/Mac

# Check content (be careful not to share this!)
type .env     # Windows
cat .env      # Linux/Mac
```

## Running Docker Compose

Once `.env` is created, Docker Compose will automatically load the variables:

```bash
docker-compose up -d
```

## Security Notes

✅ **DO:**
- Keep `.env` file local only
- Never commit `.env` to Git
- Share `.env.sample` instead
- Use different credentials for production

❌ **DON'T:**
- Commit `.env` to version control
- Share `.env` file publicly
- Use same passwords everywhere
- Store credentials in code

## Files Created

- ✅ `.env.sample` - Template with placeholder values (safe to share)
- ✅ `docker-compose.yml` - Updated to use `env_file`
- 🔄 `.env` - **You need to create this manually** (blocked by gitignore)

## What Changed

### Before (docker-compose.yml):
```yaml
environment:
  - ROBLE_PROJECT_ID=tracking_7d2ad2db74
  - ROBLE_BASE_URL=https://roble-api.openlab.uninorte.edu.co
  - ADMIN_EMAIL=admin@pine.com
  - ADMIN_PASSWORD=ThePassword!1
```

### After (docker-compose.yml):
```yaml
env_file:
  - .env
```

This is more secure and follows best practices! 🔒
