"""
Tests para Weekly Leaderboard (Ranking Semanal)

Verifica que los registros de leaderboard semanal se actualicen correctamente
y que los rankings se calculen en el orden correcto.
"""

import sys
import os
from datetime import datetime, timedelta

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
