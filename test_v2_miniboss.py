"""
Tests para Sistema Miniboss V2
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pineServer.v2.miniboss_detector import get_miniboss_detector
from pineServer.v2.miniboss_evaluator import get_miniboss_evaluator
from pineServer.v2.models import UserOperationState, ExerciseResult, Exercise

def test_miniboss_detector():
    print("\n" + "="*60)
    print("TEST 1: Miniboss Detector")
    print("="*60)
    
    detector = get_miniboss_detector()
    
    # Caso 1: Usuario nuevo (Nivel 1, Invisible 1.0) -> False
    state_new = UserOperationState(
        user_ref="u1", operacion="suma", 
        nivel_dominio=1, nivel_invisible=1.0,
        batches_desde_ultimo_miniboss=5
    )
    is_cand = detector.is_miniboss_candidate(state_new)
    print(f"New user (1.0 vs 1): {is_cand}")
    assert not is_cand
    
    # Caso 2: Listo para subir (Nivel 1, Invisible 1.8) -> True
    # Threshold default es 0.5, 1.8 >= 1.5 -> True
    state_ready = UserOperationState(
        user_ref="u1", operacion="suma",
        nivel_dominio=1, nivel_invisible=1.8,
        batches_desde_ultimo_miniboss=5
    )
    is_cand_ready = detector.is_miniboss_candidate(state_ready)
    print(f"Ready user (1.8 vs 1): {is_cand_ready}")
    assert is_cand_ready
    
    # Caso 3: Listo pero cooldown (Batches < 3) -> False
    state_cooldown = UserOperationState(
        user_ref="u1", operacion="suma",
        nivel_dominio=1, nivel_invisible=1.8,
        batches_desde_ultimo_miniboss=1 # Insuficiente
    )
    is_cand_cd = detector.is_miniboss_candidate(state_cooldown)
    print(f"Cooldown user (batches=1): {is_cand_cd}")
    assert not is_cand_cd
    
    print("✅ Miniboss Detector passed")
    

def test_miniboss_evaluator():
    print("\n" + "="*60)
    print("TEST 2: Miniboss Evaluator")
    print("="*60)
    
    evaluator = get_miniboss_evaluator()
    
    # Mock results helper
    def create_mb_results(correct_count):
        res = []
        for _ in range(10):
            ex = Exercise(1,1,"suma",2,2.0,"abierta")
            res.append(ExerciseResult(ex, 0, len(res) < correct_count, 1.0))
        return res
        
    # Caso 1: Aprobado (8/10) -> True
    res_pass = create_mb_results(8)
    passed_8 = evaluator.evaluate_miniboss(res_pass)
    print(f"Score 8/10: {passed_8}")
    assert passed_8
    
    # Caso 2: Fallado (7/10) -> False
    res_fail = create_mb_results(7)
    passed_7 = evaluator.evaluate_miniboss(res_fail)
    print(f"Score 7/10: {passed_7}")
    assert not passed_7
    
    print("✅ Miniboss Evaluator passed")
    

def run_all_tests():
    tests = [
        test_miniboss_detector,
        test_miniboss_evaluator
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
