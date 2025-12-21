"""
BatchGenerator - Generates batches of exercises

Implements IBatchGenerator interface.
"""

from typing import List, Optional

from interfaces import IBatchGenerator
from gamification_models import Exercise, BatchType, TipoRespuesta


class BatchGenerator(IBatchGenerator):
    """
    Generates batches with controlled difficulty distribution.
    """
    
    def __init__(self, container=None):
        self._container = container
    
    @property
    def config_manager(self):
        if self._container:
            return self._container.config_manager
        from config_manager import get_config_manager
        return get_config_manager()
    
    @property
    def exercise_generator(self):
        if self._container:
            return self._container.exercise_generator
        from exercise_generator import get_exercise_generator
        return get_exercise_generator()
        
    def generate_batch(
        self,
        user_ref: str,
        operacion: str,
        nivel_invisible: float,
        batch_type: str = BatchType.REGULAR,
        forced_exercises: Optional[List[Exercise]] = None,
        num_exercises: int = 10
    ) -> List[Exercise]:
        """Generate a batch of exercises."""
        if batch_type == BatchType.MINIBOSS:
            return self._generate_miniboss_batch(operacion, nivel_invisible)
        elif batch_type == BatchType.ENDLESS:
            return self._generate_endless_batch(operacion, nivel_invisible, num_exercises)
        else:
            return self._generate_regular_batch(operacion, nivel_invisible, forced_exercises)
            
    def _generate_regular_batch(self, operacion: str, nivel_central: float, forced: List[Exercise] = None) -> List[Exercise]:
        if forced is None: forced = []
        
        batch_config = self.config_manager.get_batch_config()
        count_easy = batch_config.get("distribution_easy", 2)
        count_central = batch_config.get("distribution_central", 6)
        count_hard = batch_config.get("distribution_hard", 2)
        
        # Reduce counts based on forced exercises
        to_reduce = len(forced)
        removed = min(to_reduce, count_easy)
        count_easy -= removed
        to_reduce -= removed
        removed = min(to_reduce, count_central)
        count_central -= removed
        to_reduce -= removed
        count_hard -= min(to_reduce, count_hard)
        
        exercises = list(forced)
        
        level_easy = max(1.0, nivel_central - 0.5)
        for _ in range(count_easy):
            exercises.append(self.exercise_generator.generate_exercise(operacion, level_easy))
        
        for _ in range(count_central):
            exercises.append(self.exercise_generator.generate_exercise(operacion, nivel_central))
        
        level_hard = min(6.0, nivel_central + 0.5)
        for _ in range(count_hard):
            exercises.append(self.exercise_generator.generate_exercise(operacion, level_hard))
            
        return exercises

    def _generate_miniboss_batch(self, operacion: str, nivel: float) -> List[Exercise]:
        size = self.config_manager.get_batch_config().get("size", 10)
        exercises = []
        for _ in range(size):
            ex = self.exercise_generator.generate_exercise(operacion, nivel)
            ex.tipo_respuesta = TipoRespuesta.ABIERTA
            ex.opciones = None
            exercises.append(ex)
        return exercises

    def _generate_endless_batch(self, operacion: str, nivel: float, size: int = 10) -> List[Exercise]:
        return [self.exercise_generator.generate_exercise(operacion, nivel) for _ in range(size)]


# Singleton accessor (backward compatibility)
_instance = None

def get_batch_generator():
    global _instance
    if _instance is None:
        _instance = BatchGenerator()
    return _instance
