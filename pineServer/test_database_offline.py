"""
Offline database tests using in-memory SQLite.
Covers CRUD-style functionality without hitting Roble.
"""

import json
import sqlite3
import uuid
from typing import Dict, List, Optional
import pytest


class SQLiteClient:
    """Minimal client with a Roble-like interface backed by SQLite."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row

    def read_table(self, table_name: str, filters: Optional[Dict] = None) -> List[Dict]:
        query = f"SELECT * FROM {table_name}"
        params = []
        if filters:
            clauses = []
            for key, value in filters.items():
                clauses.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(clauses)
        cur = self.conn.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]

    def insert_records(self, table_name: str, records: List[Dict]) -> bool:
        for rec in records:
            rec = rec.copy()
            if isinstance(rec.get("options"), (list, dict)):
                rec["options"] = json.dumps(rec["options"])
            columns = list(rec.keys())
            placeholders = ",".join(["?"] * len(columns))
            values = [rec[col] for col in columns]
            self.conn.execute(
                f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})",
                values,
            )
        self.conn.commit()
        return True

    def update_record(self, table_name: str, record_id: str, updates: Dict, id_column: str = "_id") -> bool:
        if not updates:
            return True
        columns = list(updates.keys())
        assignments = ",".join([f"{col} = ?" for col in columns])
        values = [updates[col] for col in columns]
        values.append(record_id)
        self.conn.execute(
            f"UPDATE {table_name} SET {assignments} WHERE {id_column} = ?",
            values,
        )
        self.conn.commit()
        return True

    def delete_record(self, table_name: str, record_id: str, id_column: str = "_id") -> bool:
        self.conn.execute(f"DELETE FROM {table_name} WHERE {id_column} = ?", (record_id,))
        self.conn.commit()
        return True


def _create_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE pine_users (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            email TEXT,
            username TEXT,
            current_score INTEGER
        );

        CREATE TABLE pine_user_difficulty_profile (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id TEXT UNIQUE,
            user_id TEXT,
            operator TEXT,
            current_difficulty REAL,
            success_rate REAL,
            total_attempts INTEGER,
            total_correct INTEGER
        );

        CREATE TABLE pine_exercise_sessions (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            user_id TEXT,
            total_exercises INTEGER,
            correct_answers INTEGER,
            avg_difficulty REAL,
            total_time_ms INTEGER,
            score_earned INTEGER
        );

        CREATE TABLE pine_exercises (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_id TEXT UNIQUE,
            session_id TEXT,
            user_id TEXT,
            exercise_type INTEGER,
            operator TEXT,
            operand_1 INTEGER,
            operand_2 INTEGER,
            correct_answer INTEGER,
            user_answer INTEGER,
            options TEXT,
            difficulty_level REAL,
            is_correct INTEGER,
            time_taken_ms INTEGER
        );

        CREATE TABLE pine_difficulty_adjustments (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            adjustment_id TEXT UNIQUE,
            user_id TEXT,
            session_id TEXT,
            operator TEXT,
            previous_difficulty REAL,
            new_difficulty REAL,
            reason TEXT
        );
        """
    )
    conn.commit()


@pytest.fixture(scope="function")
def sqlite_client():
    conn = sqlite3.connect(":memory:")
    _create_schema(conn)
    client = SQLiteClient(conn)
    try:
        yield client
    finally:
        conn.close()


@pytest.fixture(scope="function")
def user_and_session(sqlite_client: SQLiteClient):
    test_user_id = str(uuid.uuid4())
    user_record = {
        "user_id": test_user_id,
        "email": f"test_{test_user_id[:8]}@test.com",
        "username": "Test User",
        "current_score": 0,
    }
    sqlite_client.insert_records("pine_users", [user_record])

    operators = ["+", "-", "*", "/"]
    profiles = []
    for op in operators:
        profiles.append(
            {
                "profile_id": str(uuid.uuid4()),
                "user_id": test_user_id,
                "operator": op,
                "current_difficulty": 1.00,
                "success_rate": 0.00,
                "total_attempts": 0,
                "total_correct": 0,
            }
        )
    sqlite_client.insert_records("pine_user_difficulty_profile", profiles)

    session_id = str(uuid.uuid4())
    session_record = {
        "session_id": session_id,
        "user_id": test_user_id,
        "total_exercises": 10,
        "correct_answers": 7,
        "avg_difficulty": 2.5,
        "total_time_ms": 125000,
        "score_earned": 175,
    }
    sqlite_client.insert_records("pine_exercise_sessions", [session_record])

    exercises = []
    for i in range(3):
        exercises.append(
            {
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
                "is_correct": 1,
                "time_taken_ms": 5000 + (i * 1000),
            }
        )
    sqlite_client.insert_records("pine_exercises", exercises)

    adjustment = {
        "adjustment_id": str(uuid.uuid4()),
        "user_id": test_user_id,
        "session_id": session_id,
        "operator": "+",
        "previous_difficulty": 1.0,
        "new_difficulty": 1.5,
        "reason": "Success rate >= 80%",
    }
    sqlite_client.insert_records("pine_difficulty_adjustments", [adjustment])

    return test_user_id, session_id


def test_insert_offline(sqlite_client: SQLiteClient, user_and_session):
    test_user_id, session_id = user_and_session

    users = sqlite_client.read_table("pine_users", {"user_id": test_user_id})
    assert users and users[0]["email"].startswith("test_")

    sessions = sqlite_client.read_table("pine_exercise_sessions", {"session_id": session_id})
    assert sessions and sessions[0]["total_exercises"] == 10

    profiles = sqlite_client.read_table("pine_user_difficulty_profile", {"user_id": test_user_id})
    assert len(profiles) == 4

    exercises = sqlite_client.read_table("pine_exercises", {"session_id": session_id})
    assert len(exercises) == 3

    adjustments = sqlite_client.read_table("pine_difficulty_adjustments", {"session_id": session_id})
    assert len(adjustments) == 1


def test_query_with_filters_offline(sqlite_client: SQLiteClient, user_and_session):
    test_user_id, session_id = user_and_session

    users = sqlite_client.read_table("pine_users", {"user_id": test_user_id})
    assert users[0]["username"] == "Test User"

    exercises = sqlite_client.read_table("pine_exercises", {"session_id": session_id})
    assert len(exercises) == 3
    assert all(ex["is_correct"] == 1 for ex in exercises)

    profiles = sqlite_client.read_table("pine_user_difficulty_profile", {"user_id": test_user_id})
    seen_ops = {p["operator"] for p in profiles}
    assert seen_ops == {"+", "-", "*", "/"}

    adjustments = sqlite_client.read_table("pine_difficulty_adjustments", {"user_id": test_user_id})
    assert adjustments[0]["previous_difficulty"] == 1.0


def test_update_offline(sqlite_client: SQLiteClient, user_and_session):
    test_user_id, _ = user_and_session
    users = sqlite_client.read_table("pine_users", {"user_id": test_user_id})
    user_row = users[0]
    sqlite_client.update_record(
        "pine_users",
        user_row["_id"],
        {"current_score": 500, "username": "Test User (Updated)"},
    )

    updated = sqlite_client.read_table("pine_users", {"user_id": test_user_id})[0]
    assert updated["current_score"] == 500
    assert updated["username"] == "Test User (Updated)"


def test_delete_offline(sqlite_client: SQLiteClient, user_and_session):
    test_user_id, session_id = user_and_session

    exercises = sqlite_client.read_table("pine_exercises", {"session_id": session_id})
    ids = [ex["_id"] for ex in exercises]
    for exercise_id in ids:
        sqlite_client.delete_record("pine_exercises", exercise_id)

    remaining = sqlite_client.read_table("pine_exercises", {"session_id": session_id})
    assert remaining == []

    sqlite_client.delete_record(
        "pine_exercise_sessions",
        sqlite_client.read_table("pine_exercise_sessions", {"session_id": session_id})[0]["_id"],
    )
    assert sqlite_client.read_table("pine_exercise_sessions", {"session_id": session_id}) == []
