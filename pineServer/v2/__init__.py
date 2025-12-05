"""
Gamificación V2 - Sistema modular y configurable

Este paquete contiene la implementación del nuevo motor de gamificación
que usa nivel invisible, configuraciones dinámicas y tracking detallado.
"""

__version__ = "2.0.0"
__author__ = "PineServer Team"

# Importaciones principales para facilitar el uso
from .config_manager import ConfigManager

__all__ = [
    "ConfigManager",
]
