"""
DefaultConfigManager - Default implementation of IConfigManager

Manages configuration data loaded from database with caching.
Migrated from v2/config_manager.py
"""

from typing import Dict, Any, Optional
from v2.interfaces import IConfigManager
from roble_client import roble_client


class DefaultConfigManager(IConfigManager):
    """
    Default configuration manager that loads from database and caches.
    """
    
    def __init__(self):
        self._difficulty_cache: Dict[str, Dict[int, Dict]] = {}
        self._batch_config: Optional[Dict[str, Any]] = None
        self._scoring_config: Optional[Dict[str, Any]] = None
        self._miniboss_config: Optional[Dict[str, Any]] = None
        self._streak_config: Optional[Dict[str, Any]] = None
        self._loaded = False
        
    def _ensure_loaded(self):
        """Lazy load configuration from database."""
        if self._loaded:
            return
            
        try:
            # Load difficulty configs
            diff_records = roble_client.read_table("pine_v2_config_dificultad", {})
            for rec in diff_records:
                op = rec.get("operacion")
                nivel = rec.get("nivel")
                if op and nivel:
                    if op not in self._difficulty_cache:
                        self._difficulty_cache[op] = {}
                    self._difficulty_cache[op][nivel] = rec
                    
            # Load batch config
            batch_records = roble_client.read_table("pine_v2_config_batch", {})
            if batch_records:
                self._batch_config = batch_records[0]
            else:
                self._batch_config = self._get_default_batch_config()
                
            # Load scoring config  
            scoring_records = roble_client.read_table("pine_v2_config_scoring", {})
            if scoring_records:
                self._scoring_config = scoring_records[0]
            else:
                self._scoring_config = self._get_default_scoring_config()
                
            # Load miniboss config
            miniboss_records = roble_client.read_table("pine_v2_config_miniboss", {})
            if miniboss_records:
                self._miniboss_config = miniboss_records[0]
            else:
                self._miniboss_config = self._get_default_miniboss_config()
                
            # Load streak config
            streak_records = roble_client.read_table("pine_v2_config_streak", {})
            if streak_records:
                self._streak_config = streak_records[0]
            else:
                self._streak_config = self._get_default_streak_config()
                
            self._loaded = True
            print(f"[ConfigManager] Loaded configs: {len(self._difficulty_cache)} operations")
            
        except Exception as e:
            print(f"[ConfigManager] Error loading configs: {e}")
            # Use defaults on error
            self._batch_config = self._get_default_batch_config()
            self._scoring_config = self._get_default_scoring_config()
            self._miniboss_config = self._get_default_miniboss_config()
            self._streak_config = self._get_default_streak_config()
            self._loaded = True
    
    def get_difficulty_config(self, operacion: str, nivel: int) -> Optional[Dict[str, Any]]:
        """Get difficulty configuration for an operation at a specific level."""
        self._ensure_loaded()
        if operacion in self._difficulty_cache:
            return self._difficulty_cache[operacion].get(nivel)
        return None
    
    def get_batch_config(self) -> Dict[str, Any]:
        """Get batch configuration (size, distribution)."""
        self._ensure_loaded()
        return self._batch_config or self._get_default_batch_config()
    
    def get_scoring_config(self) -> Dict[str, Any]:
        """Get scoring multipliers and bonuses."""
        self._ensure_loaded()
        return self._scoring_config or self._get_default_scoring_config()
    
    def get_miniboss_config(self) -> Dict[str, Any]:
        """Get miniboss thresholds and requirements."""
        self._ensure_loaded()
        return self._miniboss_config or self._get_default_miniboss_config()
    
    def get_streak_config(self) -> Dict[str, Any]:
        """Get streak requirements and limits."""
        self._ensure_loaded()
        return self._streak_config or self._get_default_streak_config()
    
    def reload(self):
        """Force reload of all configurations."""
        self._loaded = False
        self._difficulty_cache.clear()
        self._ensure_loaded()
    
    # Default configurations
    def _get_default_batch_config(self) -> Dict[str, Any]:
        return {
            "size": 10,
            "distribution_easy": 2,
            "distribution_central": 6,
            "distribution_hard": 2
        }
    
    def _get_default_scoring_config(self) -> Dict[str, Any]:
        return {
            "base_multiplier": 5,
            "participation_bonus": 10,
            "error_penalty": 2
        }
    
    def _get_default_miniboss_config(self) -> Dict[str, Any]:
        return {
            "min_batches_after_fail": 3,
            "nivel_invisible_threshold": 0.5,
            "min_correct_rate": 0.8
        }
    
    def _get_default_streak_config(self) -> Dict[str, Any]:
        return {
            "min_correct": 4,
            "max_days": 30
        }
