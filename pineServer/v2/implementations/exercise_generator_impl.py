"""
DefaultExerciseGenerator - Default implementation of IExerciseGenerator

Generates individual exercises with interpolated difficulty configuration.
"""

import random
import math
from typing import List, Tuple, Optional, Dict, Any

from v2.interfaces import IExerciseGenerator, IConfigManager
from v2.models import Exercise, Operacion, TipoRespuesta


class DefaultExerciseGenerator(IExerciseGenerator):
    """
    Default exercise generator with interpolated difficulty.
    """
    
    def __init__(self, container=None):
        self._container = container
    
    @property
    def config_manager(self) -> IConfigManager:
        """Lazy resolution of config manager."""
        from v2.container import get_v2_container
        if self._container:
            return self._container.config_manager
        return get_v2_container().config_manager
    
    def generate_exercise(self, operacion: str, nivel_invisible: float) -> Exercise:
        """
        Generate a single exercise based on the invisible level.
        
        Args:
            operacion: Operation type ('suma', 'resta', 'mult', 'div')
            nivel_invisible: Difficulty level (float, e.g., 2.5)
            
        Returns:
            Exercise instance
        """
        # 1. Get interpolated configuration
        config = self._get_interpolated_config(operacion, nivel_invisible)
        
        # 2. Generate valid operands
        op1, op2 = self._generate_operands(operacion, config)
        
        # 3. Calculate correct answer
        respuesta = self._calculate_result(op1, op2, operacion)
        
        # 4. Determine response type
        tipo_respuesta = config["tipo_respuesta"]
        
        # 5. Generate options for multiple choice
        opciones = None
        if tipo_respuesta == TipoRespuesta.MULTIPLE_CHOICE:
            num_opciones = int(config.get("num_opciones", 4))
            opciones = self._generate_distractors(respuesta, num_opciones)
            
        # 6. Create Exercise object
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
        """
        Calculate a mixed configuration between floor and ceiling levels.
        E.g.: Level 2.3 mixes 70% of Level 2 and 30% of Level 3.
        """
        # Clamp level between 1.0 and 5.0
        nivel = max(1.0, min(float(nivel), 5.0))
        
        nivel_floor = int(math.floor(nivel))
        nivel_ceil = int(math.ceil(nivel))
        
        # If exact integer (e.g., 2.0), return that config directly
        if nivel_floor == nivel_ceil:
            config = self.config_manager.get_difficulty_config(operacion, nivel_floor)
            if not config:
                return self._get_fallback_config(operacion)
            return config
            
        # Get both configs
        config_low = self.config_manager.get_difficulty_config(operacion, nivel_floor)
        config_high = self.config_manager.get_difficulty_config(operacion, nivel_ceil)
        
        # If one is missing, use the available one
        if not config_low: 
            return config_high or self._get_fallback_config(operacion)
        if not config_high: 
            return config_low
        
        # Interpolation factor (0.0 to 1.0)
        t = nivel - nivel_floor
        
        # Interpolate numeric values
        interpolated = {}
        
        numeric_fields = [
            "min_operando_1", "max_operando_1", 
            "min_operando_2", "max_operando_2",
            "max_tiempo_segundos"
        ]
        
        for field in numeric_fields:
            val_low = config_low.get(field, 0)
            val_high = config_high.get(field, 0)
            val_interp = val_low + (val_high - val_low) * t
            interpolated[field] = int(round(val_interp))
            
        # Discrete fields use the closest level
        reference_config = config_high if t > 0.5 else config_low
        interpolated["tipo_respuesta"] = reference_config.get("tipo_respuesta", TipoRespuesta.MULTIPLE_CHOICE)
        interpolated["num_opciones"] = reference_config.get("num_opciones", 4)
        interpolated["max_resultado"] = reference_config.get("max_resultado")
        
        return interpolated

    def _generate_operands(self, operacion: str, config: dict) -> Tuple[int, int]:
        """Generate two operands respecting configuration constraints."""
        min_op1 = config["min_operando_1"]
        max_op1 = config["max_operando_1"]
        min_op2 = config["min_operando_2"]
        max_op2 = config["max_operando_2"]
        max_res = config.get("max_resultado")
        
        # Safety checks
        if max_op1 < min_op1: max_op1 = min_op1 + 10
        if max_op2 < min_op2: max_op2 = min_op2 + 10
        
        for _ in range(50):
            op1 = random.randint(min_op1, max_op1)
            op2 = random.randint(min_op2, max_op2)
            
            if operacion == Operacion.RESTA:
                if op1 < op2:
                    op1, op2 = op2, op1
                if max_res and (op1 - op2) > max_res:
                    continue
                    
            elif operacion == Operacion.DIV:
                cociente = op1
                divisor = op2
                if divisor == 0: divisor = 1
                dividendo = cociente * divisor
                op1, op2 = dividendo, divisor
                if op1 > max_op1 or op1 < min_op1:
                    continue
            
            elif operacion == Operacion.MULT:
                if max_res and (op1 * op2) > max_res:
                    continue
            
            elif operacion == Operacion.SUMA:
                if max_res and (op1 + op2) > max_res:
                    continue
            
            return op1, op2
            
        # Fallback to safe minimum values
        if operacion == Operacion.DIV:
            divisor = random.randint(min_op2, max_op2)
            if divisor == 0: divisor = 1
            cociente = random.randint(1, 10) 
            return cociente * divisor, divisor
            
        return min_op1, min_op2

    def _calculate_result(self, op1: int, op2: int, operacion: str) -> float:
        if operacion == Operacion.SUMA: return op1 + op2
        if operacion == Operacion.RESTA: return op1 - op2
        if operacion == Operacion.MULT: return op1 * op2
        if operacion == Operacion.DIV: return op1 / op2 if op2 != 0 else 0
        return 0

    def _generate_distractors(self, correcta: float, num_opciones: int) -> List[int]:
        """Generate plausible incorrect options."""
        opciones = {correcta}
        
        target = num_opciones
        attempts = 0
        
        while len(opciones) < target and attempts < 20:
            attempts += 1
            variant = random.choice([1, 2, 5, 10, -1, -2, -5, -10])
            
            if isinstance(correcta, float) and not correcta.is_integer():
                distractor = round(correcta + (variant * 0.1), 2)
            else:
                distractor = int(correcta) + variant
                
            if distractor >= 0:
                opciones.add(distractor)
                
        while len(opciones) < target:
            opciones.add(int(correcta) + random.randint(1, 50))
            
        final_opciones = list(opciones)
        
        if float(correcta).is_integer():
            final_opciones = [int(x) for x in final_opciones]
            
        random.shuffle(final_opciones)
        return final_opciones

    def _get_fallback_config(self, operacion: str) -> dict:
        """Default configuration if database fails."""
        return {
            "min_operando_1": 1, "max_operando_1": 10,
            "min_operando_2": 1, "max_operando_2": 10,
            "tipo_respuesta": TipoRespuesta.MULTIPLE_CHOICE,
            "num_opciones": 4,
            "max_tiempo_segundos": 30
        }
