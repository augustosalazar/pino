"""
Example: Custom Injectable Implementations

This file demonstrates how to create custom implementations
of the V2 interfaces for:
- A/B testing different algorithms
- Unit testing with mocks
- Experimental features

Usage:
    from v2.examples.custom_implementations import create_mock_container
    
    # For testing
    container = create_mock_container()
    set_v2_container(container)
"""

import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import List, Dict, Optional, Any

from v2.interfaces import (
    IExerciseGenerator, IPerformanceEvaluator, 
    IScoringCalculator, IMinibossEvaluator
)
from v2.models import Exercise, ExerciseResult, TipoRespuesta, UserOperationState
from v2.container import V2Container, set_v2_container


# ==============================================================================
# Example 1: Custom Scoring Calculator for A/B Testing
# ==============================================================================

class AlternativeScoringCalculator(IScoringCalculator):
    """
    Alternative scoring algorithm that rewards streaks.
    
    Use this for A/B testing different motivation mechanics.
    """
    
    def __init__(self, streak_bonus: int = 5):
        self.streak_bonus = streak_bonus
    
    def calculate_score_parts(self, resultados: List[ExerciseResult]) -> Dict[str, int]:
        if not resultados:
            return {"total": 0, "base": 0, "bonus": 0, "penalty": 0}
        
        base = 0
        streak = 0
        streak_bonuses = 0
        
        for r in resultados:
            if r.es_correcto:
                base += 10
                streak += 1
                if streak >= 3:
                    streak_bonuses += self.streak_bonus
            else:
                streak = 0
        
        return {
            "total": base + streak_bonuses,
            "base": base,
            "bonus": streak_bonuses,
            "penalty": 0
        }
    
    def calculate_score(self, resultados: List[ExerciseResult]) -> int:
        return self.calculate_score_parts(resultados)["total"]
    
    def calculate_pp(self, resultados: List[ExerciseResult]) -> int:
        return len(resultados)
    
    def calculate_pd(self, resultados: List[ExerciseResult]) -> int:
        return self.calculate_score(resultados)
    
    def calculate_xp(self, resultados: List[ExerciseResult]) -> int:
        return self.calculate_score(resultados)


# ==============================================================================
# Example 2: Mock Exercise Generator for Testing
# ==============================================================================

class MockExerciseGenerator(IExerciseGenerator):
    """
    Deterministic exercise generator for unit tests.
    
    Returns predictable exercises for assertions.
    """
    
    def __init__(self, exercises: Optional[List[Exercise]] = None):
        self._exercises = exercises or []
        self._index = 0
    
    def generate_exercise(self, operacion: str, nivel_invisible: float) -> Exercise:
        if self._exercises:
            # Return from predefined list
            ex = self._exercises[self._index % len(self._exercises)]
            self._index += 1
            return ex
        
        # Default: simple addition
        return Exercise(
            operand_1=1,
            operand_2=1,
            operacion=operacion,
            respuesta_correcta=2.0,
            dificultad=nivel_invisible,
            tipo_respuesta=TipoRespuesta.MULTIPLE_CHOICE,
            opciones=[1, 2, 3, 4]
        )


# ==============================================================================
# Example 3: Stricter Miniboss Evaluator
# ==============================================================================

class StrictMinibossEvaluator(IMinibossEvaluator):
    """
    Stricter miniboss that requires 90% correct rate.
    
    Use for advanced users or challenge modes.
    """
    
    def __init__(self, min_correct_rate: float = 0.9):
        self.min_correct_rate = min_correct_rate
    
    def evaluate_miniboss(self, resultados: List[ExerciseResult]) -> bool:
        if not resultados:
            return False
        
        total = len(resultados)
        correctos = sum(1 for r in resultados if r.es_correcto)
        rate = correctos / total
        
        passed = rate >= self.min_correct_rate
        print(f"[StrictMiniboss] Rate: {rate:.1%}, Required: {self.min_correct_rate:.1%}, Passed: {passed}")
        return passed


# ==============================================================================
# Example 4: Faster Progression Evaluator
# ==============================================================================

class FasterProgressionEvaluator(IPerformanceEvaluator):
    """
    Performance evaluator with faster level progression.
    
    Increases difficulty faster for advanced users.
    """
    
    def __init__(self):
        self.min_level = 1.0
        self.max_level = 6.0
        self.increase_step = 0.4  # Double the default
        self.decrease_step = 0.05  # Half the default decrease
    
    def evaluate_performance(
        self,
        resultados: List[ExerciseResult],
        nivel_invisible_actual: float
    ) -> float:
        if not resultados:
            return nivel_invisible_actual
        
        total = len(resultados)
        correctos = sum(1 for r in resultados if r.es_correcto)
        success_rate = correctos / total
        
        if success_rate >= 0.8:
            delta = self.increase_step
        elif success_rate < 0.4:
            delta = -self.decrease_step
        else:
            delta = 0.0
        
        nuevo = nivel_invisible_actual + delta
        return max(self.min_level, min(nuevo, self.max_level))


# ==============================================================================
# Helper Functions
# ==============================================================================

def create_test_container_with_mocks() -> V2Container:
    """
    Create a container with mock implementations for testing.
    
    Returns:
        V2Container with mock implementations
    """
    from v2.implementations.config_manager_impl import DefaultConfigManager
    from v2.implementations.dominio_level_manager_impl import DefaultDominioLevelManager
    from v2.implementations.batch_generator_impl import DefaultBatchGenerator
    from v2.implementations.batch_recorder_impl import DefaultBatchRecorder
    from v2.implementations.miniboss_detector_impl import DefaultMinibossDetector
    from v2.interfaces import (
        IConfigManager, IDominioLevelManager, IExerciseGenerator,
        IBatchGenerator, IPerformanceEvaluator, IScoringCalculator,
        IMinibossDetector, IMinibossEvaluator, IBatchRecorder
    )
    
    container = V2Container()
    
    # Use defaults for infrastructure
    container.register_factory(IConfigManager, DefaultConfigManager)
    container.register_factory(IDominioLevelManager, lambda: DefaultDominioLevelManager(container))
    container.register_factory(IBatchGenerator, lambda: DefaultBatchGenerator(container))
    container.register_factory(IMinibossDetector, lambda: DefaultMinibossDetector(container))
    container.register_factory(IBatchRecorder, lambda: DefaultBatchRecorder(container))
    
    # Use mocks/alternatives for testable logic
    container.register_instance(IExerciseGenerator, MockExerciseGenerator())
    container.register_instance(IPerformanceEvaluator, FasterProgressionEvaluator())
    container.register_instance(IScoringCalculator, AlternativeScoringCalculator())
    container.register_instance(IMinibossEvaluator, StrictMinibossEvaluator())
    
    return container


def create_ab_test_container(variant: str) -> V2Container:
    """
    Create a container configured for A/B testing.
    
    Args:
        variant: 'control' or 'treatment'
        
    Returns:
        V2Container configured for the variant
    """
    from v2.container import create_default_v2_container
    from v2.interfaces import IScoringCalculator, IPerformanceEvaluator
    
    container = create_default_v2_container()
    
    if variant == "treatment":
        # Replace with alternative implementations
        container.register_instance(IScoringCalculator, AlternativeScoringCalculator(streak_bonus=10))
        container.register_instance(IPerformanceEvaluator, FasterProgressionEvaluator())
    
    return container


# ==============================================================================
# Usage Example
# ==============================================================================

if __name__ == "__main__":
    print("=== Custom Implementations Demo ===\n")
    
    # Create mock results
    mock_results = [
        ExerciseResult(
            exercise=Exercise(1, 1, "suma", 2.0, 1.0, TipoRespuesta.MULTIPLE_CHOICE),
            respuesta_usuario=2,
            es_correcto=True,
            tiempo_segundos=5.0
        ),
        ExerciseResult(
            exercise=Exercise(2, 3, "suma", 5.0, 1.0, TipoRespuesta.MULTIPLE_CHOICE),
            respuesta_usuario=5,
            es_correcto=True,
            tiempo_segundos=4.0
        ),
        ExerciseResult(
            exercise=Exercise(3, 3, "suma", 6.0, 1.0, TipoRespuesta.MULTIPLE_CHOICE),
            respuesta_usuario=6,
            es_correcto=True,
            tiempo_segundos=3.0
        ),
    ]
    
    print("1. Testing AlternativeScoringCalculator:")
    alt_scorer = AlternativeScoringCalculator()
    score = alt_scorer.calculate_score(mock_results)
    print(f"   Score with streak bonus: {score}")
    print(f"   Parts: {alt_scorer.calculate_score_parts(mock_results)}")
    
    print("\n2. Testing FasterProgressionEvaluator:")
    fast_eval = FasterProgressionEvaluator()
    new_level = fast_eval.evaluate_performance(mock_results, 1.0)
    print(f"   Level change: 1.0 -> {new_level}")
    
    print("\n3. Testing StrictMinibossEvaluator:")
    strict_mb = StrictMinibossEvaluator(0.9)
    passed = strict_mb.evaluate_miniboss(mock_results)
    print(f"   Miniboss passed (100% correct): {passed}")
    
    print("\n✅ Custom implementations working!")
