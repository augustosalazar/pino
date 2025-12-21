"""
DefaultPerformanceEvaluator - Default implementation of IPerformanceEvaluator

Evaluates user performance and adjusts difficulty dynamically.
"""

from typing import List
from v2.interfaces import IPerformanceEvaluator
from v2.models import ExerciseResult


class DefaultPerformanceEvaluator(IPerformanceEvaluator):
    """
    Default performance evaluator that adjusts invisible level based on success rate.
    """
    
    def __init__(self):
        # Configuration for adjustment rules
        self.min_level = 1.0
        self.max_level = 6.0
        self.high_threshold = 0.8   # >= 80% correct
        self.low_threshold = 0.4    # < 40% correct
        
        self.increase_step = 0.2
        self.decrease_step = 0.1
        self.neutral_step = 0.0

    def evaluate_performance(
        self,
        resultados: List[ExerciseResult],
        nivel_invisible_actual: float
    ) -> float:
        """
        Calculate the new invisible level.
        
        Args:
            resultados: List of batch results
            nivel_invisible_actual: Current level before the batch
            
        Returns:
            New invisible level (clamped between min and max)
        """
        if not resultados:
            return nivel_invisible_actual
            
        total = len(resultados)
        correctos = sum(1 for r in resultados if r.es_correcto)
        success_rate = correctos / total
        
        delta = self._calculate_delta(success_rate)
        
        nuevo_nivel = nivel_invisible_actual + delta
        
        # Safe clamp
        return max(self.min_level, min(nuevo_nivel, self.max_level))
        
    def _calculate_delta(self, success_rate: float) -> float:
        """Determine level change based on success rate."""
        if success_rate >= self.high_threshold:
            # High performance -> Increase difficulty
            return self.increase_step
        elif success_rate < self.low_threshold:
            # Low performance -> Decrease difficulty
            return -self.decrease_step
        else:
            # Middle zone (40% - 79%) -> Maintain difficulty
            return self.neutral_step
