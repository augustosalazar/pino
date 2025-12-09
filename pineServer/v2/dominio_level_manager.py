"""
DominioLevelManager - Gestión de niveles visibles V2

Maneja la relación entre el nivel invisible (interno) y el nivel de dominio (visible).
Registra cambios de nivel y asegura que el nivel visible nunca baje.
"""

import math
from typing import Optional, Tuple
from datetime import datetime

# Import roble_client para logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from roble_client import roble_client

class DominioLevelManager:
    
    def get_nivel_dominio_teorico(self, nivel_invisible: float) -> int:
        """
        Calcula qué nivel de dominio (1-5) corresponde a un nivel invisible.
        Mapeo:
          1.0 - 1.99 -> Nivel 1
          2.0 - 2.99 -> Nivel 2
          ...
          5.0+       -> Nivel 5
        """
        # Floor simple, clamp entre 1 y 5
        nivel = int(math.floor(nivel_invisible))
        return max(1, min(nivel, 5))

    def detect_potential_level_change(self, 
                                    nivel_dominio_actual: int, 
                                    nivel_invisible_nuevo: float) -> Optional[int]:
        """
        Detecta si el usuario debería cambiar de nivel visible.
        
        Regla: "El nivel visible se incrementa únicamente cuando el usuario supera un miniboss"
        Por lo tanto, este manager SOLO detecta si el nivel teórico es superior al actual,
        lo cual es una pre-condición para activar un Miniboss.
        
        NO cambia el nivel automáticamente. El MinibossEvaluator hará eso.
        """
        teorico = self.get_nivel_dominio_teorico(nivel_invisible_nuevo)
        
        if teorico > nivel_dominio_actual:
            return teorico
        
        return None

    def log_level_change(self, user_ref: str, operacion: str, nivel_anterior: int, nivel_nuevo: int):
        """
        Registra el cambio de nivel en la base de datos
        """
        if nivel_nuevo == nivel_anterior:
            return

        try:
            record = {
                "user_ref": user_ref,
                "operacion": operacion,
                "nivel_anterior": nivel_anterior,
                "nivel_nuevo": nivel_nuevo,
                "motivo": "miniboss_completion" if nivel_nuevo > nivel_anterior else "adjustment",
                "created_at": datetime.utcnow().isoformat()
            }
            roble_client.insert_records("pine_nivel_dominio_log", [record])
            print(f"[LevelManager] Logged level change for {user_ref}: {nivel_anterior}->{nivel_nuevo}")
        except Exception as e:
            print(f"[LevelManager] Error logging level change: {e}")

# Singleton
_level_mgr_instance = None
def get_dominio_level_manager():
    global _level_mgr_instance
    if _level_mgr_instance is None:
        _level_mgr_instance = DominioLevelManager()
    return _level_mgr_instance
