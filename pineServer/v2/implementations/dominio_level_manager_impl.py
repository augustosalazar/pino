"""
DefaultDominioLevelManager - Default implementation of IDominioLevelManager

Manages domain level calculations and thresholds.
"""

from v2.interfaces import IDominioLevelManager, IConfigManager


class DefaultDominioLevelManager(IDominioLevelManager):
    """
    Default domain level manager that calculates theoretical levels
    based on invisible level thresholds.
    """
    
    def __init__(self, container=None):
        self._container = container
        # Level thresholds: invisible level >= threshold -> domain level
        self._thresholds = [
            (1.0, 1),
            (2.0, 2),
            (3.0, 3),
            (4.0, 4),
            (5.0, 5),
        ]
    
    def get_nivel_dominio_teorico(self, nivel_invisible: float) -> int:
        """
        Get the theoretical domain level based on invisible level.
        
        Args:
            nivel_invisible: Current invisible level (float)
            
        Returns:
            Corresponding domain level (1-5)
        """
        nivel_dominio = 1
        for threshold, level in self._thresholds:
            if nivel_invisible >= threshold:
                nivel_dominio = level
            else:
                break
        return nivel_dominio
