"""
Tests para Generadores V2 (Exercise y Batch)
"""

import sys
import os
import math
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pineServer.v2.exercise_generator import get_exercise_generator
from pineServer.v2.batch_generator import get_batch_generator
from pineServer.v2.models import BatchType, Operacion, TipoRespuesta
from pineServer.v2.config_manager import get_config_manager

def test_exercise_generator_interpolation():
    """Verifica que la dificultad se interpola correctamente"""
    print("\n" + "="*60)
    print("TEST 1: Exercise Interpolation")
    print("="*60)
    
    gen = get_exercise_generator()
    config_mgr = get_config_manager()
    
    # Caso 1: Nivel entero (exacto)
    print(">>> Probando Nivel 1.0 (Exacto)")
    ex1 = gen.generate_exercise("suma", 1.0)
    conf1 = config_mgr.get_difficulty_config("suma", 1)
    
    # Skip if difficulty configurations are not available (Roble DB not connected)
    if conf1 is None:
        pytest.skip("Difficulty configurations not available (Roble DB required)")
    
    print(f"Problem: {ex1.problem} = {ex1.respuesta_correcta}")
    print(f"Range: [{conf1['min_operando_1']}-{conf1['max_operando_1']}]")
    
    assert conf1['min_operando_1'] <= ex1.operand_1 <= conf1['max_operando_1']
    assert ex1.dificultad == 1.0

    # Caso 2: Nivel medio (Interpolado)
    print("\n>>> Probando Nivel 1.5 (Interpolado)")
    # Nivel 1: [0-10], Nivel 2: [10-50] (hipotético, depende de config real)
    # 1.5 debería dar rango aprox [5-30]
    
    for _ in range(5):
        ex = gen.generate_exercise("suma", 1.5)
        print(f"Lvl 1.5 -> {ex.problem}")
        
    print("✅ Interpolation logic executed without errors")
    

def test_operations_logic():
    """Verifica lógica específica de cada operación"""
    print("\n" + "="*60)
    print("TEST 2: Operations Logic")
    print("="*60)
    
    gen = get_exercise_generator()
    
    # RESTA (No negativos)
    print(">>> Checking Resta (non-negative)")
    for _ in range(10):
        ex = gen.generate_exercise("resta", 2.0)
        assert ex.respuesta_correcta >= 0, f"Resta gave negative: {ex.problem} = {ex.respuesta_correcta}"
        
    # DIV (Exacta)
    print(">>> Checking Div (exact)")
    for _ in range(10):
        ex = gen.generate_exercise("div", 2.0)
        assert ex.respuesta_correcta.is_integer(), f"Div not integer: {ex.problem} = {ex.respuesta_correcta}"
        # Verificar que operando 1 es op2 * respuesta
        assert ex.operand_1 == ex.operand_2 * ex.respuesta_correcta
        
    print("✅ Operations logic valid")
    

def test_batch_distribution():
    """Verifica la distribución 2-6-2 del batch regular"""
    print("\n" + "="*60)
    print("TEST 3: Batch Distribution 2-6-2")
    print("="*60)
    
    batch_gen = get_batch_generator()
    central_level = 2.0
    
    batch = batch_gen.generate_batch("suma", operacion="suma", nivel_invisible=central_level, batch_type=BatchType.REGULAR)
    
    print(f"Batch size: {len(batch)}")
    assert len(batch) == 10
    
    # Check difficulties
    diffs = [ex.dificultad for ex in batch]
    print(f"Difficulties: {diffs}")
    
    # First 2 should be easy (<= 1.5)
    assert diffs[0] <= 1.5 and diffs[1] <= 1.5, "First 2 should be easier"
    
    # Middle 6 should be central (2.0)
    # Note: float comparison
    assert all(d == 2.0 for d in diffs[2:8]), "Middle 6 should be central level"
    
    # Last 2 should be hard (>= 2.5)
    assert diffs[8] >= 2.5 and diffs[9] >= 2.5, "Last 2 should be harder"
    
    print("✅ 2-6-2 Distribution valid")
    

def test_miniboss_batch():
    """Verifica batch de miniboss (todo abierta)"""
    print("\n" + "="*60)
    print("TEST 4: Miniboss Batch")
    print("="*60)
    
    batch_gen = get_batch_generator()
    
    batch = batch_gen.generate_batch("mult", "mult", 3.0, batch_type=BatchType.MINIBOSS)
    
    print(f"Batch size: {len(batch)}")
    
    open_count = sum(1 for ex in batch if ex.tipo_respuesta == TipoRespuesta.ABIERTA)
    print(f"Open answers: {open_count}/{len(batch)}")
    
    assert open_count == 10, "All miniboss exercises must be open answer"
    assert all(ex.opciones is None for ex in batch), "Miniboss should have no options"
    
    print("✅ Miniboss batch valid")
    

def run_all_tests():
    tests = [
        test_exercise_generator_interpolation,
        test_operations_logic,
        test_batch_distribution,
        test_miniboss_batch
    ]
    
    passed = 0
    for test in tests:
        try:
            if test(): passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test.__name__}")
            print(e)
            import traceback
            traceback.print_exc()
            
    print("\n" + "="*60)
    print(f"Summary: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
