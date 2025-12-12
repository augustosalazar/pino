"""
Models V2 - Dataclasses para el sistema de gamificación

Este módulo define las estructuras de datos principales usadas
en todo el sistema V2.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Operacion(str, Enum):
    """Tipos de operaciones matemáticas soportadas"""
    SUMA = "suma"
    RESTA = "resta"
    MULT = "mult"
    DIV = "div"


class TipoRespuesta(str, Enum):
    """Tipos de respuesta para ejercicios"""
    MULTIPLE_CHOICE = "multiple_choice"
    ABIERTA = "abierta"


class BatchType(str, Enum):
    """Tipos de batch"""
    REGULAR = "regular"
    MINIBOSS = "miniboss"
    ENDLESS = "endless"


@dataclass
class Exercise:
    """
    Representa un ejercicio matemático generado
    
    Attributes:
        operand_1: Primer operando
        operand_2: Segundo operando
        operacion: Tipo de operación (suma, resta, mult, div)
        respuesta_correcta: Resultado correcto
        dificultad: Nivel de dificultad (float 1.0-6.0)
        tipo_respuesta: "multiple_choice" o "abierta"
        opciones: Lista de opciones para multiple choice (None si abierta)
        max_tiempo_segundos: Tiempo máximo permitido
    """
    operand_1: int
    operand_2: int
    operacion: str
    respuesta_correcta: float
    dificultad: float
    tipo_respuesta: str
    opciones: Optional[List[int]] = None
    pending_ref: Optional[str] = None # ID de pine_pending_items si viene de repaso
    max_tiempo_segundos: int = 30
    
    @property
    def problem(self) -> str:
        """Genera el string del problema (ej: '5 + 3')"""
        op_symbols = {
            "suma": "+",
            "resta": "-",
            "mult": "×",
            "div": "÷"
        }
        symbol = op_symbols.get(self.operacion, "+")
        return f"{self.operand_1} {symbol} {self.operand_2}"
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para JSON"""
        return {
            "operand_1": self.operand_1,
            "operand_2": self.operand_2,
            "operacion": self.operacion,
            "respuesta_correcta": self.respuesta_correcta,
            "dificultad": self.dificultad,
            "tipo_respuesta": self.tipo_respuesta,
            "opciones": self.opciones,
            "max_tiempo_segundos": self.max_tiempo_segundos,
            "problem": self.problem
        }


@dataclass
class ExerciseResult:
    """
    Resultado de un ejercicio completado por el usuario
    
    Attributes:
        exercise: El ejercicio original
        respuesta_usuario: Respuesta dada por el usuario
        es_correcto: Si la respuesta fue correcta
        tiempo_segundos: Tiempo que tardó en responder
        fue_retry: Si es un ejercicio de repetición
    """
    exercise: Exercise
    respuesta_usuario: float
    es_correcto: bool
    tiempo_segundos: float
    fue_retry: bool = False
    legacy_ref: Optional[str] = None  # ID del ejercicio en tabla pine_exercises
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para JSON/JSONB"""
        return {
            "operand_1": self.exercise.operand_1,
            "operand_2": self.exercise.operand_2,
            "operacion": self.exercise.operacion,
            "respuesta_correcta": self.exercise.respuesta_correcta,
            "respuesta_usuario": self.respuesta_usuario,
            "es_correcto": self.es_correcto,
            "dificultad": self.exercise.dificultad,
            "tiempo_segundos": self.tiempo_segundos,
            "fue_retry": self.fue_retry
        }


@dataclass
class BatchResult:
    """
    Resultado completo de un batch de ejercicios
    
    Attributes:
        user_ref: ID del usuario
        operacion: Operación principal del batch
        batch_type: Tipo de batch (regular, miniboss, endless)
        ejercicios: Lista de resultados de ejercicios
        nivel_central: Nivel central del batch
        nivel_invisible_antes: Nivel invisible antes del batch
        nivel_invisible_despues: Nivel invisible después del batch
        score_ganado: Score calculado
        pp_ganados: Puntos de práctica ganados
        pd_ganados: Puntos de dominio ganados
        xp_ganada: Experiencia ganada
        duracion_segundos: Duración total del batch
        miniboss_aprobado: Si aplica, resultado del miniboss
        endless_streak: Si aplica, streak en modo endless
    """
    user_ref: str
    operacion: str
    batch_type: str
    ejercicios: List[ExerciseResult]
    nivel_central: int
    nivel_invisible_antes: float
    nivel_invisible_despues: float
    score_ganado: int = 0
    pp_ganados: int = 0
    pd_ganados: int = 0
    xp_ganada: int = 0
    duracion_segundos: Optional[int] = None
    miniboss_aprobado: Optional[bool] = None
    endless_streak: Optional[int] = None
    completado_en: datetime = field(default_factory=datetime.utcnow)
    session_ref: Optional[str] = None  # ID de la sesión V2 asociada
    
    @property
    def total_ejercicios(self) -> int:
        """Cantidad total de ejercicios"""
        return len(self.ejercicios)
    
    @property
    def ejercicios_correctos(self) -> int:
        """Cantidad de ejercicios correctos"""
        return sum(1 for e in self.ejercicios if e.es_correcto)
    
    @property
    def success_rate(self) -> float:
        """Tasa de aciertos (0.0 a 1.0)"""
        if self.total_ejercicios == 0:
            return 0.0
        return self.ejercicios_correctos / self.total_ejercicios
    
    @property
    def dificultad_promedio(self) -> float:
        """Dificultad promedio de los ejercicios"""
        if not self.ejercicios:
            return 0.0
        return sum(e.exercise.dificultad for e in self.ejercicios) / len(self.ejercicios)
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para inserción en BD"""
        return {
            "user_ref": self.user_ref,
            "batch_type": self.batch_type,
            "operacion": self.operacion,
            "nivel_central": self.nivel_central,
            "nivel_invisible_antes": self.nivel_invisible_antes,
            "nivel_invisible_despues": self.nivel_invisible_despues,
            "total_ejercicios": self.total_ejercicios,
            "ejercicios_correctos": self.ejercicios_correctos,
            "dificultad_promedio": self.dificultad_promedio,
            "score_ganado": self.score_ganado,
            "pp_ganados": self.pp_ganados,
            "pd_ganados": self.pd_ganados,
            "xp_ganada": self.xp_ganada,
            "ejercicios_data": [e.to_dict() for e in self.ejercicios],
            "miniboss_aprobado": self.miniboss_aprobado,
            "endless_streak": self.endless_streak,
            "completado_en": self.completado_en.isoformat(),
            "duracion_segundos": self.duracion_segundos
        }


@dataclass
class UserOperationState:
    """
    Estado actual de una operación para un usuario
    
    Attributes:
        user_ref: ID del usuario
        operacion: Tipo de operación
        nivel_dominio: Nivel de dominio visible (1-5)
        nivel_invisible: Nivel invisible real (1.0-6.0)
        pd_operacion: Puntos de dominio en esta operación
        unlocked: Si la operación está desbloqueada
        miniboss_completed: Si completó el miniboss de nivel actual
        miniboss_attempts: Intentos de miniboss
        batches_desde_ultimo_miniboss: Batches completados desde último miniboss
        miniboss_fallos_consecutivos: Fallos consecutivos en miniboss
        total_ejercicios: Total de ejercicios realizados
        total_correctos: Total de ejercicios correctos
    """
    user_ref: str
    operacion: str
    nivel_dominio: int = 1
    nivel_invisible: float = 1.0
    pd_operacion: int = 0
    unlocked: bool = True
    miniboss_completed: bool = False
    miniboss_attempts: int = 0
    batches_desde_ultimo_miniboss: int = 0
    miniboss_fallos_consecutivos: int = 0
    total_ejercicios: int = 0
    total_correctos: int = 0
    
    @property
    def accuracy(self) -> float:
        """Precisión histórica (0.0 a 1.0)"""
        if self.total_ejercicios == 0:
            return 0.0
        return self.total_correctos / self.total_ejercicios
    
    @classmethod
    def from_db_record(cls, record: dict) -> 'UserOperationState':
        """Crea instancia desde registro de BD"""
        return cls(
            user_ref=record.get("user_ref") or "",
            operacion=record.get("operacion") or "",
            nivel_dominio=record.get("nivel_dominio") if record.get("nivel_dominio") is not None else 1,
            nivel_invisible=record.get("nivel_invisible") if record.get("nivel_invisible") is not None else 1.0,
            pd_operacion=record.get("pd_operacion") or 0,
            unlocked=record.get("unlocked", True),
            miniboss_completed=record.get("miniboss_completed", False),
            miniboss_attempts=record.get("miniboss_attempts") or 0,
            batches_desde_ultimo_miniboss=record.get("batches_desde_ultimo_miniboss") or 0,
            miniboss_fallos_consecutivos=record.get("miniboss_fallos_consecutivos") or 0,
            total_ejercicios=record.get("total_ejercicios") or 0,
            total_correctos=record.get("total_correctos") or 0
        )


@dataclass
class UserGamificationState:
    """
    Estado global de gamificación de un usuario
    
    Attributes:
        user_ref: ID del usuario
        pp_total: Puntos de práctica totales
        pd_global: Puntos de dominio globales
        xp_total: Experiencia total
        nivel_jugador: Nivel del jugador
        racha_dias: Racha actual en días
        racha_maxima: Racha máxima histórica
        dias_validos_streak: Días con 4+ aciertos
    """
    user_ref: str
    pp_total: int = 0
    pd_global: int = 0
    xp_total: int = 0
    nivel_jugador: int = 1
    racha_dias: int = 0
    racha_maxima: int = 0
    dias_validos_streak: int = 0
    racha_ultima_fecha: Optional[str] = None
    
    @classmethod
    def from_db_record(cls, record: dict) -> 'UserGamificationState':
        """Crea instancia desde registro de BD"""
        return cls(
            user_ref=record.get("user_ref") or "",
            pp_total=record.get("pp_total") or 0,
            pd_global=record.get("pd_global") or 0,
            xp_total=record.get("xp_total") or 0,
            nivel_jugador=record.get("nivel_jugador") if record.get("nivel_jugador") is not None else 1,
            racha_dias=record.get("racha_dias") or 0,
            racha_maxima=record.get("racha_maxima") or 0,
            dias_validos_streak=record.get("dias_validos_streak") or 0,
            racha_ultima_fecha=record.get("racha_ultima_fecha")
        )
