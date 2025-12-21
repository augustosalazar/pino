"""
Gamificación V2 - Sistema modular y configurable

Este paquete contiene la implementación del nuevo motor de gamificación
que usa nivel invisible, configuraciones dinámicas y tracking detallado.

Architecture:
- interfaces.py: Abstract contracts for all injectable components
- container.py: Dependency injection container
- implementations/: Default implementations of all interfaces
- session_service.py: Main orchestration layer
- models.py: Data models and DTOs

Usage:
    from v2.container import get_v2_container
    from v2.session_service import get_session_service
    
    # Get container for direct access to components
    container = get_v2_container()
    exercises = container.batch_generator.generate_batch(...)
    
    # Or use the session service for full orchestration
    service = get_session_service()
    result = service.start_session(user_ref="123")
    
Custom Implementations:
    To create a custom implementation (e.g., for testing):
    
    from v2.interfaces import IExerciseGenerator
    from v2.container import V2Container, set_v2_container
    
    class MyCustomGenerator(IExerciseGenerator):
        def generate_exercise(self, operacion, nivel):
            # Custom logic here
            pass
    
    container = V2Container()
    container.register_instance(IExerciseGenerator, MyCustomGenerator())
    # ... register other implementations
    set_v2_container(container)
"""

__version__ = "2.0.0"
__author__ = "PineServer Team"

# Interfaces
from v2.interfaces import (
    IExerciseGenerator,
    IBatchGenerator,
    IPerformanceEvaluator,
    IScoringCalculator,
    IMinibossDetector,
    IMinibossEvaluator,
    IBatchRecorder,
    IConfigManager,
    IDominioLevelManager,
)

# Container
from v2.container import (
    V2Container,
    get_v2_container,
    set_v2_container,
    reset_v2_container,
    create_default_v2_container,
)

# Session Service
from v2.session_service import (
    SessionService,
    get_session_service,
    set_session_service,
)

# Models
from v2.models import (
    Exercise,
    ExerciseResult,
    BatchResult,
    UserOperationState,
    UserGamificationState,
    Operacion,
    TipoRespuesta,
    BatchType,
)

# Legacy compatibility - these will be deprecated
from v2.config_manager import ConfigManager, get_config_manager

__all__ = [
    # Version
    "__version__",
    # Interfaces
    "IExerciseGenerator",
    "IBatchGenerator",
    "IPerformanceEvaluator",
    "IScoringCalculator",
    "IMinibossDetector",
    "IMinibossEvaluator",
    "IBatchRecorder",
    "IConfigManager",
    "IDominioLevelManager",
    # Container
    "V2Container",
    "get_v2_container",
    "set_v2_container",
    "reset_v2_container",
    "create_default_v2_container",
    # Session Service
    "SessionService",
    "get_session_service",
    "set_session_service",
    # Models
    "Exercise",
    "ExerciseResult",
    "BatchResult",
    "UserOperationState",
    "UserGamificationState",
    "Operacion",
    "TipoRespuesta",
    "BatchType",
    # Legacy
    "ConfigManager",
    "get_config_manager",
]
