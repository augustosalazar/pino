"""
Standard implementation of batch generator
Creates balanced sets of exercises
"""

import random
from typing import List, Dict
from models import Exercise, Operator
from interfaces import IBatchGenerator, IProblemGenerator


class StandardBatchGenerator(IBatchGenerator):
    """Standard implementation for generating exercise batches"""
    
    def __init__(self, problem_generator: IProblemGenerator):
        """
        Initialize with a problem generator
        
        Args:
            problem_generator: Implementation of IProblemGenerator
        """
        self.problem_generator = problem_generator
    
    def generate_batch(
        self,
        difficulty_by_operator: Dict[str, float],
        num_exercises: int
    ) -> List[Exercise]:
        """
        Generate a balanced batch of exercises
        
        Default distribution: 40% +, 20% -, 20% *, 20% /
        """
        # Create balanced operator distribution
        operator_distribution = (
            [Operator.ADD] * 4 +
            [Operator.SUBTRACT] * 2 +
            [Operator.MULTIPLY] * 2 +
            [Operator.DIVIDE] * 2
        )
        
        # Adjust for custom num_exercises
        if num_exercises != 10:
            ratio = num_exercises / 10
            operator_distribution = [Operator.ADD] * int(4 * ratio)
            operator_distribution += [Operator.SUBTRACT] * int(2 * ratio)
            operator_distribution += [Operator.MULTIPLY] * int(2 * ratio)
            operator_distribution += [Operator.DIVIDE] * (num_exercises - len(operator_distribution))
        
        # Shuffle for randomness
        random.shuffle(operator_distribution)
        
        # Generate exercises using the problem generator
        exercises = []
        for operator in operator_distribution[:num_exercises]:
            difficulty = difficulty_by_operator.get(operator.value, 1.0)
            exercise = self.problem_generator.generate_problem(operator, difficulty)
            exercises.append(exercise)
        
        return exercises
