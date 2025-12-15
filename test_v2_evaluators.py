"""
Tests para Evaluadores V2 (Performance, Scoring, Level)
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pineServer.v2.performance_evaluator import get_performance_evaluator
from pineServer.v2.scoring_calculator import get_scoring_calculator
from pineServer.v2.dominio_level_manager import get_dominio_level_manager
from pineServer.v2.models import ExerciseResult, Exercise

def test_performance_evaluator():
    print("\n" + "="*60)
    print("TEST 1: Performance Evaluator")
    print("="*60)
    
    evaluator = get_performance_evaluator()
    
    # Mock results
    def create_results(correct_count):
        results = []
        for i in range(10):
            ex = Exercise(1, 1, "suma", 2, 2.0, "mc")
            res = ExerciseResult(ex, 2 if i < correct_count else 0, i < correct_count, 1.0)
            results.append(res)
        return results
        
    # Caso 1: Alto rendimiento (10/10) -> Sube 0.2
    res_high = create_results(10)
    new_lvl = evaluator.evaluate_performance(res_high, 2.0)
    print(f"High perf (10/10) from 2.0 -> {new_lvl}")
    assert new_lvl == 2.2 # 2.0 + 0.2
    
    # Caso 2: Bajo rendimiento (2/10) -> Baja 0.1
    res_low = create_results(2)
    new_lvl = evaluator.evaluate_performance(res_low, 2.0)
    print(f"Low perf (2/10) from 2.0 -> {new_lvl}")
    assert new_lvl == 1.9 # 2.0 - 0.1
    
    # Caso 3: Medio rendimiento (5/10) -> Mantiene
    res_mid = create_results(5)
    new_lvl = evaluator.evaluate_performance(res_mid, 2.0)
    print(f"Mid perf (5/10) from 2.0 -> {new_lvl}")
    assert new_lvl == 2.0
    
    # Caso 4: Límites
    new_lvl_max = evaluator.evaluate_performance(res_high, 6.0)
    print(f"Max limit check from 6.0 -> {new_lvl_max}")
    assert new_lvl_max == 6.0
    
    print("✅ Performance Evaluator passed")

def test_scoring_calculator():
    print("\n" + "="*60)
    print("TEST 2: Scoring Calculator")
    print("="*60)
    
    calc = get_scoring_calculator()
    
    # Config default:
    # Base Mult: 5
    # Bonus: 10
    # Penalty: 2
    
    # Caso 1: Perfecto (10/10), Diff promedio 2.0
    # Score = 10 * (5 + 2.0) + 10 - 0 = 70 + 10 = 80
    exercises = []
    for _ in range(10):
        ex = Exercise(1, 1, "suma", 2, 2.0, "mc")
        exercises.append(ExerciseResult(ex, 2, True, 1.0))
        
    score = calc.calculate_score(exercises)
    parts = calc.calculate_score_parts(exercises)
    print(f"Perfect Score (Diff 2.0): {score}")
    print(f"  Parts: {parts}")
    assert score == 80
    assert parts["base"] == 70
    assert parts["bonus"] == 10
    assert parts["penalty"] == 0
    
    # Caso 2: 5 Correctos, 5 Errores, Diff 2.0
    # Score = 5 * (5 + 2.0) + 10 - (5 * 2) 
    #       = 35 + 10 - 10 = 35
    exercises_mixed = []
    for i in range(10):
        ex = Exercise(1, 1, "suma", 2, 2.0, "mc")
        is_correct = i < 5
        exercises_mixed.append(ExerciseResult(ex, 2 if is_correct else 0, is_correct, 1.0))
        
    score_mixed = calc.calculate_score(exercises_mixed)
    print(f"Mixed Score (5/10): {score_mixed}")
    assert score_mixed == 35
    
    # Caso 3: 0 Correctos -> Mínimo 0
    # Score = 0 * (7) + 10 - (10*2) = 10 - 20 = -10 -> Clamped to 0
    exercises_fail = []
    for i in range(10):
        ex = Exercise(1, 1, "suma", 2, 2.0, "mc")
        exercises_fail.append(ExerciseResult(ex, 0, False, 1.0))
        
    score_fail = calc.calculate_score(exercises_fail)
    print(f"Fail Score (0/10): {score_fail}")
    assert score_fail == 0
    
    # Test PP
    pp = calc.calculate_pp(exercises)
    print(f"PP calculated: {pp}")
    assert pp == 10
    
    print("✅ Scoring Calculator passed")

def test_level_manager():
    print("\n" + "="*60)
    print("TEST 3: Level Manager")
    print("="*60)
    
    mgr = get_dominio_level_manager()
    
    # Mapeo
    print(f"1.5 -> Level {mgr.get_nivel_dominio_teorico(1.5)}")
    assert mgr.get_nivel_dominio_teorico(1.5) == 1
    
    print(f"2.9 -> Level {mgr.get_nivel_dominio_teorico(2.9)}")
    assert mgr.get_nivel_dominio_teorico(2.9) == 2
    
    print(f"5.5 -> Level {mgr.get_nivel_dominio_teorico(5.5)}")
    assert mgr.get_nivel_dominio_teorico(5.5) == 5
    
    # Detección de cambio
    # Actual 1, invisible sube a 2.1 (teórico 2) -> Detecta cambio
    change = mgr.detect_potential_level_change(1, 2.1)
    print(f"Detect change (1 -> 2.1): {change}")
    assert change == 2
    
    # Actual 2, invisible 2.9 (teórico 2) -> No cambio
    change_none = mgr.detect_potential_level_change(2, 2.9)
    print(f"Detect change (2 -> 2.9): {change_none}")
    assert change_none is None
    
    print("✅ Level Manager passed")
    

def run_all_tests():
    tests = [
        test_performance_evaluator,
        test_scoring_calculator,
        test_level_manager
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
