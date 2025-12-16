"""
Tests para Weekly Leaderboard (Ranking Semanal)

Verifica que los registros de leaderboard semanal se actualicen correctamente
y que los rankings se calculen en el orden correcto.
"""

import sys
import os
from datetime import datetime, timedelta, date

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pineServer.v2.batch_recorder import BatchRecorder
from pineServer.v2.models import BatchResult, Exercise, ExerciseResult, UserGamificationState, BatchType


def test_generate_semana_id():
    """Test generation of week ID in format YYYY-W##"""
    recorder = BatchRecorder()
    
    # Test known date: 2025-01-15 (Wednesday in week 3)
    fecha = datetime(2025, 1, 15)
    semana_id = recorder._generate_semana_id(fecha)
    
    # Week 3 of 2025
    assert semana_id == "2025-W03", f"Expected '2025-W03', got '{semana_id}'"
    
    # Test start of year: 2025-01-01 (Wednesday in week 1)
    fecha_inicio = datetime(2025, 1, 1)
    semana_id_inicio = recorder._generate_semana_id(fecha_inicio)
    assert semana_id_inicio == "2025-W01"


def test_get_week_dates():
    """Test calculation of week start (Monday) and end (Sunday)"""
    recorder = BatchRecorder()
    
    # 2025-01-15 is a Wednesday
    reference = datetime(2025, 1, 15).date()
    fecha_inicio, fecha_fin = recorder._get_week_dates(reference)
    
    # Should be Monday 2025-01-13 to Sunday 2025-01-19
    assert fecha_inicio.date().isoformat() == "2025-01-13", f"Expected Monday 2025-01-13, got {fecha_inicio.date()}"
    assert fecha_fin.date().isoformat() == "2025-01-19", f"Expected Sunday 2025-01-19, got {fecha_fin.date()}"


def test_week_boundaries():
    """Test week boundaries for different days of the week"""
    recorder = BatchRecorder()
    
    # Test each day of the week
    test_cases = [
        ("2025-01-13", "2025-01-13", "2025-01-19"),  # Monday
        ("2025-01-14", "2025-01-13", "2025-01-19"),  # Tuesday
        ("2025-01-15", "2025-01-13", "2025-01-19"),  # Wednesday
        ("2025-01-16", "2025-01-13", "2025-01-19"),  # Thursday
        ("2025-01-17", "2025-01-13", "2025-01-19"),  # Friday
        ("2025-01-18", "2025-01-13", "2025-01-19"),  # Saturday
        ("2025-01-19", "2025-01-13", "2025-01-19"),  # Sunday
    ]
    
    for test_date_str, expected_monday, expected_sunday in test_cases:
        test_date = datetime.strptime(test_date_str, "%Y-%m-%d").date()
        fecha_inicio, fecha_fin = recorder._get_week_dates(test_date)
        
        assert fecha_inicio.date().isoformat() == expected_monday, \
            f"For {test_date_str}: Expected Monday {expected_monday}, got {fecha_inicio.date()}"
        assert fecha_fin.date().isoformat() == expected_sunday, \
            f"For {test_date_str}: Expected Sunday {expected_sunday}, got {fecha_fin.date()}"


def test_multiple_weeks():
    """Test that different weeks generate different semana_ids"""
    recorder = BatchRecorder()
    
    week1 = recorder._generate_semana_id(datetime(2025, 1, 13))  # Week 1
    week2 = recorder._generate_semana_id(datetime(2025, 1, 20))  # Week 2
    week3 = recorder._generate_semana_id(datetime(2025, 1, 27))  # Week 3
    
    assert week1 == "2025-W03"
    assert week2 == "2025-W04"
    assert week3 == "2025-W05"
    
    # All should be different
    assert len({week1, week2, week3}) == 3


def test_batch_result_accumulation():
    """Test that multiple batches in same week accumulate PP/PD/score"""
    # This is a logic test - in production it would hit Roble
    # Here we just verify the data structure is correct
    
    result1 = BatchResult(
        user_ref="test_user",
        operacion="suma",
        batch_type=BatchType.REGULAR,
        ejercicios=[ExerciseResult(Exercise(1, 1, "suma", 1, 1.0, "mc"), 1, True, 1.0)],
        nivel_central=1,
        nivel_invisible_antes=1.0,
        nivel_invisible_despues=1.0,
        score_ganado=50,
        pp_ganados=5,
        pd_ganados=10,
        xp_ganada=20,
    )
    
    result2 = BatchResult(
        user_ref="test_user",
        operacion="suma",
        batch_type=BatchType.REGULAR,
        ejercicios=[ExerciseResult(Exercise(1, 1, "suma", 1, 1.0, "mc"), 1, True, 1.0)],
        nivel_central=1,
        nivel_invisible_antes=1.0,
        nivel_invisible_despues=1.0,
        score_ganado=60,
        pp_ganados=6,
        pd_ganados=15,
        xp_ganada=25,
    )
    
    # Simulate accumulation (what would happen in weekly leaderboard)
    accumulated = {
        "pp_semana": result1.pp_ganados + result2.pp_ganados,
        "pd_semana": result1.pd_ganados + result2.pd_ganados,
        "score_semanal": result1.score_ganado + result2.score_ganado,
    }
    
    assert accumulated["pp_semana"] == 11
    assert accumulated["pd_semana"] == 25
    assert accumulated["score_semanal"] == 110


# ============ ENDLESS MONTHLY LEADERBOARD TESTS ============

def test_generate_mes_id():
    """Test generation of month ID in format YYYY-MM"""
    recorder = BatchRecorder()
    
    # Test known date: 2025-01-15
    fecha = date(2025, 1, 15)
    mes_id = recorder._generate_mes_id(fecha)
    
    assert mes_id == "2025-01", f"Expected '2025-01', got '{mes_id}'"
    
    # Test different months
    fecha_feb = date(2025, 2, 1)
    mes_id_feb = recorder._generate_mes_id(fecha_feb)
    assert mes_id_feb == "2025-02"
    
    fecha_dic = date(2024, 12, 31)
    mes_id_dic = recorder._generate_mes_id(fecha_dic)
    assert mes_id_dic == "2024-12"


def test_get_month_dates():
    """Test calculation of month start and end dates"""
    recorder = BatchRecorder()
    
    # January 2025
    reference = date(2025, 1, 15)
    fecha_inicio, fecha_fin = recorder._get_month_dates(reference)
    
    assert fecha_inicio == date(2025, 1, 1)
    assert fecha_fin == date(2025, 1, 31)
    
    # February 2025 (non-leap year)
    reference_feb = date(2025, 2, 14)
    fecha_inicio_feb, fecha_fin_feb = recorder._get_month_dates(reference_feb)
    
    assert fecha_inicio_feb == date(2025, 2, 1)
    assert fecha_fin_feb == date(2025, 2, 28)
    
    # December 2024
    reference_dic = date(2024, 12, 25)
    fecha_inicio_dic, fecha_fin_dic = recorder._get_month_dates(reference_dic)
    
    assert fecha_inicio_dic == date(2024, 12, 1)
    assert fecha_fin_dic == date(2024, 12, 31)


def test_endless_batch_with_streak():
    """Test endless batch result with streak information"""
    result = BatchResult(
        user_ref="endless_player",
        operacion="suma",
        batch_type=BatchType.ENDLESS,
        ejercicios=[ExerciseResult(Exercise(1, 1, "suma", 1, 1.0, "mc"), 1, True, 1.0) for _ in range(5)],
        nivel_central=1,
        nivel_invisible_antes=1.0,
        nivel_invisible_despues=1.0,
        score_ganado=100,
        pp_ganados=0,  # Endless no afecta progresion
        pd_ganados=0,
        xp_ganada=0,
        endless_streak=15,  # 15 ejercicios consecutivos correctos
    )
    
    assert result.batch_type == BatchType.ENDLESS
    assert result.endless_streak == 15
    # Endless no debe afectar estos
    assert result.pp_ganados == 0
    assert result.pd_ganados == 0


def test_monthly_dates_consistency():
    """Test that all days in a month have same month ID"""
    recorder = BatchRecorder()
    
    # All days in January 2025 should have same mes_id
    month_ids = set()
    for day in range(1, 32):  # January has 31 days
        fecha = date(2025, 1, day)
        mes_id = recorder._generate_mes_id(fecha)
        month_ids.add(mes_id)
    
    assert len(month_ids) == 1
    assert "2025-01" in month_ids
    
    # February 2025 should be different
    mes_id_feb = recorder._generate_mes_id(date(2025, 2, 15))
    assert mes_id_feb == "2025-02"


def test_endless_streak_comparison():
    """Test that endless streaks are correctly compared"""
    # Simulate monthly leaderboard calculation
    users = [
        {"user_ref": "user1", "mejor_streak": 15, "total_intentos": 3},
        {"user_ref": "user2", "mejor_streak": 25, "total_intentos": 2},
        {"user_ref": "user3", "mejor_streak": 25, "total_intentos": 5},
        {"user_ref": "user4", "mejor_streak": 10, "total_intentos": 10},
    ]
    
    # Sort by mejor_streak (desc) then total_intentos (desc)
    sorted_users = sorted(
        users,
        key=lambda x: (x["mejor_streak"], x["total_intentos"]),
        reverse=True
    )
    
    # Expected ranking: user3 (25, 5), user2 (25, 2), user1 (15), user4 (10)
    assert sorted_users[0]["user_ref"] == "user3"  # Best streak (25) + most attempts (5)
    assert sorted_users[1]["user_ref"] == "user2"  # Same streak (25) but fewer attempts (2)
    assert sorted_users[2]["user_ref"] == "user1"  # Lower streak (15)
    assert sorted_users[3]["user_ref"] == "user4"  # Lowest streak (10)
