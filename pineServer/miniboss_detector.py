"""
MinibossDetector - Detects when user is ready for miniboss

Implements IMinibossDetector interface.
"""

from interfaces import IMinibossDetector
from gamification_models import UserOperationState


class MinibossDetector(IMinibossDetector):
    """
    Detects miniboss eligibility based on invisible level and batch count.
    """
    
    def __init__(self, container=None):
        self._container = container
    
    @property
    def config_manager(self):
        if self._container:
            return self._container.config_manager
        from config_manager import get_config_manager
        return get_config_manager()
    
    @property
    def level_manager(self):
        if self._container:
            return self._container.dominio_level_manager
        from dominio_level_manager import get_dominio_level_manager
        return get_dominio_level_manager()
        
    def is_miniboss_candidate(self, state: UserOperationState) -> bool:
        """Check if user should face a miniboss."""
        if state.nivel_dominio >= 5:
            return False
            
        config = self.config_manager.get_miniboss_config()
        min_batches = config.get("min_batches_after_fail", 3)
        threshold = config.get("nivel_invisible_threshold", 0.5)
        
        if state.batches_desde_ultimo_miniboss is None:
            return False
        if state.batches_desde_ultimo_miniboss < min_batches:
            return False
            
        required = state.nivel_dominio + threshold
        teorico = self.level_manager.get_nivel_dominio_teorico(state.nivel_invisible)
        
        return teorico > state.nivel_dominio or state.nivel_invisible >= required
        
    def get_next_level_target(self, state: UserOperationState) -> int:
        """Get the level user would achieve if they pass."""
        return min(5, state.nivel_dominio + 1)


# Singleton accessor (backward compatibility)
_instance = None

def get_miniboss_detector():
    global _instance
    if _instance is None:
        _instance = MinibossDetector()
    return _instance
