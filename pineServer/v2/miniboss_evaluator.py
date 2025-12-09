"""
MinibossEvaluator - Juez de Miniboss V2

Evalúa si un batch de Miniboss fue aprobado exitosamente.
"""

import sys
import os
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from v2.models import ExerciseResult
from v2.config_manager import get_config_manager

class MinibossEvaluator:
    
    def __init__(self):
        self.config_manager = get_config_manager()
        
    def evaluate_miniboss(self, resultados: List[ExerciseResult]) -> bool:
        """
        Determina si se aprobó el miniboss
        
        Args:
            resultados: Lista de resultados del batch Miniboss
            
        Returns:
            True si aprobó (Level Up), False si falló
        """
        if not resultados:
            return False
            
        mb_config = self.config_manager.get_miniboss_config()
        min_rate = mb_config.get("min_correct_rate", 0.8) # 80% default
        
        total = len(resultados)
        correctos = sum(1 for r in resultados if r.es_correcto)
        rate = correctos / total
        
        passed = rate >= min_rate
        
        if passed:
            print(f"[Miniboss] APROBADO: {correctos}/{total} ({rate:.1%}) >= {min_rate:.1%}")
        else:
            print(f"[Miniboss] FALLADO: {correctos}/{total} ({rate:.1%}) < {min_rate:.1%}")
            
        return passed

# Singleton
_mb_evaluator_instance = None
def get_miniboss_evaluator():
    global _mb_evaluator_instance
    if _mb_evaluator_instance is None:
        _mb_evaluator_instance = MinibossEvaluator()
    return _mb_evaluator_instance
