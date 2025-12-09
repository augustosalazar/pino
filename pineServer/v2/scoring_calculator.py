"""
ScoringCalculator - Motor de puntuación y recompensas V2

Implementa las fórmulas de:
- Score (puntos del juego)
- PP (Puntos de Práctica)
- PD (Puntos de Dominio)
- XP (Experiencia)
"""

from typing import List, Dict
from v2.models import ExerciseResult, Operacion
from v2.config_manager import get_config_manager

class ScoringCalculator:
    
    def __init__(self):
        self.config_manager = get_config_manager()
        
    def calculate_score_parts(self, resultados: List[ExerciseResult]) -> Dict[str, int]:
        """
        Calcula el score desglosado en sus componentes.
        
        Formula: 
          Score = (C * (BaseMult + AvgDiff)) + Bonus - Penalty
        """
        if not resultados:
            return {"total": 0, "base": 0, "bonus": 0, "penalty": 0}
            
        scoring_config = self.config_manager.get_scoring_config()
        
        base_multiplier = scoring_config["base_multiplier"] # default 5
        participation_bonus = scoring_config["participation_bonus"] # default 10
        error_penalty = scoring_config["error_penalty"] # default 2
        
        correctos = sum(1 for r in resultados if r.es_correcto)
        total_items = len(resultados)
        errores = total_items - correctos
        
        # Dificultad promedio (d)
        if total_items > 0:
            avg_difficulty = sum(r.exercise.dificultad for r in resultados) / total_items
        else:
            avg_difficulty = 1.0
            
        # 1. Base Score calculation: C * (5 + d)
        # Nota: Multiplicamos por 10 o 100 si queremos enteros más grandes? 
        # El prompt dice: "C por (5 más d)". Si d es 1.5, sería C * 6.5. 
        # Para evitar decimales en el score, redondearemos al final.
        base_score_val = correctos * (base_multiplier + avg_difficulty)
        
        # 2. Bonus Participación (si completó el batch, asumimos que si llega aquí, lo hizo)
        bonus_val = participation_bonus
        
        # 3. Penalización
        penalty_val = errores * error_penalty
        
        # Total
        total = int(round(base_score_val + bonus_val - penalty_val))
        
        # Regla: Mínimo 0.
        # Regla extra: "Con dos o más aciertos siempre se obtiene una puntuación positiva"
        # Si tiene 2 aciertos (score base aprox 12) + 10 bonus - 16 penalty = 6 positivo. Cumple.
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
        Calcula Puntos de Práctica.
        Regla: "10 puntos de práctica si se intentan todos"
        """
        # Asumimos que si están en resultados, fueron intentados.
        return len(resultados) # 1 punto por ejercicio intentado = 10 por batch

    def calculate_pd(self, resultados: List[ExerciseResult]) -> int:
        """
        Calcula Puntos de Dominio (para la operación específica).
        Podría ser igual al score o una fracción.
        Por ahora usaremos el score base.
        """
        # Usamos el mismo score total como PD
        return self.calculate_score(resultados)

    def calculate_xp(self, resultados: List[ExerciseResult]) -> int:
        """XP General"""
        return self.calculate_score(resultados)

# Singleton
_scoring_calc_instance = None
def get_scoring_calculator():
    global _scoring_calc_instance
    if _scoring_calc_instance is None:
        _scoring_calc_instance = ScoringCalculator()
    return _scoring_calc_instance
