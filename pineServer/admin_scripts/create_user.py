"""
Admin Script: Create User
Creates a new user in both Roble Auth and pine_users table
"""

import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path to import roble_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from roble_client import roble_client
import requests


def get_institutions():
    """Fetch all institutions from pine_institutions table"""
    try:
        institutions = roble_client.read_table("pine_institutions")
        return institutions
    except Exception as e:
        print(f"Error fetching institutions: {e}")
        return []


def create_auth_user(email, password, name):
    """Create user in Roble Auth service"""
    try:
        # Get auth service credentials from environment
        roble_base_url = os.getenv('ROBLE_BASE_URL')
        project_id = os.getenv('ROBLE_PROJECT_ID')

        if not all([roble_base_url, project_id]):
            print("Error: Missing required environment variables")
            print("Required: ROBLE_BASE_URL, ROBLE_PROJECT_ID")
            return None

        # Create new user
        signup_url = f"{roble_base_url}/auth/{project_id}/signup-direct"
        signup_response = requests.post(signup_url, json={
            "email": email,
            "password": password,
            "name": name,
        })

        if signup_response.status_code != 201:
            print(f"Error creating user in auth service: {signup_response.text}")
            return None

        login_url = f"{roble_base_url}/auth/{project_id}/login"
        login_response = requests.post(login_url, json={
            "email": email,
            "password": password,
        })

        if login_response.status_code != 201:
            print(f"Error logging in as user: {login_response.text}")
            return None 

        user_data = login_response.json()
        print(user_data)
        user_id = user_data.get('user').get('id')
        
        print(f"✓ User created in auth service with ID: {user_id}")
        return user_id

    except Exception as e:
        print(f"Error creating auth user: {e}")
        return None


def create_pine_user(user_ref, email, username, institution_ref, grade, age, user_type):
    """Create user record in pine_users table"""
    try:
        user_data = {
            "user_ref": user_ref,
            "email": email,
            "username": username,
            "current_score": 0,
            "user_type": user_type
        }

        # Add optional fields
        if institution_ref:
            user_data["institution_ref"] = institution_ref
        if grade:
            user_data["grade"] = grade
        if age:
            user_data["age"] = age

        result = roble_client.insert_records("pine_users", [user_data])
        
        if result.get("inserted") and len(result["inserted"]) > 0:
            print(f"✓ User record created in pine_users table")
            return True
        else:
            print(f"Error creating user in pine_users: {result}")
            return False

    except Exception as e:
        print(f"Error creating pine user: {e}")
        return False


def main():
    print("=" * 60)
    print("PINO - Create New User")
    print("=" * 60)
    print()

    # Get institutions
    print("Fetching institutions...")
    institutions = get_institutions()
    
    # if not institutions:
    #     print("Warning: No institutions found. User will be created without institution.")
    #     institution_ref = None
    # else:
    #     print(f"\nFound {len(institutions)} institution(s):")
    #     for idx, inst in enumerate(institutions, 1):
    #         print(f"  {idx}. {inst.get('name', 'Unknown')}")
    
    print()

    # Collect user information
    print("Enter user details:")
    print("-" * 60)
    
    email = input("Email: ").strip()
    if not email:
        print("Error: Email is required")
        return
    
    name = email.split('@')[0]
    
    password = input("Password: ").strip()
    if not password:
        print("Error: Password is required")
        return
    
    username = email.split('@')[0]
    
    # Institution selection
    institution_ref = None
    if institutions:
        print("\nSelect institution:")
        print("  0. None (skip)")
        for idx, inst in enumerate(institutions, 1):
            print(f"  {idx}. {inst.get('name', 'Unknown')}")
        
        while True:
            try:
                choice = input("Choice (0-{}): ".format(len(institutions))).strip()
                choice_num = int(choice)
                if 0 <= choice_num <= len(institutions):
                    if choice_num > 0:
                        institution_ref = institutions[choice_num - 1].get('_id')
                        print(f"  → Selected: {institutions[choice_num - 1].get('name')}")
                    else:
                        print("  → No institution selected")
                    break
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number.")
    
    # # Age
    # age = None
    # age_input = input("\nAge (optional, press Enter to skip): ").strip()
    # if age_input:
    #     try:
    #         age = int(age_input)
    #         if age < 1 or age > 120:
    #             print("Warning: Unusual age, but continuing...")
    #     except ValueError:
    #         print("Invalid age, skipping...")
    #         age = None
    
    # # Grade
    # grade = input("Grade/Year (optional, press Enter to skip): ").strip()
    # if not grade:
    #     grade = None

    age = 1
    grade = 1
    
    # User type
    print("\nUser Type:")
    print("  1. Student (default)")
    print("  2. Admin")
    user_type_input = input("Choice (1-2, default: 1): ").strip()
    user_type = 2 if user_type_input == "2" else 1
    user_type_label = "Admin" if user_type == 2 else "Student"
    print(f"  → User type: {user_type_label}")
    
    # Confirmation
    print()
    print("=" * 60)
    print("Summary:")
    print("-" * 60)
    print(f"Email:       {email}")
    print(f"Name:        {name}")
    print(f"Username:    {username}")
    print(f"Institution: {institutions[[i for i, inst in enumerate(institutions) if inst.get('_id') == institution_ref][0]].get('name') if institution_ref and institutions else 'None'}")
    print(f"Age:         {age if age else 'Not set'}")
    print(f"Grade:       {grade if grade else 'Not set'}")
    print(f"User Type:   {user_type_label}")
    print("=" * 60)
    
    confirm = input("\nCreate this user? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print()
    print("Creating user...")
    print("-" * 60)
    
    # Step 1: Create user in auth service
    user_id = create_auth_user(email, password, name)
    if not user_id:
        print("\n✗ Failed to create user in auth service")
        return
    
    # Step 2: Create user in pine_users table
    success = create_pine_user(user_id, email, username, institution_ref, grade, age, user_type)
    if not success:
        print("\n✗ Failed to create user in pine_users table")
        print("Warning: User was created in auth service but not in pine_users")
        print(f"User ID: {user_id}")
        return
    
    print()
    print("=" * 60)
    print("✓ SUCCESS! User created successfully")
    print("=" * 60)
    print(f"User ID:  {user_id}")
    print(f"Email:    {email}")
    print(f"Username: {username}")
    print()


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
