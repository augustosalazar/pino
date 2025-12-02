# Timezone Configuration - Colombian Time

## 🌎 Overview

All datetime operations in the pineServer are now configured to use **Colombian timezone** (`America/Bogota`, GMT-5) to ensure consistency regardless of where the server is physically located.

---

## 📅 Why Colombia Time?

- **User-centric**: Most users are in Colombia
- **Predictable**: Daily resets happen at midnight Colombian time (00:00 GMT-5)
- **Consistent**: Streaks, daily limits, and weekly resets all use the same timezone
- **Independent**: Works regardless of server location (local, cloud, Docker, etc.)

---

## 🔧 Implementation

### Central Utility Module

All datetime operations go through `datetime_utils.py`, which provides:

```python
from datetime_utils import now_colombia, now_colombia_iso

# Get current time in Colombia
current_time = now_colombia()  # datetime object with timezone

# Get ISO string with timezone info
timestamp = now_colombia_iso()  # "2025-12-02T14:30:00-05:00"
```

### Updated Modules

All gamification modules now use Colombian time:

- ✅ `gamification_profile.py` - User profiles, streaks, XP, PD
- ✅ `gamification_admin.py` - Daily/weekly reset tasks
- ✅ `gamification_batch.py` - Batch processing, pending items
- ✅ `gamification_unlocks.py` - Operation and mode unlocks

---

## ⏰ Daily Reset Schedule

### Midnight in Colombian Time

The daily reset happens at **00:00 Colombia time (GMT-5)**:

| Location | Time Zone | Reset Time (Local) |
|----------|-----------|-------------------|
| 🇨🇴 Bogotá | GMT-5 | 00:00 (midnight) |
| 🇺🇸 New York | GMT-5 (EST) | 00:00 (midnight) |
| 🇺🇸 LA | GMT-8 (PST) | 21:00 (9 PM previous day) |
| 🇪🇸 Madrid | GMT+1 | 06:00 (6 AM) |
| 🇯🇵 Tokyo | GMT+9 | 14:00 (2 PM) |

### What Happens at Midnight (Colombia Time)

1. **Reset `pp_dia` to 0** for all users
2. **Check streaks**: Users who haven't played lose their streak
3. **Weekly reset** (Mondays only): Reset `pp_semana` and `pd_semana`

---

## 🐳 Docker Deployment

### Important Note

When running in Docker or cloud environments, the container might have a different timezone. **This doesn't matter** because we explicitly use `America/Bogota` in the code.

### Example Docker Setup

```dockerfile
FROM python:3.9

# Optional: Set system timezone (for logs only, not required)
ENV TZ=America/Bogota
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
```

### Cron Jobs in Docker

```bash
# This runs at midnight Colombian time, regardless of server location
0 0 * * * cd /app && python gamification_admin.py daily
```

---

## 🧪 Testing

### Test Current Time

```bash
python -c "from datetime_utils import now_colombia; print(now_colombia())"
# Output: 2025-12-02 14:30:00-05:00
```

### Test Time Functions

```python
from datetime_utils import (
    now_colombia,
    now_colombia_iso,
    get_current_date_colombia,
    get_current_time_colombia
)

print(now_colombia())              # 2025-12-02 14:30:00-05:00
print(now_colombia_iso())          # 2025-12-02T14:30:00-05:00
print(get_current_date_colombia()) # 2025-12-02
print(get_current_time_colombia()) # 14:30:00
```

---

## 📝 Database Storage

### Timezone-Aware Timestamps

All timestamps are now stored with timezone information:

```json
{
  "created_at": "2025-12-02T14:30:00-05:00",
  "updated_at": "2025-12-02T14:30:00-05:00",
  "semana_inicio": "2025-12-02T00:00:00-05:00"
}
```

### Benefits

- ✅ **No ambiguity**: Every timestamp includes timezone offset
- ✅ **Portable**: Database can be moved anywhere
- ✅ **Accurate**: Historical data maintains correct time context
- ✅ **Compatible**: ISO format works with most libraries

---

## 🔍 Comparison: Before vs After

### Before (Naive Server Time)

```python
# ❌ Problem: Uses whatever timezone the server happens to be in
datetime.now().isoformat()
# Output: "2025-12-02T14:30:00" (no timezone info)
```

**Issues:**
- If server moves to different timezone, all times shift
- Can't tell what timezone a timestamp represents
- Streaks reset at different times depending on server location

### After (Explicit Colombian Time)

```python
# ✅ Solution: Always uses Colombia time
now_colombia_iso()
# Output: "2025-12-02T14:30:00-05:00" (includes timezone)
```

**Benefits:**
- Consistent regardless of server location
- Clear timezone in every timestamp
- Predictable daily resets for all users

---

## 🚀 Migration Notes

### Existing Data

Old timestamps without timezone info will be **assumed to be Colombian time** when parsed:

```python
from datetime_utils import parse_iso_to_colombia

# Old format (no timezone)
old_timestamp = "2025-12-02T14:30:00"
dt = parse_iso_to_colombia(old_timestamp)
# Assumed to be: 2025-12-02T14:30:00-05:00

# New format (with timezone)
new_timestamp = "2025-12-02T14:30:00-05:00"
dt = parse_iso_to_colombia(new_timestamp)
# Correctly parsed: 2025-12-02T14:30:00-05:00
```

### No Data Loss

- Existing timestamps continue to work
- New timestamps include explicit timezone
- Gradual migration as records are updated

---

## ⚠️ Important Reminders

1. **Always use `datetime_utils`**: Never use `datetime.now()` directly in gamification code
2. **Cron jobs**: Set to midnight Colombian time (00:00)
3. **Server location**: Doesn't matter - we explicitly use Colombian time
4. **Testing**: Use `datetime_utils` functions to get consistent results

---

## 📚 Related Files

- `/pineServer/datetime_utils.py` - Central timezone utilities
- `/pineServer/gamification_admin.py` - Daily reset tasks
- `/pineServer/gamification_profile.py` - User profile management
- `/pineServer/CRON_JOBS_SETUP.md` - Cron job configuration

---

**Last Updated**: 2025-12-02
**Timezone**: America/Bogota (GMT-5)
