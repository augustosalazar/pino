"""
DefaultBatchGenerator - Default implementation of IBatchGenerator

Generates complete batches of exercises with proper distribution.
"""

import random
from typing import List, Optional

from v2.interfaces import IBatchGenerator, IExerciseGenerator, IConfigManager
from v2.models import Exercise, BatchType, TipoRespuesta


class DefaultBatchGenerator(IBatchGenerator):
    """
    Default batch generator with controlled difficulty distribution.
    """
    
    def __init__(self, container=None):
        self._container = container
    
    @property
    def config_manager(self) -> IConfigManager:
        from v2.container import get_v2_container
        if self._container:
            return self._container.config_manager
        return get_v2_container().config_manager
    
    @property
    def exercise_generator(self) -> IExerciseGenerator:
        from v2.container import get_v2_container
        if self._container:
            return self._container.exercise_generator
        return get_v2_container().exercise_generator
        
    def generate_batch(
        self,
        user_ref: str,
        operacion: str,
        nivel_invisible: float,
        batch_type: str = BatchType.REGULAR,
        forced_exercises: Optional[List[Exercise]] = None,
        num_exercises: int = 10
    ) -> List[Exercise]:
        """
        Generate a list of exercises for a batch.
        
        Args:
            user_ref: User ID
            operacion: Main operation
            nivel_invisible: Central difficulty level
            batch_type: Type of batch
            forced_exercises: Pre-defined exercises to include
            num_exercises: Number of exercises to generate
            
        Returns:
            List of Exercise objects
        """
        if batch_type == BatchType.MINIBOSS:
            return self._generate_miniboss_batch(operacion, nivel_invisible)
        elif batch_type == BatchType.ENDLESS:
            return self._generate_endless_batch(operacion, nivel_invisible, num_exercises)
        else:
            return self._generate_regular_batch(operacion, nivel_invisible, forced_exercises)
            
    def _generate_regular_batch(
        self, 
        operacion: str, 
        nivel_central: float, 
        forced_exercises: List[Exercise] = None
    ) -> List[Exercise]:
        """
        Generate regular batch including review exercises if they exist.
        Review exercises displace easy exercises first, then central.
        """
        if forced_exercises is None: 
            forced_exercises = []
        
        batch_config = self.config_manager.get_batch_config()
        
        count_easy = batch_config.get("distribution_easy", 2)
        count_central = batch_config.get("distribution_central", 6)
        count_hard = batch_config.get("distribution_hard", 2)
        total_size = batch_config.get("size", 10)
        
        # Adjust distribution based on forced_exercises
        to_reduce = len(forced_exercises)
        
        print(f"[BatchGenerator] Forced exercises count: {to_reduce}")
        
        # Reduce easy first
        removed_easy = min(to_reduce, count_easy)
        count_easy -= removed_easy
        to_reduce -= removed_easy
        
        # Reduce central next
        removed_central = min(to_reduce, count_central)
        count_central -= removed_central
        to_reduce -= removed_central
        
        # Reduce hard if absolutely necessary
        removed_hard = min(to_reduce, count_hard)
        count_hard -= removed_hard
        
        exercises = []
        
        # 1. Add forced exercises (Review) at the beginning
        exercises.extend(forced_exercises)
        
        # 2. Generate remaining easy
        level_easy = max(1.0, nivel_central - 0.5)
        for _ in range(count_easy):
            exercises.append(self.exercise_generator.generate_exercise(operacion, level_easy))
            
        # 3. Generate remaining central
        for _ in range(count_central):
            exercises.append(self.exercise_generator.generate_exercise(operacion, nivel_central))
            
        # 4. Generate remaining hard
        level_hard = min(6.0, nivel_central + 0.5)
        for _ in range(count_hard):
            exercises.append(self.exercise_generator.generate_exercise(operacion, level_hard))
            
        return exercises

    def _generate_miniboss_batch(self, operacion: str, nivel_invisible: float) -> List[Exercise]:
        """
        Miniboss batch:
        - Only central level exercises
        - Only OPEN response type
        """
        batch_config = self.config_manager.get_batch_config()
        size = batch_config.get("size", 10)
        
        exercises = []
        for _ in range(size):
            ex = self.exercise_generator.generate_exercise(operacion, nivel_invisible)
            
            # Force open response type
            ex.tipo_respuesta = TipoRespuesta.ABIERTA
            ex.opciones = None
            
            exercises.append(ex)
            
        return exercises

    def _generate_endless_batch(
        self, 
        operacion: str, 
        nivel_invisible: float, 
        size: int = 10
    ) -> List[Exercise]:
        """
        Endless batch:
        - Only central level
        - Native response type for the level
        """
        exercises = []
        for _ in range(size):
            exercises.append(self.exercise_generator.generate_exercise(operacion, nivel_invisible))
            
        return exercises
