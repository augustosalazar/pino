"""
Gamificación V2 - Sistema modular y configurable

Este paquete contiene la implementación del nuevo motor de gamificación
que usa nivel invisible, configuraciones dinámicas y tracking detallado.
"""

__version__ = "2.0.0"
__author__ = "PineServer Team"

# Importaciones principales para facilitar el uso
from .config_manager import ConfigManager, get_config_manager
from .models import (
    Exercise,
    ExerciseResult,
    BatchResult,
    UserOperationState,
    UserGamificationState,
    Operacion,
    TipoRespuesta,
    BatchType
)

__all__ = [
    # Config
    "ConfigManager",
    "get_config_manager",
    # Models
    "Exercise",
    "ExerciseResult",
    "BatchResult",
    "UserOperationState",
    "UserGamificationState",
    # Enums
    "Operacion",
    "TipoRespuesta",
    "BatchType",
]
