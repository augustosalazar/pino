"""
Gamification-aware problem generator
Generates math problems aligned with the


Nivel de Dominio (Mastery Level) per operation:
- Nivel 1 (0-19 PD): Básico
- Nivel 2 (20-49 PD): Intermedio
- Nivel 3 (50-89 PD): Avanzado
- Nivel 4 (90-139 PD): Experto
- Nivel 5 (≥140 PD): Maestro
"""

import random
from typing import List, Tuple
from models import Exercise, ExerciseType, Operator
from interfaces import IProblemGenerator


class GamificationProblemGenerator(IProblemGenerator):
    """Problem generator aligned with the 5-level mastery system"""
    
    # Mastery level configuration per operation
    # Format: {nivel: (min_operand, max_operand, description)}
    
    SUMA_LEVELS = {
        1: (0, 10, "1 cifra + 1 cifra"),
        2: (0, 20, "hasta 20"),
        3: (0, 50, "2 cifras + 2 cifras"),
        4: (0, 100, "hasta 100"),
        5: (0, 100, "maestro - variado")
    }
    
    RESTA_LEVELS = {
        1: (0, 10, "1 cifra - 1 cifra"),
        2: (0, 20, "hasta 20"),
        3: (0, 50, "2 cifras - 2 cifras"),
        4: (0, 100, "hasta 100"),
        5: (0, 100, "maestro - variado")
    }
    
    MULT_LEVELS = {
        1: (1, 3, "tablas 1-3"),        # Level 1: 1-3 tables
        2: (1, 5, "tablas 1-5"),        # Level 2: 1-5 tables
        3: (1, 10, "tablas 1-10"),      # Level 3: 1-10 tables
        4: (1, 10, "2 cifras × 1 cifra"),  # Level 4: 2 digits × 1 digit
        5: (1, 99, "2 cifras × 2 cifras")  # Level 5: 2 digits × 2 digits
    }
    
    DIV_LEVELS = {
        1: (1, 2, "divisiones por 1-2"),
        2: (1, 5, "tablas 1-5"),
        3: (1, 10, "divisiones exactas tabla 1-10"),
        4: (1, 10, "divisiones exactas y con resto"),
        5: (1, 10, "2 cifras entre 1 cifra")
    }
    
    def pd_to_nivel(self, pd_operacion: int) -> int:
        """
        Convert PD points to mastery level (1-5)
        
        Args:
            pd_operacion: PD points for the specific operation
            
        Returns:
            Nivel de dominio (1-5)
        """
        if pd_operacion < 20:
            return 1
        elif pd_operacion < 50:
            return 2
        elif pd_operacion < 90:
            return 3
        elif pd_operacion < 140:
            return 4
        else:
            return 5
    
    def get_nivel_config(self, operator: Operator, nivel: int) -> Tuple[int, int, str]:
        """
        Get configuration for a specific operator at a specific nivel
        
        Args:
            operator: The mathematical operator
            nivel: Mastery level (1-5)
            
        Returns:
            (min_operand, max_operand, description)
        """
        nivel = max(1, min(5, nivel))  # Clamp to 1-5
        
        if operator == Operator.ADD:
            return self.SUMA_LEVELS[nivel]
        elif operator == Operator.SUBTRACT:
            return self.RESTA_LEVELS[nivel]
        elif operator == Operator.MULTIPLY:
            return self.MULT_LEVELS[nivel]
        elif operator == Operator.DIVIDE:
            return self.DIV_LEVELS[nivel]
        
        return (0, 10, "default")  # Fallback
    
    def generate_operands(self, operator: Operator, difficulty: float) -> Tuple[int, int, int]:
        """
        Generate operands based on difficulty (interpreted as PD or nivel)
        
        For backward compatibility:
        - If difficulty < 10, treat as old system and map to nivel
        - Otherwise, convert PD to nivel using pd_to_nivel()
        """
        # Convert difficulty to nivel
        if difficulty < 10:
            # Old system: map 1.0-10.0 to nivel 1-5
            nivel = max(1, min(5, int((difficulty / 2) + 0.5)))
        else:
            # New system: difficulty is actually PD points
            nivel = self.pd_to_nivel(int(difficulty))
        
        min_val, max_val, description = self.get_nivel_config(operator, nivel)
        
        if operator == Operator.ADD:
            return self._generate_suma(min_val, max_val, nivel)
        elif operator == Operator.SUBTRACT:
            return self._generate_resta(min_val, max_val, nivel)
        elif operator == Operator.MULTIPLY:
            return self._generate_mult(min_val, max_val, nivel)
        elif operator == Operator.DIVIDE:
            return self._generate_div(min_val, max_val, nivel)
        
        # Fallback
        return (1, 1, 2)
    
    def _generate_suma(self, min_val: int, max_val: int, nivel: int) -> Tuple[int, int, int]:
        """Generate addition exercise"""
        op1 = random.randint(min_val, max_val)
        op2 = random.randint(min_val, max_val)
        answer = op1 + op2
        return (op1, op2, answer)
    
    def _generate_resta(self, min_val: int, max_val: int, nivel: int) -> Tuple[int, int, int]:
        """Generate subtraction exercise (ensuring non-negative results)"""
        op1 = random.randint(min_val, max_val)
        op2 = random.randint(min_val, op1)  # Ensure op2 <= op1
        answer = op1 - op2
        return (op1, op2, answer)
    
    def _generate_mult(self, min_val: int, max_val: int, nivel: int) -> Tuple[int, int, int]:
        """
        Generate multiplication exercise aligned with nivel
        
        Nivel 1-3: Tables (smaller numbers)
        Nivel 4: 2 digits × 1 digit
        Nivel 5: 2 digits × 2 digits
        """
        if nivel <= 3:
            # Tables: both operands in range
            op1 = random.randint(min_val, max_val)
            op2 = random.randint(min_val, max_val)
        elif nivel == 4:
            # 2 digits × 1 digit
            op1 = random.randint(10, 99)
            op2 = random.randint(2, 9)
        else:  # nivel == 5
            # 2 digits × 2 digits
            op1 = random.randint(10, 99)
            op2 = random.randint(10, 99)
        
        answer = op1 * op2
        return (op1, op2, answer)
    
    def _generate_div(self, min_val: int, max_val: int, nivel: int) -> Tuple[int, int, int]:
        """
        Generate division exercise
        
        Niveles 1-3: Exact divisions (no remainder)
        Nivel 4: Mix of exact and with remainder
        Nivel 5: 2 digits / 1 digit
        """
        if nivel <= 3:
            # Exact division: op1 = op2 × quotient
            divisor = random.randint(max(1, min_val), max_val)
            quotient = random.randint(1, max_val)
            dividend = divisor * quotient
            return (dividend, divisor, quotient)
        
        elif nivel == 4:
            # Mix: 70% exact, 30% with remainder
            if random.random() < 0.7:
                # Exact
                divisor = random.randint(2, 10)
                quotient = random.randint(2, 10)
                dividend = divisor * quotient
            else:
                # With remainder
                divisor = random.randint(2, 10)
                quotient = random.randint(2, 10)
                remainder = random.randint(1, divisor - 1)
                dividend = divisor * quotient + remainder
            return (dividend, divisor, quotient)
        
        else:  # nivel == 5
            # 2 digits / 1 digit
            divisor = random.randint(2, 9)
            quotient = random.randint(2, 20)
            
            # 50% exact, 50% with remainder
            if random.random() < 0.5:
                dividend = divisor * quotient
            else:
                remainder = random.randint(1, divisor - 1)
                dividend = divisor * quotient + remainder
            
            return (dividend, divisor, quotient)
    
    def generate_options(self, correct_answer: int, nivel: int = 1) -> List[int]:
        """
        Generate 4 multiple choice options with distractors based on nivel
        
        Higher niveles have distractors closer to the correct answer (more challenging)
        """
        # Distractor closeness based on nivel
        distractor_ranges = {
            1: 0.3,   # Nivel 1: distractors ±30% away
            2: 0.25,  # Nivel 2: distractors ±25% away
            3: 0.2,   # Nivel 3: distractors ±20% away (closer)
            4: 0.15,  # Nivel 4: distractors ±15% away (very close)
            5: 0.1    # Nivel 5: distractors ±10% away (tricky)
        }
        
        variation_pct = distractor_ranges.get(nivel, 0.2)
        variation = max(1, int(correct_answer * variation_pct))
        
        options = [correct_answer]
        attempts = 0
        
        while len(options) < 4 and attempts < 50:
            # For higher niveles, make distractors more strategic
            if nivel >= 3:
                # More likely to be close to the answer
                offset = random.randint(-variation, variation)
                if offset == 0:
                    offset = random.choice([-1, 1])
            else:
                # More varied distractors for beginners
                strategies = ['small_neg', 'small_pos', 'medium']
                strategy = random.choice(strategies)
                
                if strategy == 'small_neg':
                    offset = random.randint(-variation, -1)
                elif strategy == 'small_pos':
                    offset = random.randint(1, variation)
                else:  # medium
                    offset = random.randint(-variation * 2, variation * 2)
            
            wrong_answer = correct_answer + offset
            
            # Validate
            if wrong_answer > 0 and wrong_answer not in options:
                options.append(wrong_answer)
            
            attempts += 1
        
        # Fill remaining if needed
        while len(options) < 4:
            fallback = random.randint(max(1, correct_answer - variation * 3), correct_answer + variation * 3)
            if fallback not in options and fallback > 0:
                options.append(fallback)
        
        # Shuffle to randomize position of correct answer
        random.shuffle(options)
        return options
    
    def generate_problem(self, operator: Operator, difficulty: float) -> Exercise:
        """
        Generate a single exercise problem aligned with gamification system
        
        Args:
            operator: Mathematical operator
            difficulty: Difficulty level (can be PD points or old 1.0-10.0 scale)
        
        Returns:
            Exercise object
        """
        # Generate operands and answer
        op1, op2, answer = self.generate_operands(operator, difficulty)
        
        # Determine nivel for distractor generation
        if difficulty < 10:
            nivel = max(1, min(5, int((difficulty / 2) + 0.5)))
        else:
            nivel = self.pd_to_nivel(int(difficulty))
        
        # Exercise type distribution by nivel
        # Lower niveles: more multiple choice (easier)
        # Higher niveles: more text input (builds fluency)
        mc_probability = {
            1: 0.8,   # Nivel 1: 80% multiple choice
            2: 0.7,   # Nivel 2: 70% multiple choice
            3: 0.6,   # Nivel 3: 60% multiple choice
            4: 0.5,   # Nivel 4: 50% multiple choice
            5: 0.4    # Nivel 5: 40% multiple choice (more text input)
        }
        
        exercise_type = ExerciseType.MULTIPLE_CHOICE if random.random() < mc_probability.get(nivel, 0.66) else ExerciseType.TEXT_INPUT
        
        # Generate options for multiple choice
        options = None
        if exercise_type == ExerciseType.MULTIPLE_CHOICE:
            options = self.generate_options(answer, nivel)
        
        return Exercise(
            exercise_type=exercise_type,
            operator=operator,
            operand_1=op1,
            operand_2=op2,
            correct_answer=answer,
            options=options,
            difficulty_level=round(difficulty, 2)
        )
