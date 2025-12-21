"""
DefaultMinibossDetector - Default implementation of IMinibossDetector

Determines when a user is ready to face a miniboss challenge.
"""

from v2.interfaces import IMinibossDetector, IConfigManager, IDominioLevelManager
from v2.models import UserOperationState


class DefaultMinibossDetector(IMinibossDetector):
    """
    Default miniboss detector that checks eligibility criteria.
    """
    
    def __init__(self, container=None):
        self._container = container
    
    @property
    def config_manager(self) -> IConfigManager:
        from v2.container import get_v2_container
        if self._container:
            return self._container.config_manager
        return get_v2_container().config_manager
    
    @property
    def level_manager(self) -> IDominioLevelManager:
        from v2.container import get_v2_container
        if self._container:
            return self._container.dominio_level_manager
        return get_v2_container().dominio_level_manager
        
    def is_miniboss_candidate(self, state: UserOperationState) -> bool:
        """
        Check if user is ready for a miniboss.
        
        Args:
            state: Current operation state for the user
            
        Returns:
            True if miniboss should be generated
        """
        # 0. If already at max level, no miniboss
        if state.nivel_dominio >= 5:
            return False
            
        # 1. Get configuration
        mb_config = self.config_manager.get_miniboss_config()
        min_batches = mb_config.get("min_batches_after_fail", 3)
        threshold = mb_config.get("nivel_invisible_threshold", 0.5)
        
        # 2. Check: Sufficient batches since last attempt
        if state.batches_desde_ultimo_miniboss is None:
            return False

        if state.batches_desde_ultimo_miniboss < min_batches:
            return False
            
        # 3. Check: Sufficient invisible level
        required_invisible = state.nivel_dominio + threshold
        
        # Optionally, use LevelManager to check theoretical level
        teorico = self.level_manager.get_nivel_dominio_teorico(state.nivel_invisible)
        
        # If theoretically at a higher level, strong candidate
        if teorico > state.nivel_dominio:
            return True
            
        # If doesn't reach integer level but passes threshold, can attempt
        if state.nivel_invisible >= required_invisible:
            return True
            
        return False
        
    def get_next_level_target(self, state: UserOperationState) -> int:
        """Returns the level the user would achieve if they pass."""
        return min(5, state.nivel_dominio + 1)
