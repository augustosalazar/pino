"""
PerformanceEvaluator - Evaluates performance and adjusts difficulty

Implements IPerformanceEvaluator interface.
"""

from typing import List
from interfaces import IPerformanceEvaluator
from gamification_models import ExerciseResult


class PerformanceEvaluator(IPerformanceEvaluator):
    """
    Evaluates performance and adjusts invisible level based on success rate.
    """
    
    def __init__(self):
        self.min_level = 1.0
        self.max_level = 6.0
        self.high_threshold = 0.8   # >= 80% correct -> increase
        self.low_threshold = 0.4    # < 40% correct -> decrease
        self.increase_step = 0.2
        self.decrease_step = 0.1

    def evaluate_performance(self, resultados: List[ExerciseResult], nivel_invisible_actual: float) -> float:
        """Calculate the new invisible level based on performance."""
        if not resultados:
            return nivel_invisible_actual
            
        total = len(resultados)
        correctos = sum(1 for r in resultados if r.es_correcto)
        success_rate = correctos / total
        
        if success_rate >= self.high_threshold:
            delta = self.increase_step
        elif success_rate < self.low_threshold:
            delta = -self.decrease_step
        else:
            delta = 0.0
        
        nuevo = nivel_invisible_actual + delta
        return max(self.min_level, min(nuevo, self.max_level))


# Singleton accessor (backward compatibility)
_instance = None

def get_performance_evaluator():
    global _instance
    if _instance is None:
        _instance = PerformanceEvaluator()
    return _instance
