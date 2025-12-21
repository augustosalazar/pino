"""
ScoringCalculator - Calculates scores and rewards

Implements IScoringCalculator interface.
"""

from typing import List, Dict
from interfaces import IScoringCalculator
from gamification_models import ExerciseResult


class ScoringCalculator(IScoringCalculator):
    """
    Calculates PP, PD, XP, and total score.
    """
    
    def __init__(self, container=None):
        self._container = container
    
    @property
    def config_manager(self):
        if self._container:
            return self._container.config_manager
        from config_manager import get_config_manager
        return get_config_manager()
        
    def calculate_score_parts(self, resultados: List[ExerciseResult]) -> Dict[str, int]:
        """Calculate score breakdown: total, base, bonus, penalty."""
        if not resultados:
            return {"total": 0, "base": 0, "bonus": 0, "penalty": 0}
            
        config = self.config_manager.get_scoring_config()
        base_mult = config["base_multiplier"]
        bonus = config["participation_bonus"]
        penalty_rate = config["error_penalty"]
        
        correctos = sum(1 for r in resultados if r.es_correcto)
        errores = len(resultados) - correctos
        avg_diff = sum(r.exercise.dificultad for r in resultados) / len(resultados)
        
        base = int(round(correctos * (base_mult + avg_diff)))
        penalty = errores * penalty_rate
        total = max(0, base + bonus - penalty)
        
        return {"total": total, "base": base, "bonus": bonus, "penalty": penalty}

    def calculate_score(self, resultados: List[ExerciseResult]) -> int:
        return self.calculate_score_parts(resultados)["total"]

    def calculate_pp(self, resultados: List[ExerciseResult]) -> int:
        """Practice Points = 1 per attempted exercise."""
        return len(resultados)

    def calculate_pd(self, resultados: List[ExerciseResult]) -> int:
        """Domain Points = same as score."""
        return self.calculate_score(resultados)

    def calculate_xp(self, resultados: List[ExerciseResult]) -> int:
        """Experience Points = same as score."""
        return self.calculate_score(resultados)


# Singleton accessor (backward compatibility)
_instance = None

def get_scoring_calculator():
    global _instance
    if _instance is None:
        _instance = ScoringCalculator()
    return _instance
