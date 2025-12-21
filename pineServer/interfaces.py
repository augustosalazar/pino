"""
Interfaces for Dependency Injection

Defines contracts for all injectable components in the gamification system.
Each interface can have multiple implementations that can be swapped via the container.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


class IExerciseGenerator(ABC):
    """Generates individual math exercises."""
    
    @abstractmethod
    def generate_exercise(self, operacion: str, nivel_invisible: float) -> 'Exercise':
        """Generate a single exercise based on operation and difficulty level."""
        pass


class IBatchGenerator(ABC):
    """Generates batches of exercises with proper distribution."""
    
    @abstractmethod
    def generate_batch(
        self,
        user_ref: str,
        operacion: str,
        nivel_invisible: float,
        batch_type: str,
        forced_exercises: Optional[List] = None,
        num_exercises: int = 10
    ) -> List:
        """Generate a batch of exercises."""
        pass


class IPerformanceEvaluator(ABC):
    """Evaluates user performance and adjusts difficulty."""
    
    @abstractmethod
    def evaluate_performance(
        self,
        resultados: List,
        nivel_invisible_actual: float
    ) -> float:
        """Evaluate performance and return new invisible level."""
        pass


class IScoringCalculator(ABC):
    """Calculates scores and rewards (PP, PD, XP)."""
    
    @abstractmethod
    def calculate_score_parts(self, resultados: List) -> Dict[str, int]:
        """Calculate score breakdown with total, base, bonus, penalty."""
        pass
    
    @abstractmethod
    def calculate_score(self, resultados: List) -> int:
        """Calculate total score."""
        pass
    
    @abstractmethod
    def calculate_pp(self, resultados: List) -> int:
        """Calculate Practice Points."""
        pass
    
    @abstractmethod
    def calculate_pd(self, resultados: List) -> int:
        """Calculate Domain Points."""
        pass
    
    @abstractmethod
    def calculate_xp(self, resultados: List) -> int:
        """Calculate Experience Points."""
        pass


class IMinibossDetector(ABC):
    """Detects when a user is ready for a miniboss challenge."""
    
    @abstractmethod
    def is_miniboss_candidate(self, state) -> bool:
        """Check if user should face a miniboss."""
        pass
    
    @abstractmethod
    def get_next_level_target(self, state) -> int:
        """Get the level user would achieve if they pass."""
        pass


class IMinibossEvaluator(ABC):
    """Evaluates miniboss results."""
    
    @abstractmethod
    def evaluate_miniboss(self, resultados: List) -> bool:
        """Determine if miniboss was passed (True = level up)."""
        pass


class IBatchRecorder(ABC):
    """Records batch results and updates user state."""
    
    @abstractmethod
    def record_batch(self, result, current_gamif_state) -> bool:
        """Record batch results to database. Returns True on success."""
        pass


class IConfigManager(ABC):
    """Provides configuration data."""
    
    @abstractmethod
    def get_difficulty_config(self, operacion: str, nivel: int) -> Optional[Dict]:
        """Get difficulty config for operation at level."""
        pass
    
    @abstractmethod
    def get_batch_config(self) -> Dict[str, Any]:
        """Get batch configuration."""
        pass
    
    @abstractmethod
    def get_scoring_config(self) -> Dict[str, Any]:
        """Get scoring configuration."""
        pass
    
    @abstractmethod
    def get_miniboss_config(self) -> Dict[str, Any]:
        """Get miniboss configuration."""
        pass
    
    @abstractmethod
    def get_streak_config(self) -> Dict[str, Any]:
        """Get streak configuration."""
        pass


class IDominioLevelManager(ABC):
    """Manages domain level calculations."""
    
    @abstractmethod
    def get_nivel_dominio_teorico(self, nivel_invisible: float) -> int:
        """Get theoretical domain level based on invisible level."""
        pass
