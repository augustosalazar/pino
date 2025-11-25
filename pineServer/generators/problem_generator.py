"""
Standard implementation of problem generator
Generates math problems with adaptive difficulty
"""

import random
from typing import List, Tuple
from models import Exercise, ExerciseType, Operator
from interfaces import IProblemGenerator


class StandardProblemGenerator(IProblemGenerator):
    """Standard implementation for generating math problems"""
    
    # Operator difficulty modifiers
    OPERATOR_MODIFIERS = {
        Operator.ADD: 0.0,
        Operator.SUBTRACT: 0.3,
        Operator.MULTIPLY: 0.5,
        Operator.DIVIDE: 0.8
    }
    
    def get_operand_range(self, difficulty: float) -> Tuple[int, int]:
        """Get operand range based on difficulty level"""
        if difficulty <= 2.0:
            return (1, 9)
        elif difficulty <= 3.5:
            return (1, 25)
        elif difficulty <= 5.0:
            return (10, 99)
        elif difficulty <= 7.0:
            return (10, 250)
        elif difficulty <= 8.5:
            return (100, 500)
        else:
            return (100, 999)
    
    def generate_operands(self, operator: Operator, difficulty: float) -> Tuple[int, int, int]:
        """Generate two valid operands and the correct answer"""
        min_val, max_val = self.get_operand_range(difficulty)
        
        if operator == Operator.ADD:
            op1 = random.randint(min_val, max_val)
            op2 = random.randint(min_val, max_val)
            answer = op1 + op2
            
        elif operator == Operator.SUBTRACT:
            op1 = random.randint(min_val, max_val)
            op2 = random.randint(min_val, op1)  # Ensure non-negative result
            answer = op1 - op2
            
        elif operator == Operator.MULTIPLY:
            # Adjust range to avoid huge results
            adjusted_max = min(max_val, int(max_val ** 0.5) + 5)
            adjusted_min = max(2, min_val)
            op1 = random.randint(adjusted_min, adjusted_max)
            op2 = random.randint(adjusted_min, adjusted_max)
            answer = op1 * op2
            
        elif operator == Operator.DIVIDE:
            # Generate exact division
            adjusted_max = min(50, int(max_val ** 0.5))
            adjusted_min = max(2, min(10, min_val))
            op2 = random.randint(adjusted_min, adjusted_max)  # Divisor
            quotient = random.randint(adjusted_min, adjusted_max)
            op1 = op2 * quotient  # Dividend
            answer = quotient
        
        return op1, op2, answer
    
    def generate_options(self, correct_answer: int) -> List[int]:
        """Generate 4 multiple choice options including the correct answer"""
        variation = max(1, int(correct_answer * 0.2))
        options = [correct_answer]
        attempts = 0
        
        while len(options) < 4 and attempts < 50:
            # Generate different types of wrong answers
            strategy = random.choice(['small_neg', 'small_pos', 'large_pos', 'large_neg'])
            
            if strategy == 'small_neg':
                offset = random.randint(-variation, -1)
            elif strategy == 'small_pos':
                offset = random.randint(1, variation)
            elif strategy == 'large_pos':
                offset = random.randint(1, 10)
            else:  # large_neg
                offset = random.randint(-10, -1)
            
            wrong_answer = correct_answer + offset
            
            # Validate
            if wrong_answer > 0 and wrong_answer not in options:
                options.append(wrong_answer)
            
            attempts += 1
        
        # Fill remaining if needed
        while len(options) < 4:
            fallback = random.randint(1, correct_answer * 2)
            if fallback not in options:
                options.append(fallback)
        
        # Shuffle to randomize position of correct answer
        random.shuffle(options)
        return options
    
    def generate_problem(self, operator: Operator, difficulty: float) -> Exercise:
        """
        Generate a single exercise problem
        
        Implementation of IProblemGenerator interface
        """
        # Generate operands and answer
        op1, op2, answer = self.generate_operands(operator, difficulty)
        
        # Randomly choose exercise type (66% multiple choice, 33% text input)
        exercise_type = ExerciseType.MULTIPLE_CHOICE if random.random() < 0.66 else ExerciseType.TEXT_INPUT
        
        # Generate options for multiple choice
        options = None
        if exercise_type == ExerciseType.MULTIPLE_CHOICE:
            options = self.generate_options(answer)
        
        # Apply operator modifier to difficulty
        adjusted_difficulty = min(10.0, max(1.0, difficulty + self.OPERATOR_MODIFIERS[operator]))
        
        return Exercise(
            exercise_type=exercise_type,
            operator=operator,
            operand_1=op1,
            operand_2=op2,
            correct_answer=answer,
            options=options,
            difficulty_level=round(adjusted_difficulty, 2)
        )
