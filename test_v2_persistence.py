"""
Tests para Batch Recorder V2 (Integración)

Verifica que los datos se guardan y actualizan correctamente en la BD.
Usa un usuario de prueba 'test_persist_user'.
"""

import sys
import os
import time
from datetime import datetime
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pineServer.v2.batch_recorder import get_batch_recorder
from pineServer.v2.models import BatchResult, ExerciseResult, Exercise, UserGamificationState, BatchType
from pineServer.roble_client import roble_client

USER_REF = "test_persist_user_v2"


@pytest.fixture(autouse=True, scope="module")
def _ensure_seed_data():
    """Seed test data before each module run to avoid missing records."""
    setup_test_data()

def setup_test_data():
    """Limpia datos anteriores del usuario de prueba"""
    print(f"Cleaning data for {USER_REF}...")
    
    # Tables to clean
    tables = [
        "pine_batches_completados",
        "pine_user_operations", 
        "pine_user_gamification",
        "pine_mini_jefes_intentos"
    ]
    
    for table in tables:
        records = roble_client.read_table(table, {"user_ref": USER_REF})
        for r in records:
            roble_client._delete_record(table, r["_id"])
            
    # Create initial gamification state
    roble_client.insert_records("pine_user_gamification", [{
        "user_ref": USER_REF,
        "pp_total": 100,
        "pd_global": 500,
        "xp_total": 1000,
        "racha_dias": 5,
        "racha_ultima_fecha": "2024-01-01" # Fecha vieja para probar update
    }])
    
    # Create initial operation state
    roble_client.insert_records("pine_user_operations", [{
        "user_ref": USER_REF,
        "operacion": "suma",
        "nivel_dominio": 2,
        "nivel_invisible": 2.5,
        "batches_desde_ultimo_miniboss": 1
    }])
    # Give the backend a moment to persist before test reads
    time.sleep(0.5)

    gamif = roble_client.read_table("pine_user_gamification", {"user_ref": USER_REF})
    ops = roble_client.read_table("pine_user_operations", {"user_ref": USER_REF, "operacion": "suma"})
    if not gamif or not ops:
        pytest.skip("Seed data not available in Roble (check credentials/connectivity).")

    print("Setup complete.")

def test_record_regular_batch():
    print("\n" + "="*60)
    print("TEST 1: Record Regular Batch")
    print("="*60)
    
    recorder = get_batch_recorder()
    
    # 1. Crear BatchResult Mock
    exercises = []
    for i in range(10):
        ex = Exercise(1, 1, "suma", 2, 2.0, "mc")
        exercises.append(ExerciseResult(ex, 2, True, 1.0))
        
    result = BatchResult(
        user_ref=USER_REF,
        operacion="suma",
        batch_type=BatchType.REGULAR,
        ejercicios=exercises,
        nivel_central=2,
        nivel_invisible_antes=2.5,
        nivel_invisible_despues=2.7, # Subió nivel invisible
        score_ganado=100,
        pp_ganados=10,
        pd_ganados=50,
        xp_ganada=100
    )
    
    # 2. Get current gamif state (mocked or read)
    # Leemos de BD para ser realistas
    gamif_records = roble_client.read_table("pine_user_gamification", {"user_ref": USER_REF})
    if not gamif_records:
        setup_test_data()
        gamif_records = roble_client.read_table("pine_user_gamification", {"user_ref": USER_REF})
    if not gamif_records:
        pytest.skip("Seed gamification record missing; cannot validate persistence.")

    gamif_rec = gamif_records[0]
    current_gamif = UserGamificationState.from_db_record(gamif_rec)
    
    # 3. Record
    success = recorder.record_batch(result, current_gamif)
    print(f"Record success: {success}")
    assert success
    
    # 4. Verify DB updates
    
    # Check Batch Log
    batches = roble_client.read_table("pine_batches_completados", {"user_ref": USER_REF})
    print(f"Batches found: {len(batches)}")
    assert len(batches) == 1
    assert batches[0]["score_ganado"] == 100
    
    # Check Operation Update
    ops = roble_client.read_table("pine_user_operations", {"user_ref": USER_REF, "operacion": "suma"})
    op = ops[0]
    print(f"New invisible level: {op['nivel_invisible']}")
    print(f"Batches since boss: {op['batches_desde_ultimo_miniboss']}")
    
    assert op['nivel_invisible'] == 2.7
    assert op['batches_desde_ultimo_miniboss'] == 2 # 1 inicial + 1
    
    # Check Gamification Update
    gamif = roble_client.read_table("pine_user_gamification", {"user_ref": USER_REF})[0]
    print(f"New PP Total: {gamif['pp_total']}")
    print(f"New Streak: {gamif['racha_dias']}")
    
    assert gamif['pp_total'] == 110 # 100 + 10
    # Streak logic: Fecha vieja -> Hoy = Streak + 1 ? Depende si es consecutivo.
    # En el setup pusimos 2024-01-01. Hoy es 2025. NO es consecutivo.
    # Logic: Si no es ayer ni hoy -> Reset a 1.
    assert gamif['racha_dias'] == 1 
    
    print("✅ Regular Batch Recording passed")
    

def test_record_miniboss_batch():
    print("\n" + "="*60)
    print("TEST 2: Record Miniboss Batch (Success)")
    print("="*60)
    
    recorder = get_batch_recorder()
    
    # Simulamos que aprobó miniboss para subir a nivel 3
    exercises = [] # dummy
    
    result = BatchResult(
        user_ref=USER_REF,
        operacion="suma",
        batch_type=BatchType.MINIBOSS,
        ejercicios=exercises,
        nivel_central=2,
        nivel_invisible_antes=2.9,
        nivel_invisible_despues=3.0,
        score_ganado=200,
        miniboss_aprobado=True,
        pp_ganados=10
    )
    
    gamif_records = roble_client.read_table("pine_user_gamification", {"user_ref": USER_REF})
    if not gamif_records:
        setup_test_data()
        gamif_records = roble_client.read_table("pine_user_gamification", {"user_ref": USER_REF})
    if not gamif_records:
        pytest.skip("Seed gamification record missing; cannot validate persistence.")

    gamif_rec = gamif_records[0]
    current_gamif = UserGamificationState.from_db_record(gamif_rec)
    
    success = recorder.record_batch(result, current_gamif)
    assert success
    
    # Verify Miniboss Log
    attempts = roble_client.read_table("pine_mini_jefes_intentos", {"user_ref": USER_REF})
    print(f"Miniboss attempts: {len(attempts)}")
    assert len(attempts) >= 1
    assert attempts[0]['aprobado'] == True
    
    # Verify Level Up
    ops = roble_client.read_table("pine_user_operations", {"user_ref": USER_REF})[0]
    print(f"New Domain Level: {ops['nivel_dominio']}")
    assert ops['nivel_dominio'] == 3 # Subió de 2 a 3
    assert ops['batches_desde_ultimo_miniboss'] == 0 # Reset
    assert ops['miniboss_completed'] == True
    
    print("✅ Miniboss Recording passed")
    

def run_all_tests():
    try:
        setup_test_data()
        
        tests = [
            test_record_regular_batch,
            test_record_miniboss_batch
        ]
        
        passed = 0
        for test in tests:
            try:
                test()
                passed += 1
            except Exception as e:
                print(f"\n❌ Test failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*60)
        print(f"Summary: {passed}/{len(tests)} tests passed")
        
        # Cleanup? 
        # setup_test_data() # Uncomment to clean after
        
        return passed == len(tests)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
