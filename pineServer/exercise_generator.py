"""
ExerciseGenerator - Generates individual math exercises

Implements IExerciseGenerator interface.
Uses interpolated difficulty configuration.
"""

import random
import math
from typing import List, Tuple, Optional

from interfaces import IExerciseGenerator
from gamification_models import Exercise, Operacion, TipoRespuesta


class ExerciseGenerator(IExerciseGenerator):
    """
    Generates exercises with interpolated difficulty.
    """
    
    def __init__(self, container=None):
        self._container = container
    
    @property
    def config_manager(self):
        if self._container:
            return self._container.config_manager
        from config_manager import get_config_manager
        return get_config_manager()
    
    def generate_exercise(self, operacion: str, nivel_invisible: float) -> Exercise:
        """Generate a single exercise based on the invisible level."""
        config = self._get_interpolated_config(operacion, nivel_invisible)
        op1, op2 = self._generate_operands(operacion, config)
        respuesta = self._calculate_result(op1, op2, operacion)
        tipo_respuesta = config["tipo_respuesta"]
        
        opciones = None
        if tipo_respuesta == TipoRespuesta.MULTIPLE_CHOICE:
            num_opciones = int(config.get("num_opciones", 4))
            opciones = self._generate_distractors(respuesta, num_opciones)
            
        return Exercise(
            operand_1=op1,
            operand_2=op2,
            operacion=operacion,
            respuesta_correcta=respuesta,
            dificultad=nivel_invisible,
            tipo_respuesta=tipo_respuesta,
            opciones=opciones,
            max_tiempo_segundos=int(config.get("max_tiempo_segundos", 30))
        )
    
    def _get_interpolated_config(self, operacion: str, nivel: float) -> dict:
        """Calculate mixed config between floor and ceiling levels."""
        nivel = max(1.0, min(float(nivel), 5.0))
        nivel_floor = int(math.floor(nivel))
        nivel_ceil = int(math.ceil(nivel))
        
        if nivel_floor == nivel_ceil:
            config = self.config_manager.get_difficulty_config(operacion, nivel_floor)
            return config if config else self._get_fallback_config()
        
        config_low = self.config_manager.get_difficulty_config(operacion, nivel_floor)
        config_high = self.config_manager.get_difficulty_config(operacion, nivel_ceil)
        
        if not config_low: return config_high or self._get_fallback_config()
        if not config_high: return config_low
        
        t = nivel - nivel_floor
        interpolated = {}
        
        for field in ["min_operando_1", "max_operando_1", "min_operando_2", "max_operando_2", "max_tiempo_segundos"]:
            val_low = config_low.get(field, 0)
            val_high = config_high.get(field, 0)
            interpolated[field] = int(round(val_low + (val_high - val_low) * t))
        
        ref = config_high if t > 0.5 else config_low
        interpolated["tipo_respuesta"] = ref.get("tipo_respuesta", TipoRespuesta.MULTIPLE_CHOICE)
        interpolated["num_opciones"] = ref.get("num_opciones", 4)
        interpolated["max_resultado"] = ref.get("max_resultado")
        
        return interpolated

    def _generate_operands(self, operacion: str, config: dict) -> Tuple[int, int]:
        min_op1, max_op1 = config["min_operando_1"], config["max_operando_1"]
        min_op2, max_op2 = config["min_operando_2"], config["max_operando_2"]
        max_res = config.get("max_resultado")
        
        if max_op1 < min_op1: max_op1 = min_op1 + 10
        if max_op2 < min_op2: max_op2 = min_op2 + 10
        
        for _ in range(50):
            op1 = random.randint(min_op1, max_op1)
            op2 = random.randint(min_op2, max_op2)
            
            if operacion == Operacion.RESTA:
                if op1 < op2: op1, op2 = op2, op1
                if max_res and (op1 - op2) > max_res: continue
            elif operacion == Operacion.DIV:
                if op2 == 0: op2 = 1
                dividendo = op1 * op2
                op1, op2 = dividendo, op2
                if op1 > max_op1 or op1 < min_op1: continue
            elif operacion == Operacion.MULT:
                if max_res and (op1 * op2) > max_res: continue
            elif operacion == Operacion.SUMA:
                if max_res and (op1 + op2) > max_res: continue
            
            return op1, op2
        
        if operacion == Operacion.DIV:
            divisor = max(1, random.randint(min_op2, max_op2))
            return random.randint(1, 10) * divisor, divisor
        return min_op1, min_op2

    def _calculate_result(self, op1: int, op2: int, operacion: str) -> float:
        if operacion == Operacion.SUMA: return op1 + op2
        if operacion == Operacion.RESTA: return op1 - op2
        if operacion == Operacion.MULT: return op1 * op2
        if operacion == Operacion.DIV: return op1 / op2 if op2 != 0 else 0
        return 0

    def _generate_distractors(self, correcta: float, num_opciones: int) -> List[int]:
        opciones = {correcta}
        for _ in range(20):
            if len(opciones) >= num_opciones: break
            variant = random.choice([1, 2, 5, 10, -1, -2, -5, -10])
            distractor = int(correcta) + variant if float(correcta).is_integer() else round(correcta + variant * 0.1, 2)
            if distractor >= 0: opciones.add(distractor)
        
        while len(opciones) < num_opciones:
            opciones.add(int(correcta) + random.randint(1, 50))
        
        result = list(opciones)
        if float(correcta).is_integer():
            result = [int(x) for x in result]
        random.shuffle(result)
        return result

    def _get_fallback_config(self) -> dict:
        return {
            "min_operando_1": 1, "max_operando_1": 10,
            "min_operando_2": 1, "max_operando_2": 10,
            "tipo_respuesta": TipoRespuesta.MULTIPLE_CHOICE,
            "num_opciones": 4, "max_tiempo_segundos": 30
        }


# Singleton accessor (backward compatibility)
_instance = None

def get_exercise_generator():
    global _instance
    if _instance is None:
        _instance = ExerciseGenerator()
    return _instance
