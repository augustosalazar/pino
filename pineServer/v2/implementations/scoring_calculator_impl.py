"""
DefaultScoringCalculator - Default implementation of IScoringCalculator

Implements scoring formulas for PP, PD, XP, and total score.
"""

from typing import List, Dict
from v2.interfaces import IScoringCalculator, IConfigManager
from v2.models import ExerciseResult


class DefaultScoringCalculator(IScoringCalculator):
    """
    Default scoring calculator implementing gamification reward formulas.
    """
    
    def __init__(self, container=None):
        self._container = container
    
    @property
    def config_manager(self) -> IConfigManager:
        from v2.container import get_v2_container
        if self._container:
            return self._container.config_manager
        return get_v2_container().config_manager
        
    def calculate_score_parts(self, resultados: List[ExerciseResult]) -> Dict[str, int]:
        """
        Calculate score breakdown.
        
        Formula: 
          Score = (C * (BaseMult + AvgDiff)) + Bonus - Penalty
        """
        if not resultados:
            return {"total": 0, "base": 0, "bonus": 0, "penalty": 0}
            
        scoring_config = self.config_manager.get_scoring_config()
        
        base_multiplier = scoring_config["base_multiplier"]  # default 5
        participation_bonus = scoring_config["participation_bonus"]  # default 10
        error_penalty = scoring_config["error_penalty"]  # default 2
        
        correctos = sum(1 for r in resultados if r.es_correcto)
        total_items = len(resultados)
        errores = total_items - correctos
        
        # Average difficulty
        if total_items > 0:
            avg_difficulty = sum(r.exercise.dificultad for r in resultados) / total_items
        else:
            avg_difficulty = 1.0
            
        # 1. Base Score: C * (5 + d)
        base_score_val = correctos * (base_multiplier + avg_difficulty)
        
        # 2. Participation Bonus
        bonus_val = participation_bonus
        
        # 3. Penalty
        penalty_val = errores * error_penalty
        
        # Total
        total = int(round(base_score_val + bonus_val - penalty_val))
        
        # Minimum 0
        if total < 0:
            total = 0
            
        return {
            "total": total,
            "base": int(round(base_score_val)),
            "bonus": bonus_val,
            "penalty": penalty_val
        }

    def calculate_score(self, resultados: List[ExerciseResult]) -> int:
        parts = self.calculate_score_parts(resultados)
        return parts["total"]

    def calculate_pp(self, resultados: List[ExerciseResult]) -> int:
        """
        Calculate Practice Points.
        Rule: "10 practice points if all are attempted"
        """
        # If in results, they were attempted
        return len(resultados)  # 1 point per attempted exercise = 10 per batch

    def calculate_pd(self, resultados: List[ExerciseResult]) -> int:
        """
        Calculate Domain Points (for specific operation).
        Uses the same score total as PD.
        """
        return self.calculate_score(resultados)

    def calculate_xp(self, resultados: List[ExerciseResult]) -> int:
        """General XP."""
        return self.calculate_score(resultados)
