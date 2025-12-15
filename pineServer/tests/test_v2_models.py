"""
Test de Models V2
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pineServer.v2.models import (
    Exercise, ExerciseResult, BatchResult, 
    UserOperationState, UserGamificationState,
    Operacion, TipoRespuesta, BatchType
)


def test_exercise():
    """Test Exercise dataclass"""
    print("\n" + "="*60)
    print("TEST 1: Exercise")
    print("="*60)
    
    ex = Exercise(
        operand_1=5,
        operand_2=3,
        operacion="suma",
        respuesta_correcta=8,
        dificultad=1.5,
        tipo_respuesta="multiple_choice",
        opciones=[6, 7, 8, 9],
        max_tiempo_segundos=30
    )
    
    print(f"✓ Problem: {ex.problem}")
    print(f"✓ Respuesta: {ex.respuesta_correcta}")
    print(f"✓ Dificultad: {ex.dificultad}")
    print(f"✓ Opciones: {ex.opciones}")
    
    ex_dict = ex.to_dict()
    print(f"✓ to_dict keys: {list(ex_dict.keys())}")
    
    assert ex.problem == "5 + 3"
    assert ex_dict["problem"] == "5 + 3"
    
    print("✅ Exercise test PASSED")
    


def test_exercise_result():
    """Test ExerciseResult dataclass"""
    print("\n" + "="*60)
    print("TEST 2: ExerciseResult")
    print("="*60)
    
    ex = Exercise(5, 3, "suma", 8, 1.5, "multiple_choice", [6,7,8,9])
    
    result = ExerciseResult(
        exercise=ex,
        respuesta_usuario=8,
        es_correcto=True,
        tiempo_segundos=2.5,
        fue_retry=False
    )
    
    print(f"✓ Correcto: {result.es_correcto}")
    print(f"✓ Tiempo: {result.tiempo_segundos}s")
    
    result_dict = result.to_dict()
    print(f"✓ to_dict: operand_1={result_dict['operand_1']}, correcto={result_dict['es_correcto']}")
    
    assert result.es_correcto == True
    assert result_dict["respuesta_correcta"] == 8
    
    print("✅ ExerciseResult test PASSED")
    


def test_batch_result():
    """Test BatchResult dataclass"""
    print("\n" + "="*60)
    print("TEST 3: BatchResult")
    print("="*60)
    
    # Crear algunos ejercicios
    exercises = []
    for i in range(10):
        ex = Exercise(i+1, 2, "suma", i+3, 1.5, "multiple_choice")
        is_correct = i < 8  # 8 correctos, 2 incorrectos
        result = ExerciseResult(ex, i+3 if is_correct else 0, is_correct, 2.0)
        exercises.append(result)
    
    batch = BatchResult(
        user_ref="test_user",
        operacion="suma",
        batch_type="regular",
        ejercicios=exercises,
        nivel_central=2,
        nivel_invisible_antes=1.5,
        nivel_invisible_despues=1.7,
        score_ganado=58,
        pp_ganados=10,
        pd_ganados=16
    )
    
    print(f"✓ Total ejercicios: {batch.total_ejercicios}")
    print(f"✓ Correctos: {batch.ejercicios_correctos}")
    print(f"✓ Success rate: {batch.success_rate:.1%}")
    print(f"✓ Dificultad promedio: {batch.dificultad_promedio:.2f}")
    
    assert batch.total_ejercicios == 10
    assert batch.ejercicios_correctos == 8
    assert batch.success_rate == 0.8
    
    batch_dict = batch.to_dict()
    print(f"✓ to_dict keys: {list(batch_dict.keys())[:5]}...")
    
    print("✅ BatchResult test PASSED")
    


def test_user_operation_state():
    """Test UserOperationState dataclass"""
    print("\n" + "="*60)
    print("TEST 4: UserOperationState")
    print("="*60)
    
    # Test from_db_record
    db_record = {
        "user_ref": "user123",
        "operacion": "suma",
        "nivel_dominio": 2,
        "nivel_invisible": 2.3,
        "pd_operacion": 150,
        "unlocked": True,
        "total_ejercicios": 100,
        "total_correctos": 85,
        "batches_desde_ultimo_miniboss": 5
    }
    
    state = UserOperationState.from_db_record(db_record)
    
    print(f"✓ User: {state.user_ref}")
    print(f"✓ Operación: {state.operacion}")
    print(f"✓ Nivel visible: {state.nivel_dominio}")
    print(f"✓ Nivel invisible: {state.nivel_invisible}")
    print(f"✓ Accuracy: {state.accuracy:.1%}")
    print(f"✓ Batches desde miniboss: {state.batches_desde_ultimo_miniboss}")
    
    assert state.nivel_dominio == 2
    assert state.nivel_invisible == 2.3
    assert state.accuracy == 0.85
    
    print("✅ UserOperationState test PASSED")
    


def test_enums():
    """Test Enums"""
    print("\n" + "="*60)
    print("TEST 5: Enums")
    print("="*60)
    
    print(f"✓ Operaciones: {[o.value for o in Operacion]}")
    print(f"✓ TipoRespuesta: {[t.value for t in TipoRespuesta]}")
    print(f"✓ BatchType: {[b.value for b in BatchType]}")
    
    assert Operacion.SUMA.value == "suma"
    assert TipoRespuesta.ABIERTA.value == "abierta"
    assert BatchType.MINIBOSS.value == "miniboss"
    
    print("✅ Enums test PASSED")
    


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "🔍"*30)
    print("  MODELS V2 - TEST SUITE")
    print("🔍"*30)
    
    tests = [
        ("Exercise", test_exercise),
        ("ExerciseResult", test_exercise_result),
        ("BatchResult", test_batch_result),
        ("UserOperationState", test_user_operation_state),
        ("Enums", test_enums),
    ]
    
    results = {}
    for name, func in tests:
        try:
            results[name] = func()
        except Exception as e:
            print(f"❌ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    for name, result in results.items():
        print(f"{'✅' if result else '❌'} {name}")
    
    print(f"\nTotal: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All models working correctly!")
    
    return passed == len(tests)


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
