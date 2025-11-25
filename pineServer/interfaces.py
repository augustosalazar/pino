"""
Interfaces for dependency injection
Defines contracts for swappable components
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from models import Exercise, ExerciseWithAnswer, Operator


class IProblemGenerator(ABC):
    """Interface for generating a single problem"""
    
    @abstractmethod
    def generate_problem(self, operator: Operator, difficulty: float) -> Exercise:
        """
        Generate a single exercise problem
        
        Args:
            operator: The mathematical operator (+, -, *, /)
            difficulty: Difficulty level (1.0 to 10.0)
            
        Returns:
            Exercise: A single exercise with problem and answer
        """
        pass


class IBatchGenerator(ABC):
    """Interface for generating batches of exercises"""
    
    @abstractmethod
    def generate_batch(
        self,
        difficulty_by_operator: Dict[str, float],
        num_exercises: int
    ) -> List[Exercise]:
        """
        Generate a batch of exercises based on difficulty profile
        
        Args:
            difficulty_by_operator: Dict mapping operator ('+', '-', etc.) to difficulty
            num_exercises: Number of exercises to generate
            
        Returns:
            List[Exercise]: Batch of exercises
        """
        pass


class IProfileEvaluator(ABC):
    """Interface for evaluating user performance and adjusting difficulty"""
    
    @abstractmethod
    def evaluate_performance(
        self,
        exercises: List[ExerciseWithAnswer],
        current_difficulty: Dict[str, float]
    ) -> Tuple[Dict[str, float], List[Dict]]:
        """
        Evaluate user performance and calculate difficulty adjustments
        
        Args:
            exercises: List of completed exercises with answers
            current_difficulty: Current difficulty levels by operator
            
        Returns:
            Tuple containing:
                - new_difficulty: Updated difficulty levels
                - adjustment_records: List of adjustment details for logging
        """
        pass
    
    @abstractmethod
    def calculate_score(self, exercises: List[ExerciseWithAnswer]) -> int:
        """
        Calculate score earned from completed exercises
        
        Args:
            exercises: List of completed exercises with answers
            
        Returns:
            int: Total score earned
        """
        pass
