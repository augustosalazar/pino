"""
Test script for R_PINE database operations - Version 2
Uses Roble's auto-generated _id instead of custom ID fields
"""

import requests
from typing import Dict, List, Optional


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
        """Read records from a table"""
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
    
    def insert_records(self, table_name: str, records: List[Dict]) -> Dict:
        """Insert records into a table - returns inserted records with _id"""
        url = f"{self.db_url}/insert"
        
        payload = {
            "tableName": table_name,
            "records": records
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Inserted {len(result.get('inserted', []))} record(s) into '{table_name}'")
            
            if result.get("skipped") and len(result["skipped"]) > 0:
                print(f"  ⚠ Warning: {len(result['skipped'])} records were skipped")
                for skip in result['skipped']:
                    print(f"    - {skip}")
            
            return result
        else:
            print(f"✗ Failed to insert into '{table_name}': {response.status_code}")
            print(f"  Response: {response.text}")
            return {"inserted": [], "skipped": []}
    
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


def main():
    """Main test execution"""
    
    PROJECT_ID = "tracking_7d2ad2db74"
    ADMIN_EMAIL = "admin@pine.com"
    ADMIN_PASSWORD = "ThePassword!1"
    
    print("=" * 60)
    print("R_PINE Database Test Suite V2")
    print("Using Roble's auto-generated _id")
    print("=" * 60)
    print()
    
    client = RobleDBClient(PROJECT_ID)
    
    if not client.login(ADMIN_EMAIL, ADMIN_PASSWORD):
        print("\n✗ Tests aborted due to login failure")
        return
    
    print()
    
    # ========================================
    # TEST 1: Insert a user (no user_id field)
    # ========================================
    print("=" * 60)
    print("TEST 1: Inserting test user")
    print("=" * 60)
    
    user_record = {
        "user_ref": client.user_id,  # ID from Roble authentication
        "email": "testuser@pine.com",
        "username": "Test User",
        "current_score": 0
    }
    
    result = client.insert_records("pine_users", [user_record])
    
    if not result.get("inserted"):
        print("✗ User insert failed, aborting tests")
        return
    
    # Get the _id of the inserted user
    user_id = result["inserted"][0]["_id"]
    print(f"  Created user with _id: {user_id}")
    
    # ========================================
    # TEST 2: Insert difficulty profiles
    # ========================================
    print("\n" + "=" * 60)
    print("TEST 2: Inserting difficulty profiles")
    print("=" * 60)
    
    operators = ['+', '-', '*', '/']
    profiles = []
    
    for op in operators:
        profile = {
            "user_ref": user_id,  # Reference to user's _id
            "operator": op,
            "current_difficulty": 1.00,
            "success_rate": 0.00,
            "total_attempts": 0,
            "total_correct": 0
        }
        profiles.append(profile)
    
    result = client.insert_records("pine_user_difficulty_profile", profiles)
    print(f"  Inserted profiles for user {user_id}")
    
    # ========================================
    # TEST 3: Insert an exercise session
    # ========================================
    print("\n" + "=" * 60)
    print("TEST 3: Inserting exercise session")
    print("=" * 60)
    
    session_record = {
        "user_ref": user_id,
        "total_exercises": 10,
        "correct_answers": 7,
        "avg_difficulty": 2.5,
        "total_time_ms": 125000,
        "score_earned": 175
    }
    
    result = client.insert_records("pine_exercise_sessions", [session_record])
    
    if not result.get("inserted"):
        print("✗ Session insert failed")
        session_id = None
    else:
        session_id = result["inserted"][0]["_id"]
        print(f"  Created session with _id: {session_id}")
    
    # ========================================
    # TEST 4: Insert exercises
    # ========================================
    if session_id:
        print("\n" + "=" * 60)
        print("TEST 4: Inserting exercises")
        print("=" * 60)
        
        import json
        exercises = []
        for i in range(3):
            exercise = {
                "session_ref": session_id,
                "user_ref": user_id,
                "exercise_type": 1,
                "operator": "+",
                "operand_1": 5 + i,
                "operand_2": 3 + i,
                "correct_answer": 8 + (i * 2),
                "user_answer": 8 + (i * 2),
                "options": json.dumps([8 + (i * 2), 7 + (i * 2), 9 + (i * 2), 10 + (i * 2)]),
                "difficulty_level": 1.5,
                "is_correct": True,
                "time_taken_ms": 5000 + (i * 1000)
            }
            exercises.append(exercise)
        
        result = client.insert_records("pine_exercises", exercises)
        print(f"  Inserted {len(result.get('inserted', []))} exercises")
    
    # ========================================
    # TEST 5: Insert difficulty adjustment
    # ========================================
    if session_id:
        print("\n" + "=" * 60)
        print("TEST 5: Inserting difficulty adjustment")
        print("=" * 60)
        
        adjustment = {
            "user_ref": user_id,
            "session_ref": session_id,
            "operator": "+",
            "previous_difficulty": 1.0,
            "new_difficulty": 1.5,
            "reason": "Success rate >= 80%"
        }
        
        client.insert_records("pine_difficulty_adjustments", [adjustment])
    
    # ========================================
    # TEST 6: Query data
    # ========================================
    print("\n" + "=" * 60)
    print("TEST 6: Querying data")
    print("=" * 60)
    
    # Query user
    print("\n1. Querying user by _id...")
    users = client.read_table("pine_users", {"_id": user_id})
    if users:
        user = users[0]
        print(f"  Username: {user.get('username')}")
        print(f"  Email: {user.get('email')}")
        print(f"  Score: {user.get('current_score')}")
    
    # Query profiles by user_ref
    print("\n2. Querying difficulty profiles by user_ref...")
    profiles = client.read_table("pine_user_difficulty_profile", {"user_ref": user_id})
    if profiles:
        print(f"  Found {len(profiles)} profiles:")
        for p in profiles:
            print(f"    {p.get('operator')}: difficulty={p.get('current_difficulty')}, rate={p.get('success_rate')}%")
    
    # Query session by user_ref
    if session_id:
        print("\n3. Querying sessions by user_ref...")
        sessions = client.read_table("pine_exercise_sessions", {"user_ref": user_id})
        if sessions:
            print(f"  Found {len(sessions)} sessions")
            for s in sessions:
                print(f"    Session {s.get('_id')}: {s.get('correct_answers')}/{s.get('total_exercises')} correct")
        
        # Query exercises by session_ref
        print("\n4. Querying exercises by session_ref...")
        exercises = client.read_table("pine_exercises", {"session_ref": session_id})
        print(f"  Found {len(exercises)} exercises")
    
    # Query adjustments
    print("\n5. Querying difficulty adjustments by user_ref...")
    adjustments = client.read_table("pine_difficulty_adjustments", {"user_ref": user_id})
    if adjustments:
        print(f"  Found {len(adjustments)} adjustments")
        for adj in adjustments:
            print(f"    {adj.get('operator')}: {adj.get('previous_difficulty')} → {adj.get('new_difficulty')}")
    
    # ========================================
    # Summary
    # ========================================
    print("\n" + "=" * 60)
    print("✓ ALL TESTS COMPLETED")
    print("=" * 60)
    print(f"\nTest user _id: {user_id}")
    if session_id:
        print(f"Test session _id: {session_id}")
    print("\nVerify data in Roble's interface")


if __name__ == "__main__":
    main()
