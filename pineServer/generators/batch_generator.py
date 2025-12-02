"""
Standard implementation of batch generator
Creates balanced sets of exercises based on unlocked operations
"""

import random
from typing import List, Dict, Set
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
        num_exercises: int,
        unlocked_operations: List[str] = None
    ) -> List[Exercise]:
        """
        Generate a balanced batch of exercises based on unlocked operations
        
        Args:
            difficulty_by_operator: Difficulty level for each operator
            num_exercises: Number of exercises to generate
            unlocked_operations: List of unlocked operators (e.g., ['+', '-', '*'])
                                If None, generates for all operators (legacy behavior)
        
        Returns:
            List of Exercise objects
        """
        # Map operator symbols to Operator enum
        operator_map = {
            '+': Operator.ADD,
            '-': Operator.SUBTRACT,
            '*': Operator.MULTIPLY,
            '/': Operator.DIVIDE
        }
        
        # If no unlock info provided, use all operators (legacy mode)
        if unlocked_operations is None:
            unlocked_operations = ['+', '-', '*', '/']
        
        # Filter to only unlocked operators
        available_operators = [
            operator_map[op] 
            for op in unlocked_operations 
            if op in operator_map
        ]
        
        if not available_operators:
            # Fallback: if nothing is unlocked, at least give them addition
            print("[WARNING] No unlocked operations found, defaulting to addition")
            available_operators = [Operator.ADD]
        
        # Create distribution based on number of unlocked operations
        operator_distribution = self._create_distribution(
            available_operators,
            num_exercises
        )
        
        # Shuffle for randomness
        random.shuffle(operator_distribution)
        
        # Generate exercises using the problem generator
        exercises = []
        for operator in operator_distribution[:num_exercises]:
            difficulty = difficulty_by_operator.get(operator.value, 1.0)
            exercise = self.problem_generator.generate_problem(operator, difficulty)
            exercises.append(exercise)
        
        return exercises
    
    def _create_distribution(
        self,
        available_operators: List[Operator],
        num_exercises: int
    ) -> List[Operator]:
        """
        Create operator distribution based on what's available
        
        Strategy:
        - 1 operation: 100% that operation
        - 2 operations: 60/40 split
        - 3 operations: 50/30/20 split
        - 4 operations: 40/25/20/15 split
        """
        num_ops = len(available_operators)
        
        if num_ops == 1:
            # Only one operation unlocked - use it 100%
            return [available_operators[0]] * num_exercises
        
        elif num_ops == 2:
            # Two operations - 60/40 split
            count_1 = int(num_exercises * 0.6)
            count_2 = num_exercises - count_1
            return (
                [available_operators[0]] * count_1 +
                [available_operators[1]] * count_2
            )
        
        elif num_ops == 3:
            # Three operations - 50/30/20 split
            count_1 = int(num_exercises * 0.5)
            count_2 = int(num_exercises * 0.3)
            count_3 = num_exercises - count_1 - count_2
            return (
                [available_operators[0]] * count_1 +
                [available_operators[1]] * count_2 +
                [available_operators[2]] * count_3
            )
        
        else:  # 4 operations
            # Four operations - 40/25/20/15 split
            count_1 = int(num_exercises * 0.4)
            count_2 = int(num_exercises * 0.25)
            count_3 = int(num_exercises * 0.2)
            count_4 = num_exercises - count_1 - count_2 - count_3
            return (
                [available_operators[0]] * count_1 +
                [available_operators[1]] * count_2 +
                [available_operators[2]] * count_3 +
                [available_operators[3]] * count_4
            )
