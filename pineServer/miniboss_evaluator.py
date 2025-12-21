"""
MinibossEvaluator - Evaluates miniboss results

Implements IMinibossEvaluator interface.
"""

from typing import List
from interfaces import IMinibossEvaluator
from gamification_models import ExerciseResult


class MinibossEvaluator(IMinibossEvaluator):
    """
    Evaluates miniboss pass/fail based on correct rate.
    """
    
    def __init__(self, container=None):
        self._container = container
    
    @property
    def config_manager(self):
        if self._container:
            return self._container.config_manager
        from config_manager import get_config_manager
        return get_config_manager()
        
    def evaluate_miniboss(self, resultados: List[ExerciseResult]) -> bool:
        """Determine if miniboss was passed (True = level up)."""
        if not resultados:
            return False
            
        min_rate = self.config_manager.get_miniboss_config().get("min_correct_rate", 0.8)
        
        total = len(resultados)
        correctos = sum(1 for r in resultados if r.es_correcto)
        rate = correctos / total
        
        passed = rate >= min_rate
        status = "PASSED" if passed else "FAILED"
        print(f"[Miniboss] {status}: {correctos}/{total} ({rate:.1%}) vs {min_rate:.1%}")
        
        return passed


# Singleton accessor (backward compatibility)
_instance = None

def get_miniboss_evaluator():
    global _instance
    if _instance is None:
        _instance = MinibossEvaluator()
    return _instance
