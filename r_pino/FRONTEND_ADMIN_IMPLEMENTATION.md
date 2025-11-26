# Frontend Implementation Guide - Admin Features

## Summary of Changes Needed

### 1. Update AuthUser Model
Add new fields to the user model:
- `age?: number`
- `grade?: string`
- `user_type: number` (1 = student, 2 = admin)
- `institution_name?: string`

### 2. Create Profile Screen (`app/profile.tsx`)

**Features:**
- Form to edit age and grade
- Save button
- Only visible to students (user_type = 1)

**API Calls:**
```typescript
// Update profile
PUT /api/users/{user_ref}/profile
Body: { age?: number, grade?: string }
```

### 3. Update Home Screen (`app/index.tsx`)

**For Students (user_type = 1):**
- Show institution name at top
- Show personal stats
- Show "Start New Session" button
- Show "View Statistics" button

**For Admins (user_type = 2):**
- Show institution name at top
- Show "Institution Statistics" button instead of game buttons
- Hide "Start New Session" button

**Code Changes:**
```typescript
// Check user type
const isAdmin = user?.user_type === 2;

// Conditionally render buttons
{!isAdmin && (
    <TouchableOpacity onPress={handleStartSession}>
        <Text>Start New Session</Text>
    </TouchableOpacity>
)}

{isAdmin && (
    <TouchableOpacity onPress={() => router.push('/admin-stats')}>
        <Text>Institution Statistics</Text>
    </TouchableOpacity>
)}

// Show institution name
<Text>{user?.institution_name || 'Loading...'}</Text>
```

### 4. Create Admin Stats Screen (`app/admin-stats.tsx`)

**Features:**
- Fetch institution statistics
- Show aggregate data:
  - Total students
  - Average score
  - Total sessions/exercises
  - Overall accuracy
- Filters:
  - Age range (min/max)
  - Grade dropdown
- Apply filters button

**API Calls:**
```typescript
POST /api/institutions/{institution_ref}/stats
Body: {
    institution_ref: string,
    age_min?: number,
    age_max?: number,
    grade?: string
}

Response: {
    total_students: number,
    average_score: number,
    total_sessions: number,
    total_exercises: number,
    overall_accuracy: number,
    filter_options: {
        grades: string[],
        age_range: { min: number, max: number }
    },
    is_uninorte: boolean
}
```

### 5. Update API Service (`services/api.ts`)

Add new methods:
```typescript
static async updateProfile(userRef: string, age?: number, grade?: string) {
    const response = await fetch(`${config.api.baseUrl}/users/${userRef}/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ age, grade })
    });
    if (!response.ok) throw new Error('Failed to update profile');
    return await response.json();
}

static async getInstitutionStats(
    institutionRef: string,
    filters: { age_min?: number; age_max?: number; grade?: string }
) {
    const response = await fetch(
        `${config.api.baseUrl}/institutions/${institutionRef}/stats`,
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ institution_ref: institutionRef, ...filters })
        }
    );
    if (!response.ok) throw new Error('Failed to get institution stats');
    return await response.json();
}
```

### 6. Update \_layout.tsx Navigation

Add profile route:
```typescript
<Stack.Screen name="profile" options={{ title: 'Edit Profile' }} />
<Stack.Screen name="admin-stats" options={{ title: 'Institution Statistics' }} />
```

### 7. Fetch Institution Name

When loading user in `AuthContext` or home screen:
```typescript
// After ensureUser, get institution name
if (user.institution_ref) {
    const institutions = await PineServerAPI.getInstitutions();
    const userInst = institutions.find(i => i._id === user.institution_ref);
    if (userInst) {
        user.institution_name = userInst.name;
    }
}
```

## Backend Changes Already Done ✅

1. ✅ Added `user_type` default value of 1
2. ✅ Added `UpdateProfileRequest` model
3. ✅ Added `InstitutionStatsRequest` model
4. ✅ Created `PUT /api/users/{user_ref}/profile` endpoint
5. ✅ Created `POST /api/institutions/{institution_ref}/stats` endpoint
6. ✅ Uninorte institution shows all users
7. ✅ Statistics filtered by age and grade
8. ✅ Only students (user_type=1) appear in stats

## Testing Checklist

- [ ] Student user can edit profile (age, grade)
- [ ] Student user sees game buttons
- [ ] Admin user does NOT see game buttons
- [ ] Admin user sees Institution Statistics button
- [ ] Admin stats show filtered data correctly
- [ ] Uninorte admin sees all users
- [ ] Non-Uninorte admin sees only their institution
- [ ] Institution name displays on home page
- [ ] Filters work correctly (age min/max, grade)

## Priority Order

1. Update AuthUser model and fetch institution name
2. Conditional rendering on home screen (hide game for admins)
3. Add institution name to home screen
4. Create profile screen for students
5. Create admin stats screen with filters
