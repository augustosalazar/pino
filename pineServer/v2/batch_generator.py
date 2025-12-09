"""
BatchGenerator - Generador de batches completos V2

Responsable de orquestar la creación de conjuntos de ejercicios (batches)
siguiendo las reglas de distribución de dificultad y tipos de batch.
"""

import sys
import os
import random
from typing import List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v2.models import Exercise, BatchType, Operacion, TipoRespuesta
from v2.config_manager import get_config_manager
from v2.exercise_generator import get_exercise_generator


class BatchGenerator:
    """
    Generador de batches con distribución de dificultad controlada
    """
    
    def __init__(self):
        self.config_manager = get_config_manager()
        self.exercise_generator = get_exercise_generator()
        
    def generate_batch(self, 
                      user_ref: str, 
                      operacion: str, 
                      nivel_invisible: float,
                      batch_type: str = BatchType.REGULAR,
                      forced_exercises: Optional[List[Exercise]] = None) -> List[Exercise]:
        """
        Genera una lista de ejercicios para un batch
        
        Args:
            user_ref: ID del usuario
            operacion: Operación principal
            nivel_invisible: Nivel de dificultad central
            batch_type: Tipo de batch deseado
            forced_exercises: Lista de ejercicios pre-definidos (ej: repaso) a incluir
            
        Returns:
            Lista de objetos Exercise
        """
        # 1. Configurar distribución según tipo de batch
        if batch_type == BatchType.MINIBOSS:
            return self._generate_miniboss_batch(operacion, nivel_invisible)
        elif batch_type == BatchType.ENDLESS:
            return self._generate_endless_batch(operacion, nivel_invisible)
        else:
            return self._generate_regular_batch(operacion, nivel_invisible, forced_exercises)
            
    def _generate_regular_batch(self, operacion: str, nivel_central: float, forced_exercises: List[Exercise] = None) -> List[Exercise]:
        """
        Genera batch regular incluyendo ejercicios de repaso (forced) si existen.
        Los ejercicios de repaso desplazan primero a los fáciles, luego centrales.
        """
        if forced_exercises is None: forced_exercises = []
        
        batch_config = self.config_manager.get_batch_config()
        
        count_easy = batch_config.get("distribution_easy", 2)
        count_central = batch_config.get("distribution_central", 6)
        count_hard = batch_config.get("distribution_hard", 2)
        total_size = batch_config.get("size", 10)
        
        # Ajustar distribución basada en forced_exercises
        # Asumimos que los forced ocupan lugar de Easy/Central (warmup)
        # Reducimos counts para mantener total_size
        to_reduce = len(forced_exercises)

        print(f"[BatchGenerator] Forced exercises count: {to_reduce}")
        
        # Reducir Easy primero
        removed_easy = min(to_reduce, count_easy)
        count_easy -= removed_easy
        to_reduce -= removed_easy
        
        # Reducir Central después
        removed_central = min(to_reduce, count_central)
        count_central -= removed_central
        to_reduce -= removed_central
        
        # Reducir Hard si es absolutamente necesario (raro)
        removed_hard = min(to_reduce, count_hard)
        count_hard -= removed_hard
        
        exercises = []
        
        # 1. Agregar ejercicios forzados (Review) al principio
        exercises.extend(forced_exercises)
        
        # 2. Generar Easy restantes
        level_easy = max(1.0, nivel_central - 0.5)
        for _ in range(count_easy):
            exercises.append(self.exercise_generator.generate_exercise(operacion, level_easy))
            
        # 3. Generar Central restantes
        for _ in range(count_central):
            exercises.append(self.exercise_generator.generate_exercise(operacion, nivel_central))
            
        # 4. Generar Hard restantes
        level_hard = min(6.0, nivel_central + 0.5)
        for _ in range(count_hard):
            exercises.append(self.exercise_generator.generate_exercise(operacion, level_hard))
            
        return exercises

    def _generate_miniboss_batch(self, operacion: str, nivel_invisible: float) -> List[Exercise]:
        """
        Batch de Miniboss:
        - Solo ejercicios del nivel central
        - Solo respuesta ABIERTA (si es posible)
        """
        batch_config = self.config_manager.get_batch_config()
        size = batch_config.get("size", 10)
        
        exercises = []
        for _ in range(size):
            # Forzar tipo de respuesta ABIERTA en generator podría requerir 
            # pasar un override config, pero por ahora confiamos en el generator.
            # Ojo: El prompt dice "El batch miniboss contiene únicamente ejercicios de respuesta abierta"
            
            # Generamos el ejercicio estándar
            ex = self.exercise_generator.generate_exercise(operacion, nivel_invisible)
            
            # Lo forzamos a ser abierta y limpiamos opciones
            ex.tipo_respuesta = TipoRespuesta.ABIERTA
            ex.opciones = None
            
            exercises.append(ex)
            
        return exercises

    def _generate_endless_batch(self, operacion: str, nivel_invisible: float) -> List[Exercise]:
        """
        Batch Endless:
        - Solo nivel central
        - Tipo respuesta nativo del nivel
        """
        batch_config = self.config_manager.get_batch_config()
        size = batch_config.get("size", 10)
        
        exercises = []
        for _ in range(size):
            exercises.append(self.exercise_generator.generate_exercise(operacion, nivel_invisible))
            
        return exercises


# Singleton
_batch_gen_instance = None
def get_batch_generator():
    global _batch_gen_instance
    if _batch_gen_instance is None:
        _batch_gen_instance = BatchGenerator()
    return _batch_gen_instance
