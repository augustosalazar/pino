"""
ConfigManager - Gestión centralizada de configuraciones V2

Lee y cachea configuraciones desde las tablas:
- pine_configuracion_sistema: Parámetros generales (scoring, streak, etc.)
- pine_configuracion_dificultad: Configuraciones por operación y nivel

El cache en memoria mejora el performance evitando lecturas repetidas a la BD.
"""

import sys
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from roble_client import roble_client


class ConfigManager:
    """
    Gestor de configuraciones para el sistema de gamificación V2
    
    Características:
    - Cache en memoria con TTL de 5 minutos
    - Lectura lazy (solo cuando se necesita)
    - Métodos helper para acceso fácil a configs comunes
    """
    
    def __init__(self):
        """Inicializa el ConfigManager con caches vacíos"""
        self._system_config_cache: Dict[str, Any] = {}
        self._difficulty_config_cache: Dict[str, Dict] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
    
    def _is_cache_valid(self) -> bool:
        """Verifica si el cache sigue siendo válido"""
        if self._cache_timestamp is None:
            return False
        return datetime.utcnow() - self._cache_timestamp < self._cache_ttl
    
    def _refresh_cache_if_needed(self):
        """Refresca el cache si ha expirado"""
        if not self._is_cache_valid():
            self._load_system_config()
            self._load_difficulty_config()
            self._cache_timestamp = datetime.utcnow()
    
    def _load_system_config(self):
        """Carga todas las configuraciones del sistema desde la BD"""
        try:
            configs = roble_client.read_table("pine_configuracion_sistema", {"activa": True})
            
            if not configs:
                print("[ConfigManager] Warning: No system configurations found")
                return
            
            # Convertir a dict key -> value
            for config in configs:
                key = config.get("config_key")
                value_json = config.get("config_value")
                
                if key and value_json:
                    try:
                        # Si config_value ya es un dict (Roble lo parseó), úsalo directamente
                        if isinstance(value_json, dict):
                            value_dict = value_json
                        else:
                            # Si es string JSON, parsearlo
                            value_dict = json.loads(value_json)
                        
                        # Extraer el valor real del dict {"value": X, "type": "Y"}
                        self._system_config_cache[key] = value_dict.get("value")
                    except json.JSONDecodeError:
                        print(f"[ConfigManager] Error parsing config_value for {key}")
            
            print(f"[ConfigManager] Loaded {len(self._system_config_cache)} system configs")
            
        except Exception as e:
            print(f"[ConfigManager] Error loading system config: {e}")
    
    def _load_difficulty_config(self):
        """Carga todas las configuraciones de dificultad desde la BD"""
        try:
            configs = roble_client.read_table("pine_configuracion_dificultad", {"activa": True})
            
            if not configs:
                print("[ConfigManager] Warning: No difficulty configurations found")
                return
            
            # Organizar por operacion_nivel como clave
            for config in configs:
                operacion = config.get("operacion")
                nivel = config.get("nivel")
                
                if operacion and nivel is not None:
                    key = f"{operacion}_{nivel}"
                    self._difficulty_config_cache[key] = config
            
            print(f"[ConfigManager] Loaded {len(self._difficulty_config_cache)} difficulty configs")
            
        except Exception as e:
            print(f"[ConfigManager] Error loading difficulty config: {e}")
    
    def get_system_config(self, key: str, default: Any = None) -> Any:
        """
        Obtiene una configuración del sistema por su clave
        
        Args:
            key: Clave de la configuración (ej: "scoring.base_multiplier")
            default: Valor por defecto si no existe
            
        Returns:
            El valor de la configuración o el default
            
        Example:
            >>> config_mgr.get_system_config("scoring.base_multiplier")
            5
        """
        self._refresh_cache_if_needed()
        return self._system_config_cache.get(key, default)
    
    def get_difficulty_config(self, operacion: str, nivel: int) -> Optional[Dict]:
        """
        Obtiene la configuración de dificultad para una operación y nivel
        
        Args:
            operacion: Tipo de operación ("suma", "resta", "mult", "div")
            nivel: Nivel de 1 a 5
            
        Returns:
            Dict con la configuración completa o None si no existe
            
        Example:
            >>> config = config_mgr.get_difficulty_config("suma", 1)
            >>> config["min_operando_1"]
            0
        """
        self._refresh_cache_if_needed()
        key = f"{operacion}_{nivel}"
        return self._difficulty_config_cache.get(key)
    
    # === MÉTODOS HELPER PARA CONFIGURACIONES COMUNES ===
    
    def get_scoring_config(self) -> Dict[str, Any]:
        """
        Obtiene toda la configuración de scoring
        
        Returns:
            Dict con base_multiplier, participation_bonus, error_penalty
        """
        return {
            "base_multiplier": self.get_system_config("scoring.base_multiplier", 5),
            "participation_bonus": self.get_system_config("scoring.participation_bonus", 10),
            "error_penalty": self.get_system_config("scoring.error_penalty", 2),
        }
    
    def get_streak_config(self) -> Dict[str, Any]:
        """
        Obtiene toda la configuración de streak
        
        Returns:
            Dict con min_correct, base_score, daily_multiplier, max_days
        """
        return {
            "min_correct": self.get_system_config("streak.min_correct", 4),
            "base_score": self.get_system_config("streak.base_score", 5),
            "daily_multiplier": self.get_system_config("streak.daily_multiplier", 3),
            "max_days": self.get_system_config("streak.max_days", 30),
        }
    
    def get_miniboss_config(self) -> Dict[str, Any]:
        """
        Obtiene toda la configuración de miniboss
        
        Returns:
            Dict con min_batches_after_fail, min_correct_rate, nivel_invisible_threshold
        """
        return {
            "min_batches_after_fail": self.get_system_config("miniboss.min_batches_after_fail", 3),
            "min_correct_rate": self.get_system_config("miniboss.min_correct_rate", 0.8),
            "nivel_invisible_threshold": self.get_system_config("miniboss.nivel_invisible_threshold", 0.5),
        }
    
    def get_batch_config(self) -> Dict[str, Any]:
        """
        Obtiene toda la configuración de batch
        
        Returns:
            Dict con size, distribution_easy, distribution_central, distribution_hard
        """
        return {
            "size": self.get_system_config("batch.size", 10),
            "distribution_easy": self.get_system_config("batch.distribution_easy", 2),
            "distribution_central": self.get_system_config("batch.distribution_central", 6),
            "distribution_hard": self.get_system_config("batch.distribution_hard", 2),
        }
    
    def get_practice_points_config(self) -> Dict[str, Any]:
        """
        Obtiene toda la configuración de puntos de práctica
        
        Returns:
            Dict con chest_interval
        """
        return {
            "chest_interval": self.get_system_config("practice_points.chest_interval", 100),
        }
    
    def invalidate_cache(self):
        """
        Invalida el cache forzando una recarga en el próximo acceso
        
        Útil cuando se actualizan configuraciones en la BD
        """
        self._cache_timestamp = None
        print("[ConfigManager] Cache invalidated")
    
    def get_all_system_configs(self) -> Dict[str, Any]:
        """
        Obtiene todas las configuraciones del sistema
        
        Returns:
            Dict completo con todas las configuraciones
        """
        self._refresh_cache_if_needed()
        return self._system_config_cache.copy()
    
    def get_all_difficulty_configs(self) -> Dict[str, Dict]:
        """
        Obtiene todas las configuraciones de dificultad
        
        Returns:
            Dict completo con todas las configuraciones de dificultad
        """
        self._refresh_cache_if_needed()
        return self._difficulty_config_cache.copy()


# Singleton instance
_config_manager_instance = None


def get_config_manager() -> ConfigManager:
    """
    Obtiene la instancia singleton del ConfigManager
    
    Returns:
        Instancia única de ConfigManager
    """
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()
    return _config_manager_instance
