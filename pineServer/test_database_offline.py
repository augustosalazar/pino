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

        CREATE TABLE pine_user_gamification (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_ref TEXT UNIQUE,
            pp_total INTEGER,
            pd_global INTEGER,
            xp_total INTEGER,
            racha_dias INTEGER,
            racha_ultima_fecha TEXT
        );

        CREATE TABLE pine_batches_completados (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_ref TEXT,
            operacion TEXT,
            batch_type TEXT,
            score_ganado INTEGER,
            pp_ganados INTEGER,
            pd_ganados INTEGER,
            xp_ganada INTEGER,
            ejercicios_correctos INTEGER,
            ejercicios_totales INTEGER,
            dificultad_promedio REAL,
            nivel_central INTEGER,
            nivel_invisible_antes REAL,
            nivel_invisible_despues REAL,
            fecha_completado TEXT
        );

        CREATE TABLE pine_user_operations (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_ref TEXT,
            operacion TEXT,
            nivel_dominio INTEGER,
            nivel_invisible REAL,
            batches_desde_ultimo_miniboss INTEGER,
            miniboss_completed INTEGER DEFAULT 0,
            UNIQUE(user_ref, operacion)
        );

        CREATE TABLE pine_mini_jefes_intentos (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_ref TEXT,
            operacion TEXT,
            nivel_dominio INTEGER,
            aprobado INTEGER,
            score_obtenido INTEGER,
            fecha_intento TEXT
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

    # Seed gamification profile
    gamif = {
        "user_ref": test_user_id,
        "pp_total": 100,
        "pd_global": 200,
        "xp_total": 500,
        "racha_dias": 2,
        "racha_ultima_fecha": "2025-01-01",
    }
    sqlite_client.insert_records("pine_user_gamification", [gamif])

    # Seed operation state
    operation = {
        "user_ref": test_user_id,
        "operacion": "suma",
        "nivel_dominio": 2,
        "nivel_invisible": 2.5,
        "batches_desde_ultimo_miniboss": 1,
        "miniboss_completed": 0,
    }
    sqlite_client.insert_records("pine_user_operations", [operation])

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


def _compute_score(correct: int, total: int, avg_difficulty: float) -> int:
    errors = total - correct
    base = correct * (5 + avg_difficulty)
    participation = 10
    penalty = 2 * errors
    raw = base + participation - penalty
    return max(0, int(raw))


def _apply_streak(previous_days: int, correct: int, last_date: str, today: str) -> int:
    """
    Increment streak if >=4 correct and this is the first qualifying batch of the day.
    Reset to 1 if user skipped a day.
    """
    if correct < 4:
        return previous_days  # Hold steady, don't reset
    
    # Check if consecutive day
    from datetime import datetime, timedelta
    last = datetime.fromisoformat(last_date)
    current = datetime.fromisoformat(today)
    gap = (current - last).days
    
    if gap == 0:
        # Same day, no increment
        return previous_days
    elif gap == 1:
        # Consecutive day, increment
        return min(30, previous_days + 1)
    else:
        # Skipped day(s), reset
        return 1


def _streak_score(days: int) -> int:
    return 5 + 3 * days


def test_score_and_streak_offline(sqlite_client: SQLiteClient, user_and_session):
    user_ref, _ = user_and_session

    # Case 1: 8/10 correct, avg difficulty 2.0
    score = _compute_score(correct=8, total=10, avg_difficulty=2.0)
    assert score == 62  # 8*(5+2)=56 +10 -4

    # Case 2: 0 correct clamps to 0
    score_zero = _compute_score(correct=0, total=10, avg_difficulty=2.0)
    assert score_zero == 0

    # Streak updates only if >=4 correct
    gamif = sqlite_client.read_table("pine_user_gamification", {"user_ref": user_ref})[0]
    new_streak = _apply_streak(gamif["racha_dias"], correct=6, last_date=gamif["racha_ultima_fecha"], today="2025-01-02")
    sqlite_client.update_record(
        "pine_user_gamification",
        gamif["_id"],
        {"racha_dias": new_streak, "racha_ultima_fecha": "2025-01-02"},
    )

    updated = sqlite_client.read_table("pine_user_gamification", {"user_ref": user_ref})[0]
    assert updated["racha_dias"] == 3
    assert _streak_score(updated["racha_dias"]) == 14

    # Case: Second batch same day (no increment)
    same_day_streak = _apply_streak(updated["racha_dias"], correct=5, last_date="2025-01-02", today="2025-01-02")
    assert same_day_streak == 3

    # Case: Skipped a day (reset to 1)
    skipped = _apply_streak(updated["racha_dias"], correct=5, last_date="2025-01-02", today="2025-01-05")
    assert skipped == 1

    # Case: Cap at 30 days
    sqlite_client.update_record(
        "pine_user_gamification",
        updated["_id"],
        {"racha_dias": 30, "racha_ultima_fecha": "2025-01-10"},
    )
    capped = sqlite_client.read_table("pine_user_gamification", {"user_ref": user_ref})[0]
    assert _apply_streak(capped["racha_dias"], correct=5, last_date="2025-01-10", today="2025-01-11") == 30
    assert _streak_score(30) == 95

    # Case: Less than 4 correct holds steady
    hold = _apply_streak(3, correct=2, last_date="2025-01-03", today="2025-01-04")
    assert hold == 3


def test_record_regular_batch_offline(sqlite_client: SQLiteClient, user_and_session):
    """Test recording a regular batch completion offline"""
    user_ref, _ = user_and_session
    
    # Initial state
    gamif = sqlite_client.read_table("pine_user_gamification", {"user_ref": user_ref})[0]
    operation = sqlite_client.read_table("pine_user_operations", {"user_ref": user_ref, "operacion": "suma"})[0]
    
    initial_pp = gamif["pp_total"]
    initial_batches_since_boss = operation["batches_desde_ultimo_miniboss"]
    
    # Simulate batch completion
    batch_record = {
        "user_ref": user_ref,
        "operacion": "suma",
        "batch_type": "regular",
        "score_ganado": 100,
        "pp_ganados": 10,
        "pd_ganados": 50,
        "xp_ganada": 100,
        "ejercicios_correctos": 8,
        "ejercicios_totales": 10,
        "dificultad_promedio": 2.5,
        "nivel_central": 2,
        "nivel_invisible_antes": 2.5,
        "nivel_invisible_despues": 2.7,
        "fecha_completado": "2025-01-02T10:30:00",
    }
    sqlite_client.insert_records("pine_batches_completados", [batch_record])
    
    # Update operation state
    sqlite_client.update_record(
        "pine_user_operations",
        operation["_id"],
        {
            "nivel_invisible": 2.7,
            "batches_desde_ultimo_miniboss": initial_batches_since_boss + 1,
        },
    )
    
    # Update gamification state
    new_streak = _apply_streak(gamif["racha_dias"], correct=8, last_date=gamif["racha_ultima_fecha"], today="2025-01-02")
    sqlite_client.update_record(
        "pine_user_gamification",
        gamif["_id"],
        {
            "pp_total": initial_pp + 10,
            "pd_global": gamif["pd_global"] + 50,
            "xp_total": gamif["xp_total"] + 100,
            "racha_dias": new_streak,
            "racha_ultima_fecha": "2025-01-02",
        },
    )
    
    # Verify batch record
    batches = sqlite_client.read_table("pine_batches_completados", {"user_ref": user_ref})
    assert len(batches) == 1
    assert batches[0]["score_ganado"] == 100
    assert batches[0]["batch_type"] == "regular"
    
    # Verify operation update
    updated_op = sqlite_client.read_table("pine_user_operations", {"user_ref": user_ref, "operacion": "suma"})[0]
    assert updated_op["nivel_invisible"] == 2.7
    assert updated_op["batches_desde_ultimo_miniboss"] == 2
    
    # Verify gamification update
    updated_gamif = sqlite_client.read_table("pine_user_gamification", {"user_ref": user_ref})[0]
    assert updated_gamif["pp_total"] == 110
    assert updated_gamif["racha_dias"] == 3  # Consecutive day increment


def test_record_miniboss_batch_offline(sqlite_client: SQLiteClient, user_and_session):
    """Test recording a miniboss batch completion offline"""
    user_ref, _ = user_and_session
    
    # Initial state
    operation = sqlite_client.read_table("pine_user_operations", {"user_ref": user_ref, "operacion": "suma"})[0]
    
    # Simulate miniboss completion (success)
    batch_record = {
        "user_ref": user_ref,
        "operacion": "suma",
        "batch_type": "miniboss",
        "score_ganado": 200,
        "pp_ganados": 10,
        "pd_ganados": 0,
        "xp_ganada": 0,
        "ejercicios_correctos": 6,
        "ejercicios_totales": 6,
        "dificultad_promedio": 2.9,
        "nivel_central": 2,
        "nivel_invisible_antes": 2.9,
        "nivel_invisible_despues": 3.0,
        "fecha_completado": "2025-01-03T15:45:00",
    }
    sqlite_client.insert_records("pine_batches_completados", [batch_record])
    
    # Record miniboss attempt
    miniboss_attempt = {
        "user_ref": user_ref,
        "operacion": "suma",
        "nivel_dominio": 2,
        "aprobado": 1,
        "score_obtenido": 200,
        "fecha_intento": "2025-01-03T15:45:00",
    }
    sqlite_client.insert_records("pine_mini_jefes_intentos", [miniboss_attempt])
    
    # Update operation state (level up)
    sqlite_client.update_record(
        "pine_user_operations",
        operation["_id"],
        {
            "nivel_dominio": 3,
            "nivel_invisible": 3.0,
            "batches_desde_ultimo_miniboss": 0,
            "miniboss_completed": 1,
        },
    )
    
    # Verify batch record
    batches = sqlite_client.read_table("pine_batches_completados", {"user_ref": user_ref, "batch_type": "miniboss"})
    assert len(batches) == 1
    assert batches[0]["score_ganado"] == 200
    
    # Verify miniboss attempt
    attempts = sqlite_client.read_table("pine_mini_jefes_intentos", {"user_ref": user_ref})
    assert len(attempts) == 1
    assert attempts[0]["aprobado"] == 1
    assert attempts[0]["nivel_dominio"] == 2
    
    # Verify level up
    updated_op = sqlite_client.read_table("pine_user_operations", {"user_ref": user_ref, "operacion": "suma"})[0]
    assert updated_op["nivel_dominio"] == 3
    assert updated_op["nivel_invisible"] == 3.0
    assert updated_op["batches_desde_ultimo_miniboss"] == 0
    assert updated_op["miniboss_completed"] == 1
