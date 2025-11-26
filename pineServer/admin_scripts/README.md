# Admin Scripts

Administrative scripts for managing the Pino application.

## Prerequisites

Make sure you have the `.env` file configured with:
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `ROBLE_BASE_URL`
- `ROBLE_PROJECT_ID`

## Scripts

### `create_user.py`

Interactive script to create a new user in both Roble Auth and the pine_users database.

**Usage:**
```bash
cd pineServer
python admin_scripts/create_user.py
```

**Features:**
- Creates user in Roble authentication service
- Adds user record to pine_users table
- Interactive prompts for all user details
- Lists available institutions
- Validates input
- Shows summary before creation
- Handles errors gracefully

**User Fields:**
- **Email** (required): User's email address
- **Name** (required): User's full name
- **Password** (required): User's password for authentication
- **Username** (optional): Display name (defaults to email prefix)
- **Institution** (optional): Select from available institutions
- **Age** (optional): User's age (1-120)
- **Grade** (optional): User's grade/year (e.g., "9th Grade", "Year 10")
- **User Type** (required): 
  - `1` - Student (default) - Can play the game
  - `2` - Admin - Can view institution statistics

**Example Session:**
```
============================================================
PINO - Create New User
============================================================

Fetching institutions...

Found 2 institution(s):
  1. Uninorte
  2. Test School

Enter user details:
------------------------------------------------------------
Email: john.doe@example.com
Full Name: John Doe
Password: SecurePass123
Username (optional, will use email prefix if empty): johndoe
  → Using username: johndoe

Select institution:
  0. None (skip)
  1. Uninorte
  2. Test School
Choice (0-2): 1
  → Selected: Uninorte

Age (optional, press Enter to skip): 15

Grade/Year (optional, press Enter to skip): 10th Grade

User Type:
  1. Student (default)
  2. Admin
Choice (1-2, default: 1): 1
  → User type: Student

============================================================
Summary:
------------------------------------------------------------
Email:       john.doe@example.com
Name:        John Doe
Username:    johndoe
Institution: Uninorte
Age:         15
Grade:       10th Grade
User Type:   Student
============================================================

Create this user? (yes/no): yes

Creating user...
------------------------------------------------------------
✓ User created in auth service with ID: abc123...
✓ User record created in pine_users table

============================================================
✓ SUCCESS! User created successfully
============================================================
User ID:  abc123...
Email:    john.doe@example.com
Username: johndoe
```

## Adding More Scripts

To add new admin scripts:
1. Create a new `.py` file in this directory
2. Import `roble_client` from the parent directory:
   ```python
   import sys
   import os
   sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
   from roble_client import roble_client
   ```
3. Load environment variables:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```
4. Document it in this README

## Common Tasks

### Create a Student User
```bash
python admin_scripts/create_user.py
# Select user type: 1 (Student)
```

### Create an Admin User
```bash
python admin_scripts/create_user.py
# Select user type: 2 (Admin)
```

### Create a User Without Institution
```bash
python admin_scripts/create_user.py
# When prompted for institution, select: 0 (None)
```

## Troubleshooting

**"Error: Missing required environment variables"**
- Make sure your `.env` file exists in the pineServer directory
- Verify all required variables are set

**"No institutions found"**
- Run the table creation script first to populate institutions
- Or manually add institutions to pine_institutions table

**"Error creating user in auth service"**
- Check that ROBLE_BASE_URL is correct
- Verify ADMIN_EMAIL and ADMIN_PASSWORD are valid
- Make sure the Roble service is running

**"User was created in auth service but not in pine_users"**
- The user exists in authentication but needs manual database entry
- Note the User ID shown and manually insert into pine_users table
