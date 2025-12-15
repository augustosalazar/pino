"""
Simple interactive login test based on your working code
"""

import requests
from typing import Optional


def simple_login_test():
    """Test login with manual credential input"""
    
    PROJECT_ID = "tracking_7d2ad2db74"
    BASE_URL = "https://roble-api.openlab.uninorte.edu.co"
    
    auth_url = f"{BASE_URL}/auth/{PROJECT_ID}".rstrip('/')
    session = requests.Session()
    
    print("=" * 60)
    print("Simple Login Test (based on your working code)")
    print("=" * 60)
    print(f"Project ID: {PROJECT_ID}")
    print()
    
    # Get credentials
    print("Enter credentials to test:")
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    print()
    print("Attempting login...")
    
    url = f"{auth_url}/login"
    print(f"URL: {url}")
    
    # Exactly as in your working code
    resp = session.post(url, json={'email': email, 'password': password})
    
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")
    
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        print(f"\n✗ Login error {resp.status_code}: {resp.text}")
        return False
    
    data = resp.json()
    access_token = data.get('accessToken')
    refresh_token = data.get('refreshToken')
    user_id = data.get('user', {}).get('id')
    
    session.headers.update({'Authorization': f'Bearer {access_token}'})
    
    print("\n✓ Login successful!")
    print(f"User ID: {user_id}")
    print(f"Access Token: {access_token[:50]}..." if access_token else "None")
    
    return True


if __name__ == "__main__":
    simple_login_test()
