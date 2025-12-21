"""
DefaultMinibossEvaluator - Default implementation of IMinibossEvaluator

Evaluates miniboss results to determine pass/fail.
"""

from typing import List
from v2.interfaces import IMinibossEvaluator, IConfigManager
from v2.models import ExerciseResult


class DefaultMinibossEvaluator(IMinibossEvaluator):
    """
    Default miniboss evaluator that checks correct rate against threshold.
    """
    
    def __init__(self, container=None):
        self._container = container
    
    @property
    def config_manager(self) -> IConfigManager:
        from v2.container import get_v2_container
        if self._container:
            return self._container.config_manager
        return get_v2_container().config_manager
        
    def evaluate_miniboss(self, resultados: List[ExerciseResult]) -> bool:
        """
        Determine if the miniboss was passed.
        
        Args:
            resultados: List of miniboss exercise results
            
        Returns:
            True if passed (level up), False if failed
        """
        if not resultados:
            return False
            
        mb_config = self.config_manager.get_miniboss_config()
        min_rate = mb_config.get("min_correct_rate", 0.8)  # 80% default
        
        total = len(resultados)
        correctos = sum(1 for r in resultados if r.es_correcto)
        rate = correctos / total
        
        passed = rate >= min_rate
        
        if passed:
            print(f"[Miniboss] PASSED: {correctos}/{total} ({rate:.1%}) >= {min_rate:.1%}")
        else:
            print(f"[Miniboss] FAILED: {correctos}/{total} ({rate:.1%}) < {min_rate:.1%}")
            
        return passed
