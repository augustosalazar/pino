"""
ExerciseGenerator - Generador de ejercicios matemáticos V2

Responsable de crear instancias de ejercicios individuales basándose en:
- Operación (suma, resta, mult, div)
- Nivel invisible (float)
- Configuraciones interpoladas de dificultad
"""

import sys
import os
import random
import math
from typing import List, Tuple, Optional, Any

# Add parent directory to path to import sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v2.models import Exercise, Operacion, TipoRespuesta
from v2.config_manager import get_config_manager


class ExerciseGenerator:
    """
    Generador de ejercicios con dificultad interpolada
    """
    
    def __init__(self):
        self.config_manager = get_config_manager()
    
    def generate_exercise(self, operacion: str, nivel_invisible: float) -> Exercise:
        """
        Genera un único ejercicio basado en el nivel invisible
        
        Args:
            operacion: Tipo de operación (suma, resta, mult, div)
            nivel_invisible: Nivel de dificultad (float, ej: 2.5)
            
        Returns:
            Instancia de Exercise
        """
        # 1. Obtener configuración interpolada
        config = self._get_interpolated_config(operacion, nivel_invisible)
        
        # 2. Generar operandos válidos
        op1, op2 = self._generate_operands(operacion, config)
        
        # 3. Calcular respuesta correcta
        respuesta = self._calculate_result(op1, op2, operacion)
        
        # 4. Determinar tipo de respuesta (probabilístico o determinista)
        # Si estamos cerca de un nivel abierto, favorecer abierta
        tipo_respuesta = config["tipo_respuesta"]
        
        # 5. Generar opciones si es multiple choice
        opciones = None
        if tipo_respuesta == TipoRespuesta.MULTIPLE_CHOICE:
            num_opciones = int(config.get("num_opciones", 4))
            opciones = self._generate_distractors(respuesta, num_opciones)
            
        # 6. Crear objeto Exercise
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
        Calcula una configuración mezcla entre el piso y techo del nivel actual.
        Ej: Nivel 2.3 mezcla 70% de Nivel 2 y 30% de Nivel 3.
        """
        # Clamp nivel entre 1.0 y 5.0 (o el máximo que tengamos configurado)
        # Asumimos config max es 5 por ahora
        nivel = max(1.0, min(float(nivel), 5.0))
        
        nivel_floor = int(math.floor(nivel))
        nivel_ceil = int(math.ceil(nivel))
        
        # Si es entero exacto (ej: 2.0), devolvemos esa config directa
        if nivel_floor == nivel_ceil:
            config = self.config_manager.get_difficulty_config(operacion, nivel_floor)
            if not config:
                # Fallback seguro si falta config
                return self._get_fallback_config(operacion)
            return config
            
        # Obtener ambas configs
        config_low = self.config_manager.get_difficulty_config(operacion, nivel_floor)
        config_high = self.config_manager.get_difficulty_config(operacion, nivel_ceil)
        
        # Si falta alguna, usar la disponible (sin interpolar)
        if not config_low: return config_high or self._get_fallback_config(operacion)
        if not config_high: return config_low
        
        # Factor de interpolación (0.0 a 1.0)
        # Ej: 2.3 -> t = 0.3
        t = nivel - nivel_floor
        
        # Interpolar valores numéricos
        interpolated = {}
        
        # Campos numéricos a interpolar
        numeric_fields = [
            "min_operando_1", "max_operando_1", 
            "min_operando_2", "max_operando_2",
            "max_tiempo_segundos"
        ]
        
        for field in numeric_fields:
            val_low = config_low.get(field, 0)
            val_high = config_high.get(field, 0)
            # Lerp: a + (b - a) * t
            val_interp = val_low + (val_high - val_low) * t
            interpolated[field] = int(round(val_interp))
            
        # Campos discretos (strings / bools)
        # Usamos el nivel más cercano (round)
        reference_config = config_high if t > 0.5 else config_low
        interpolated["tipo_respuesta"] = reference_config.get("tipo_respuesta", TipoRespuesta.MULTIPLE_CHOICE)
        interpolated["num_opciones"] = reference_config.get("num_opciones", 4)
        interpolated["max_resultado"] = reference_config.get("max_resultado") # Puede ser None
        
        return interpolated

    def _generate_operands(self, operacion: str, config: dict) -> Tuple[int, int]:
        """Genera dos operandos respetando las restricciones de la configuración"""
        min_op1 = config["min_operando_1"]
        max_op1 = config["max_operando_1"]
        min_op2 = config["min_operando_2"]
        max_op2 = config["max_operando_2"]
        max_res = config.get("max_resultado")
        
        # Safety checks
        if max_op1 < min_op1: max_op1 = min_op1 + 10
        if max_op2 < min_op2: max_op2 = min_op2 + 10
        
        for _ in range(50): # Intentos para cumplir restricciones
            op1 = random.randint(min_op1, max_op1)
            op2 = random.randint(min_op2, max_op2)
            
            # Restricciones por operación
            if operacion == Operacion.RESTA:
                # Evitar negativos si estamos en niveles básicos (asumido por ahora)
                # Swap si op1 < op2 para garantizar positivo
                if op1 < op2:
                    op1, op2 = op2, op1
                
                # Check max result constraint (para resta, el resultado <= op1, usually ok)
                if max_res and (op1 - op2) > max_res:
                    continue
                    
            elif operacion == Operacion.DIV:
                # Para división, generamos multiplicando inverso
                # op2 será el divisor, op1 (generado) será el cociente
                # Real op1 (dividendo) = divisor * cociente
                cociente = op1
                divisor = op2
                if divisor == 0: divisor = 1 # Evitar div por 0
                
                dividendo = cociente * divisor
                
                # Reasignar para retornar (dividendo, divisor)
                op1, op2 = dividendo, divisor
                
                # Validar rango del dividendo (op1 actual)
                # A veces el rango configurado es para el dividendo, a veces para los factores
                # Asumamos que config de división define rango de DIVIDENDO y DIVISOR
                # Si dividendo se pasa del max_op1, reintentar
                if op1 > max_op1 or op1 < min_op1:
                    continue
            
            elif operacion == Operacion.MULT:
                 if max_res and (op1 * op2) > max_res:
                    continue
            
            elif operacion == Operacion.SUMA:
                if max_res and (op1 + op2) > max_res:
                    continue
            
            return op1, op2
            
        # Si fallan los intentos, devolver valores seguros mínimos
        if operacion == Operacion.DIV:
            # Asegurar división exacta básica
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
        """Genera opciones incorrectas plausibles"""
        opciones = {correcta}
        
        target = num_opciones
        attempts = 0
        
        while len(opciones) < target and attempts < 20:
            attempts += 1
            # Estrategias de error:
            # 1. Variación pequeña (+-1, +-2, +-10)
            # 2. Error de dígito
            variant = random.choice([1, 2, 5, 10, -1, -2, -5, -10])
            
            # Si es float (división), manejar decimales o enteros cercanos
            if isinstance(correcta, float) and not correcta.is_integer():
                distractor = round(correcta + (variant * 0.1), 2)
            else:
                distractor = int(correcta) + variant
                
            if distractor >= 0: # Asumimos no negativos por ahora
                opciones.add(distractor)
                
        # Fill with random if logic fails
        while len(opciones) < target:
            opciones.add(int(correcta) + random.randint(1, 50))
            
        # Convert to list and shuffle
        final_opciones = list(opciones)
        
        # Asegurar que sean ints si la respuesta es entera (para mejor UX)
        if float(correcta).is_integer():
            final_opciones = [int(x) for x in final_opciones]
            
        random.shuffle(final_opciones)
        return final_opciones

    def _get_fallback_config(self, operacion: str) -> dict:
        """Configuración por defecto si falla la BD"""
        return {
            "min_operando_1": 1, "max_operando_1": 10,
            "min_operando_2": 1, "max_operando_2": 10,
            "tipo_respuesta": TipoRespuesta.MULTIPLE_CHOICE,
            "num_opciones": 4,
            "max_tiempo_segundos": 30
        }

# Singleton
_exercise_gen_instance = None
def get_exercise_generator():
    global _exercise_gen_instance
    if _exercise_gen_instance is None:
        _exercise_gen_instance = ExerciseGenerator()
    return _exercise_gen_instance
