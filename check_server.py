#!/usr/bin/env python3
"""
Quick test script for PineServer deployment
Tests basic endpoints to verify server is working
"""

import requests
import json
from datetime import datetime

# Server configuration
BASE_URL = "https://pineserver.openlab.uninorte.edu.co"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health():
    """Test if server is responding"""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_get_institutions():
    """Test getting institutions"""
    print_section("2. Get Institutions")
    try:
        response = requests.get(f"{BASE_URL}/api/institutions")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Found {len(data)} institutions:")
        for inst in data:
            print(f"  - {inst.get('name')} (ID: {inst.get('_id')})")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_ensure_user():
    """Test user creation/check endpoint"""
    print_section("3. Ensure User (Create/Check)")
    try:
        test_user = {
            "user_ref": "test_user_123",
            "email": "test@example.com",
            "username": "testuser"
        }
        response = requests.post(
            f"{BASE_URL}/api/users/ensure",
            json=test_user
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Status: {data.get('status')}")
        if 'user' in data:
            user = data['user']
            print(f"User ID: {user.get('_id')}")
            print(f"Username: {user.get('username')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_get_user_stats():
    """Test getting user stats"""
    print_section("4. Get User Stats")
    try:
        test_user_ref = "test_user_123"
        response = requests.get(f"{BASE_URL}/api/users/{test_user_ref}/stats")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Current Score: {data.get('current_score', 0)}")
            print(f"Total Sessions: {data.get('total_sessions', 0)}")
            print(f"Accuracy: {data.get('accuracy', 0):.1f}%")
            return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_start_session():
    """Test starting a session"""
    print_section("5. Start Session")
    try:
        session_data = {
            "user_ref": "test_user_123"
        }
        response = requests.post(
            f"{BASE_URL}/api/sessions/start",
            json=session_data
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Session ID: {data.get('session_id')}")
            print(f"Exercises Count: {len(data.get('exercises', []))}")
            if data.get('exercises'):
                first_ex = data['exercises'][0]
                print(f"First Exercise: {first_ex.get('problem')}")
            return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run all tests and show summary"""
    print("\n" + "🔍" * 30)
    print("  PINESERVER DEPLOYMENT TEST")
    print(f"  Server: {BASE_URL}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔍" * 30)

    results = {
        "Health Check": test_health(),
        "Get Institutions": test_get_institutions(),
        "Ensure User": test_ensure_user(),
        "Get User Stats": test_get_user_stats(),
        "Start Session": test_start_session()
    }

    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Server is working correctly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check server logs.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
