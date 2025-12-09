"""
PerformanceEvaluator - Motor de ajuste de dificultad V2

Responsable de calcular el nuevo 'nivel_invisible' basado en el desempeño
del usuario en un batch. Ajusta la dificultad dinámicamente.
"""

from typing import List
from v2.models import ExerciseResult

class PerformanceEvaluator:
    """
    Evaluador de desempeño que ajusta el nivel invisible
    """
    
    def __init__(self):
        # Configuración hardcoded de reglas de ajuste para garantizar estabilidad 
        # (podrían moverse a ConfigManager si se requiere A/B testing agresivo)
        self.min_level = 1.0
        self.max_level = 6.0
        self.high_threshold = 0.8  # >= 80% aciertos
        self.low_threshold = 0.4   # < 40% aciertos
        
        self.increase_step = 0.2
        self.decrease_step = 0.1
        self.neutral_step = 0.0

    def evaluate_performance(self, 
                           resultados: List[ExerciseResult], 
                           nivel_invisible_actual: float) -> float:
        """
        Calcula el nuevo nivel invisible.
        
        Args:
            resultados: Lista de resultados del batch
            nivel_invisible_actual: Nivel actual antes del batch
            
        Returns:
            Nuevo nivel invisible (clamped entre min y max)
        """
        if not resultados:
            return nivel_invisible_actual
            
        total = len(resultados)
        correctos = sum(1 for r in resultados if r.es_correcto)
        success_rate = correctos / total
        
        delta = self._calculate_delta(success_rate)
        
        nuevo_nivel = nivel_invisible_actual + delta
        
        # Clamp seguro
        return max(self.min_level, min(nuevo_nivel, self.max_level))
        
    def _calculate_delta(self, success_rate: float) -> float:
        """Determina el cambio de nivel según la tasa de éxito"""
        if success_rate >= self.high_threshold:
            # Desempeño alto -> Subir dificultad
            return self.increase_step
        elif success_rate < self.low_threshold:
            # Desempeño bajo -> Bajar dificultad
            return -self.decrease_step
        else:
            # Zona media (40% - 79%) -> Mantener dificultad
            # Esto da estabilidad y evita fluctuaciones constantes
            return self.neutral_step

# Singleton
_perf_evaluator_instance = None
def get_performance_evaluator():
    global _perf_evaluator_instance
    if _perf_evaluator_instance is None:
        _perf_evaluator_instance = PerformanceEvaluator()
    return _perf_evaluator_instance
