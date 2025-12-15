"""
Diagnostic script to test Roble connectivity and project ID
"""

import requests


def test_roble_connection():
    """Test basic connectivity to Roble"""
    
    PROJECT_ID = "tracking_7d2ad2db7"
    BASE_URL = "https://roble-api.openlab.uninorte.edu.co"
    
    print("=" * 60)
    print("Roble Connection Diagnostics")
    print("=" * 60)
    print()
    print(f"Project ID: {PROJECT_ID}")
    print(f"Base URL: {BASE_URL}")
    print()
    
    # Test 1: Check base URL
    print("Test 1: Checking base URL...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✓ Base URL reachable (Status: {response.status_code})")
    except Exception as e:
        print(f"✗ Base URL unreachable: {e}")
        return
    
    print()
    
    # Test 2: Check auth endpoint
    auth_url = f"{BASE_URL}/auth/{PROJECT_ID}"
    print(f"Test 2: Checking auth endpoint...")
    print(f"  URL: {auth_url}")
    
    # Try login endpoint
    login_url = f"{auth_url}/login"
    print(f"\nAttempting OPTIONS request to: {login_url}")
    try:
        response = requests.options(login_url, timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print()
    
    # Test 3: Try a malformed login to see the error response
    print("Test 3: Testing login endpoint with empty credentials...")
    try:
        response = requests.post(login_url, json={"email": "", "password": ""})
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print()
    
    # Test 4: Database endpoint
    db_url = f"{BASE_URL}/database/{PROJECT_ID}"
    print(f"Test 4: Checking database endpoint...")
    print(f"  URL: {db_url}")
    
    # Try a read without auth
    read_url = f"{db_url}/read?tableName=test"
    try:
        response = requests.get(read_url, timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print()
    print("=" * 60)
    print("Diagnostics Complete")
    print("=" * 60)
    print()
    print("If all endpoints return 401/403, the project ID is likely correct.")
    print("If endpoints return 404, the project ID may be wrong.")
    print("If you see 500 errors, there may be a server-side issue.")


if __name__ == "__main__":
    test_roble_connection()
