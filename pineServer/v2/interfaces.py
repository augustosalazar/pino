"""
V2 Interfaces - Abstract contracts for injectable components

These interfaces define the contracts that implementations must follow,
enabling dependency injection and easy swapping of implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


class IExerciseGenerator(ABC):
    """
    Interface for generating individual exercises.
    Implementations control how single exercises are created based on operation and difficulty.
    """
    
    @abstractmethod
    def generate_exercise(self, operacion: str, nivel_invisible: float) -> 'Exercise':
        """
        Generate a single exercise.
        
        Args:
            operacion: Operation type ('suma', 'resta', 'mult', 'div')
            nivel_invisible: Invisible difficulty level (float, e.g., 2.5)
            
        Returns:
            Exercise instance
        """
        pass


class IBatchGenerator(ABC):
    """
    Interface for generating batches of exercises.
    Implementations control batch composition and exercise distribution.
    """
    
    @abstractmethod
    def generate_batch(
        self,
        user_ref: str,
        operacion: str,
        nivel_invisible: float,
        batch_type: str,
        forced_exercises: Optional[List['Exercise']] = None,
        num_exercises: int = 10
    ) -> List['Exercise']:
        """
        Generate a batch of exercises.
        
        Args:
            user_ref: User identifier
            operacion: Main operation type
            nivel_invisible: Central difficulty level
            batch_type: Type of batch (regular, miniboss, endless)
            forced_exercises: Pre-defined exercises to include (e.g., review items)
            num_exercises: Number of exercises to generate
            
        Returns:
            List of Exercise objects
        """
        pass


class IPerformanceEvaluator(ABC):
    """
    Interface for evaluating user performance and adjusting difficulty.
    Implementations control how performance impacts the invisible level.
    """
    
    @abstractmethod
    def evaluate_performance(
        self,
        resultados: List['ExerciseResult'],
        nivel_invisible_actual: float
    ) -> float:
        """
        Evaluate performance and calculate new invisible level.
        
        Args:
            resultados: List of exercise results from the batch
            nivel_invisible_actual: Current invisible level before the batch
            
        Returns:
            New invisible level (clamped between min and max)
        """
        pass


class IScoringCalculator(ABC):
    """
    Interface for calculating scores and rewards.
    Implementations control scoring formulas for PP, PD, XP, and total score.
    """
    
    @abstractmethod
    def calculate_score_parts(self, resultados: List['ExerciseResult']) -> Dict[str, int]:
        """
        Calculate score breakdown.
        
        Args:
            resultados: List of exercise results
            
        Returns:
            Dict with 'total', 'base', 'bonus', 'penalty' keys
        """
        pass
    
    @abstractmethod
    def calculate_score(self, resultados: List['ExerciseResult']) -> int:
        """Calculate total score."""
        pass
    
    @abstractmethod
    def calculate_pp(self, resultados: List['ExerciseResult']) -> int:
        """Calculate Practice Points (PP)."""
        pass
    
    @abstractmethod
    def calculate_pd(self, resultados: List['ExerciseResult']) -> int:
        """Calculate Domain Points (PD)."""
        pass
    
    @abstractmethod
    def calculate_xp(self, resultados: List['ExerciseResult']) -> int:
        """Calculate Experience Points (XP)."""
        pass


class IMinibossDetector(ABC):
    """
    Interface for detecting when a user is ready for a miniboss challenge.
    Implementations control the criteria for miniboss triggers.
    """
    
    @abstractmethod
    def is_miniboss_candidate(self, state: 'UserOperationState') -> bool:
        """
        Check if user is ready for a miniboss.
        
        Args:
            state: Current operation state for the user
            
        Returns:
            True if miniboss should be generated
        """
        pass
    
    @abstractmethod
    def get_next_level_target(self, state: 'UserOperationState') -> int:
        """Get the level the user would achieve if they pass the miniboss."""
        pass


class IMinibossEvaluator(ABC):
    """
    Interface for evaluating miniboss results.
    Implementations control pass/fail criteria for level advancement.
    """
    
    @abstractmethod
    def evaluate_miniboss(self, resultados: List['ExerciseResult']) -> bool:
        """
        Determine if the miniboss was passed.
        
        Args:
            resultados: List of miniboss exercise results
            
        Returns:
            True if passed (level up), False if failed
        """
        pass


class IBatchRecorder(ABC):
    """
    Interface for recording batch results and updating user state.
    Implementations control persistence logic.
    """
    
    @abstractmethod
    def record_batch(
        self,
        result: 'BatchResult',
        current_gamif_state: 'UserGamificationState'
    ) -> bool:
        """
        Record batch results and update all related state.
        
        Args:
            result: Complete batch result data
            current_gamif_state: Current gamification state for streak calculations
            
        Returns:
            True if all updates succeeded
        """
        pass


class IConfigManager(ABC):
    """
    Interface for accessing configuration data.
    Implementations control how configuration is loaded and cached.
    """
    
    @abstractmethod
    def get_difficulty_config(self, operacion: str, nivel: int) -> Optional[Dict[str, Any]]:
        """Get difficulty configuration for an operation at a specific level."""
        pass
    
    @abstractmethod
    def get_batch_config(self) -> Dict[str, Any]:
        """Get batch configuration (size, distribution)."""
        pass
    
    @abstractmethod
    def get_scoring_config(self) -> Dict[str, Any]:
        """Get scoring multipliers and bonuses."""
        pass
    
    @abstractmethod
    def get_miniboss_config(self) -> Dict[str, Any]:
        """Get miniboss thresholds and requirements."""
        pass
    
    @abstractmethod
    def get_streak_config(self) -> Dict[str, Any]:
        """Get streak requirements and limits."""
        pass


class IDominioLevelManager(ABC):
    """
    Interface for managing domain level calculations.
    Implementations control level thresholds and conversions.
    """
    
    @abstractmethod
    def get_nivel_dominio_teorico(self, nivel_invisible: float) -> int:
        """Get the theoretical domain level based on invisible level."""
        pass
