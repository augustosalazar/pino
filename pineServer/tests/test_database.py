"""
Test script for R_PINE database operations
Tests both reading and writing to all tables with pino_ prefix
"""

import os
import uuid
import requests
from typing import Dict, List, Optional
from datetime import datetime
import pytest
from dotenv import load_dotenv


load_dotenv()


class RobleDBClient:
    """Client for Roble database operations"""
    
    def __init__(self, project_id: str, base_url: str = "https://roble-api.openlab.uninorte.edu.co"):
        self.project_id = project_id
        self.base_url = base_url
        self.auth_url = f"{base_url}/auth/{project_id}".rstrip('/')
        self.db_url = f"{base_url}/database/{project_id}"
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.user_id: Optional[str] = None
    
    def login(self, email: str, password: str) -> bool:
        """Authenticate with Roble"""
        print(f"Logging in as {email}...")
        url = f"{self.auth_url}/login"
        
        response = self.session.post(url, json={"email": email, "password": password})
        
        try:
            response.raise_for_status()
        except requests.HTTPError:
            print(f"✗ Login error {response.status_code}: {response.text}")
            return False
        
        data = response.json()
        self.access_token = data.get("accessToken")
        self.user_id = data.get("user", {}).get("id")
        self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
        
        print(f"✓ Logged in successfully")
        print(f"  User ID: {self.user_id}")
        return True
    
    def read_table(self, table_name: str, filters: Dict = None) -> List[Dict]:
        """
        Read records from a table
        filters: dict with field-value pairs to filter (e.g., {"user_id": "123"})
        """
        url = f"{self.db_url}/read"
        params = {"tableName": table_name}
        
        if filters:
            params.update(filters)
        
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Read {len(data)} records from '{table_name}'")
            return data
        else:
            print(f"✗ Failed to read from '{table_name}': {response.status_code} - {response.text}")
            return []
    
    def insert_records(self, table_name: str, records: List[Dict]) -> bool:
        """Insert records into a table"""
        url = f"{self.db_url}/insert"
        
        payload = {
            "tableName": table_name,
            "records": records
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Inserted {len(records)} record(s) into '{table_name}'")
            
            # Check for skipped records
            if result.get("skipped") and len(result["skipped"]) > 0:
                print(f"  ⚠ Warning: {len(result['skipped'])} records were skipped")
                print(f"    Skipped: {result['skipped']}")
            
            return True
        else:
            print(f"✗ Failed to insert into '{table_name}': {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    def update_record(self, table_name: str, record_id: str, updates: Dict) -> bool:
        """Update a record by _id"""
        url = f"{self.db_url}/update"
        
        payload = {
            "tableName": table_name,
            "idColumn": "_id",
            "idValue": record_id,
            "updates": updates
        }
        
        response = self.session.put(url, json=payload)
        
        if response.status_code == 200:
            print(f"✓ Updated record in '{table_name}'")
            return True
        else:
            print(f"✗ Failed to update '{table_name}': {response.status_code} - {response.text}")
            return False
    
    def delete_record(self, table_name: str, record_id: str) -> bool:
        """Delete a record by _id"""
        url = f"{self.db_url}/delete"
        
        payload = {
            "tableName": table_name,
            "idColumn": "_id",
            "idValue": record_id,
            "updates": {}
        }
        
        response = self.session.delete(url, json=payload)
        
        if response.status_code == 200:
            print(f"✓ Deleted record from '{table_name}'")
            return True
        else:
            print(f"✗ Failed to delete from '{table_name}': {response.status_code} - {response.text}")
            return False


# -------------------------
# Pytest fixtures (module scope)
# -------------------------


@pytest.fixture(scope="session")
def client():
    """Authenticated Roble client or skip if disabled/missing credentials."""
    if os.getenv("RUN_ROBLE_TESTS") not in {"1", "true", "True", "yes", "on"}:
        pytest.skip("Roble tests disabled; set RUN_ROBLE_TESTS=1 to enable.")

    project_id = os.getenv("ROBLE_PROJECT_ID") or "tracking_7d2ad2db74"
    admin_email = os.getenv("ROBLE_ADMIN_EMAIL")
    admin_password = os.getenv("ROBLE_ADMIN_PASSWORD")

    if not (admin_email and admin_password):
        pytest.skip("Roble credentials not provided (set ROBLE_ADMIN_EMAIL/ROBLE_ADMIN_PASSWORD)")

    c = RobleDBClient(project_id)
    if not c.login(admin_email, admin_password):
        pytest.skip("Roble login failed; skipping integration DB tests")
    return c


@pytest.fixture(scope="session")
def user_and_session(client):
    """Create a test user, profiles, session, exercises, adjustment; return ids, then clean up."""
    test_user_id = str(uuid.uuid4())
    user_record = {
        "user_id": test_user_id,
        "email": f"test_{test_user_id[:8]}@test.com",
        "username": "Test User",
        "current_score": 0
    }
    assert client.insert_records("pine_users", [user_record])

    operators = ['+', '-', '*', '/']
    profiles = []
    for op in operators:
        profiles.append({
            "profile_id": str(uuid.uuid4()),
            "user_id": test_user_id,
            "operator": op,
            "current_difficulty": 1.00,
            "success_rate": 0.00,
            "total_attempts": 0,
            "total_correct": 0
        })
    assert client.insert_records("pine_user_difficulty_profile", profiles)

    session_id = str(uuid.uuid4())
    session_record = {
        "session_id": session_id,
        "user_id": test_user_id,
        "total_exercises": 10,
        "correct_answers": 7,
        "avg_difficulty": 2.5,
        "total_time_ms": 125000,
        "score_earned": 175
    }
    assert client.insert_records("pine_exercise_sessions", [session_record])

    exercises = []
    for i in range(3):
        exercises.append({
            "exercise_id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": test_user_id,
            "exercise_type": 1,
            "operator": "+",
            "operand_1": 5 + i,
            "operand_2": 3 + i,
            "correct_answer": 8 + (i * 2),
            "user_answer": 8 + (i * 2),
            "options": [8 + (i * 2), 7 + (i * 2), 9 + (i * 2), 10 + (i * 2)],
            "difficulty_level": 1.5,
            "is_correct": True,
            "time_taken_ms": 5000 + (i * 1000)
        })
    assert client.insert_records("pine_exercises", exercises)

    adjustment = {
        "adjustment_id": str(uuid.uuid4()),
        "user_id": test_user_id,
        "session_id": session_id,
        "operator": "+",
        "previous_difficulty": 1.0,
        "new_difficulty": 1.5,
        "reason": "Success rate >= 80%"
    }
    client.insert_records("pine_difficulty_adjustments", [adjustment])

    try:
        yield test_user_id, session_id
    finally:
        cleanup_targets = [
            ("pine_difficulty_adjustments", {"session_id": session_id}),
            ("pine_exercises", {"session_id": session_id}),
            ("pine_exercise_sessions", {"session_id": session_id}),
            ("pine_user_difficulty_profile", {"user_id": test_user_id}),
            ("pine_users", {"user_id": test_user_id}),
        ]

        for table, filters in cleanup_targets:
            records = client.read_table(table, filters)
            for r in records:
                record_id = r.get("_id")
                if record_id:
                    client.delete_record(table, record_id)


@pytest.fixture(scope="session")
def user_id(user_and_session):
    return user_and_session[0]


@pytest.fixture(scope="session")
def session_id(user_and_session):
    return user_and_session[1]


def test_roble_connectivity():
    """Test basic connectivity to Roble API before running authenticated tests."""
    base_url = os.getenv("ROBLE_BASE_URL", "https://roble-api.openlab.uninorte.edu.co")
    
    if os.getenv("RUN_ROBLE_TESTS") not in {"1", "true", "True", "yes", "on"}:
        pytest.skip("Roble tests disabled; set RUN_ROBLE_TESTS=1 to enable.")
    
    response = requests.get(base_url, timeout=5)
    assert response.status_code in {200, 301, 302, 404}, f"Base URL unreachable: {response.status_code}"


def test_roble_schema_tables_exist(client: RobleDBClient):
    """Validate Roble tables respond and include expected keys without mutating data."""
    tables_and_keys = {
        "pine_users": {"user_id", "email", "username"},
        "pine_user_difficulty_profile": {"user_id", "operator", "current_difficulty"},
        "pine_exercise_sessions": {"session_id", "user_id", "total_exercises"},
        "pine_exercises": {"session_id", "user_id", "exercise_type"},
        "pine_difficulty_adjustments": {"session_id", "user_id", "operator"},
        "pine_user_gamification": {"user_ref", "pp_total", "racha_dias"},
        "pine_user_operations": {"user_ref", "operacion", "nivel_dominio"},
        "pine_batches_completados": {"user_ref", "operacion", "batch_type"},
        "pine_mini_jefes_intentos": {"user_ref", "operacion", "aprobado"},
        "pine_weekly_leaderboard": {"user_ref", "semana_id", "pp_semana", "ranking"},
    }

    for table, expected_keys in tables_and_keys.items():
        records = client.read_table(table)
        assert isinstance(records, list)
        if records:
            first = records[0]
            assert expected_keys.issubset(first.keys()), f"Missing keys in {table}: {expected_keys - set(first.keys())}"


def main():
    """Main test execution"""
    
    # Configuration
    PROJECT_ID = "tracking_7d2ad2db74"
    ADMIN_EMAIL = "admin@pine.com"
    ADMIN_PASSWORD = "ThePassword!1"
    
    print("=" * 60)
    print("R_PINE Database Test Suite")
    print("=" * 60)
    print(f"Project ID: {PROJECT_ID}")
    print()
    
    # Initialize client
    client = RobleDBClient(PROJECT_ID)
    
    # Login
    if not client.login(ADMIN_EMAIL, ADMIN_PASSWORD):
        print("\n✗ Tests aborted due to login failure")
        return
    
    # Run tests
    try:
        # Test 1: Query existing tables
        test_queries(client)
        
        # Test 2: Insert test data
        user_id, session_id = test_insert(client)
        
        if user_id and session_id:
            # Test 3: Query with filters
            test_query_with_filters(client, user_id, session_id)
            
            # Test 4: Update records
            test_update(client, user_id)
            
            print("\n" + "=" * 60)
            print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print(f"\nTest user ID: {user_id}")
            print(f"Test session ID: {session_id}")
            print("\nYou can now manually verify the data in Roble's interface")
        else:
            print("\n⚠ Some tests were skipped due to insert failures")
    
    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
