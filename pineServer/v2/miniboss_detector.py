"""
MinibossDetector - Guardián de nivel V2

Determina si un usuario cumple los requisitos para enfrentar un Miniboss
y potencialmente subir de nivel visible.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v2.models import UserOperationState
from v2.config_manager import get_config_manager
from v2.dominio_level_manager import get_dominio_level_manager

class MinibossDetector:
    
    def __init__(self):
        self.config_manager = get_config_manager()
        self.level_manager = get_dominio_level_manager()
        
    def is_miniboss_candidate(self, state: UserOperationState) -> bool:
        """
        Verifica si el usuario es candidato para un Miniboss
        
        Args:
            state: Estado actual de la operación para el usuario
            
        Returns:
            True si debe generarse un batch de Miniboss
        """
        # 0. Si ya está en nivel máximo, no hay miniboss
        if state.nivel_dominio >= 5:
            return False
            
        # 1. Obtener configuración
        mb_config = self.config_manager.get_miniboss_config()
        min_batches = mb_config.get("min_batches_after_fail", 3)
        threshold = mb_config.get("nivel_invisible_threshold", 0.5)
        
        # 2. Check: Batches suficientes desde último intento
        # Esto previene spam de miniboss inmediatos después de fallar

        if state.batches_desde_ultimo_miniboss == None:
            return False

        if state.batches_desde_ultimo_miniboss < min_batches:
            return False
            
        # 3. Check: Nivel invisible suficiente
        # El nivel invisible debe superar al visible por un margen (threshold)
        # Ej: Visible 1, Threshold 0.5 -> Invisible debe ser >= 1.5
        required_invisible = state.nivel_dominio + threshold
        
        # Opcionalmente, usamos la lógica de LevelManager para ver si teóricamente ya es Nivel+1
        teorico = self.level_manager.get_nivel_dominio_teorico(state.nivel_invisible)
        
        # Si teóricamente ya es de un nivel superior, es candidato fuerte
        if teorico > state.nivel_dominio:
            return True
            
        # Si no llega al nivel entero pero pasa el threshold, también puede intentar
        if state.nivel_invisible >= required_invisible:
            return True
            
        return False
        
    def get_next_level_target(self, state: UserOperationState) -> int:
        """Retorna el nivel al que aspiraría el usuario"""
        return min(5, state.nivel_dominio + 1)

# Singleton
_mb_detector_instance = None
def get_miniboss_detector():
    global _mb_detector_instance
    if _mb_detector_instance is None:
        _mb_detector_instance = MinibossDetector()
    return _mb_detector_instance
