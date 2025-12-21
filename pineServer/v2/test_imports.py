"""
Simple syntax check for V2 refactoring.
Run: python v2/test_imports.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(f"Python {sys.version}")

# Test interfaces
print("Testing interfaces...")
from v2.interfaces import (
    IExerciseGenerator, IBatchGenerator, IPerformanceEvaluator,
    IScoringCalculator, IMinibossDetector, IMinibossEvaluator,
    IBatchRecorder, IConfigManager, IDominioLevelManager
)
print("  ✓ All interfaces imported")

# Test implementations
print("Testing implementations...")
from v2.implementations.config_manager_impl import DefaultConfigManager
from v2.implementations.dominio_level_manager_impl import DefaultDominioLevelManager
from v2.implementations.exercise_generator_impl import DefaultExerciseGenerator
from v2.implementations.batch_generator_impl import DefaultBatchGenerator
from v2.implementations.performance_evaluator_impl import DefaultPerformanceEvaluator
from v2.implementations.scoring_calculator_impl import DefaultScoringCalculator
from v2.implementations.miniboss_detector_impl import DefaultMinibossDetector
from v2.implementations.miniboss_evaluator_impl import DefaultMinibossEvaluator
from v2.implementations.batch_recorder_impl import DefaultBatchRecorder
print("  ✓ All implementations imported")

# Test container
print("Testing container...")
from v2.container import V2Container, create_default_v2_container
print("  ✓ Container imported")

# Test session service
print("Testing session service...")
from v2.session_service import SessionService
print("  ✓ SessionService imported")

# Test models
print("Testing models...")
from v2.models import Exercise, ExerciseResult, BatchResult, BatchType
print("  ✓ Models imported")

# Test instantiation (no DB calls)
print("Testing instantiation...")
evaluator = DefaultPerformanceEvaluator()
print(f"  ✓ PerformanceEvaluator created (thresholds: {evaluator.high_threshold}/{evaluator.low_threshold})")

print("\n✅ All imports successful!")
