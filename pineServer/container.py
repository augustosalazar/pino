"""
Dependency Injection Container

Central registry for all injectable components.
Supports registration, resolution, and lazy initialization.
"""

from typing import Optional, Type, TypeVar, Callable, Dict, Any

T = TypeVar('T')


class Container:
    """
    DI container for the gamification system.
    
    Usage:
        container = get_container()
        generator = container.exercise_generator
        
    Custom implementations:
        container.register_instance(IExerciseGenerator, MyCustomGenerator())
    """
    
    def __init__(self):
        self._instances: Dict[type, Any] = {}
        self._factories: Dict[type, Callable[[], Any]] = {}
        
    def register_instance(self, interface: Type[T], instance: T) -> 'Container':
        """Register a specific instance for an interface."""
        self._instances[interface] = instance
        return self
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> 'Container':
        """Register a factory function for lazy instantiation."""
        self._factories[interface] = factory
        return self
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve an implementation for the given interface."""
        if interface in self._instances:
            return self._instances[interface]
        
        if interface in self._factories:
            instance = self._factories[interface]()
            self._instances[interface] = instance
            return instance
        
        raise RuntimeError(f"No implementation registered for {interface.__name__}")
    
    def has(self, interface: Type[T]) -> bool:
        """Check if an interface has a registered implementation."""
        return interface in self._instances or interface in self._factories
    
    def clear(self):
        """Clear all registrations."""
        self._instances.clear()
        self._factories.clear()
    
    # Convenience properties
    @property
    def config_manager(self):
        from interfaces import IConfigManager
        return self.resolve(IConfigManager)
    
    @property
    def exercise_generator(self):
        from interfaces import IExerciseGenerator
        return self.resolve(IExerciseGenerator)
    
    @property
    def batch_generator(self):
        from interfaces import IBatchGenerator
        return self.resolve(IBatchGenerator)
    
    @property
    def performance_evaluator(self):
        from interfaces import IPerformanceEvaluator
        return self.resolve(IPerformanceEvaluator)
    
    @property
    def scoring_calculator(self):
        from interfaces import IScoringCalculator
        return self.resolve(IScoringCalculator)
    
    @property
    def miniboss_detector(self):
        from interfaces import IMinibossDetector
        return self.resolve(IMinibossDetector)
    
    @property
    def miniboss_evaluator(self):
        from interfaces import IMinibossEvaluator
        return self.resolve(IMinibossEvaluator)
    
    @property
    def batch_recorder(self):
        from interfaces import IBatchRecorder
        return self.resolve(IBatchRecorder)
    
    @property
    def dominio_level_manager(self):
        from interfaces import IDominioLevelManager
        return self.resolve(IDominioLevelManager)


def create_default_container() -> Container:
    """
    Create container with all default implementations.
    """
    from interfaces import (
        IConfigManager, IDominioLevelManager, IExerciseGenerator,
        IBatchGenerator, IPerformanceEvaluator, IScoringCalculator,
        IMinibossDetector, IMinibossEvaluator, IBatchRecorder
    )
    
    container = Container()
    
    # Import implementations - they now implement the interfaces directly
    from config_manager import ConfigManager
    from dominio_level_manager import DominioLevelManager
    from exercise_generator import ExerciseGenerator
    from batch_generator import BatchGenerator
    from performance_evaluator import PerformanceEvaluator
    from scoring_calculator import ScoringCalculator
    from miniboss_detector import MinibossDetector
    from miniboss_evaluator import MinibossEvaluator
    from batch_recorder import BatchRecorder
    
    # Register all with factories for lazy init
    container.register_factory(IConfigManager, ConfigManager)
    container.register_factory(IDominioLevelManager, lambda: DominioLevelManager(container))
    container.register_factory(IExerciseGenerator, lambda: ExerciseGenerator(container))
    container.register_factory(IBatchGenerator, lambda: BatchGenerator(container))
    container.register_factory(IPerformanceEvaluator, PerformanceEvaluator)
    container.register_factory(IScoringCalculator, lambda: ScoringCalculator(container))
    container.register_factory(IMinibossDetector, lambda: MinibossDetector(container))
    container.register_factory(IMinibossEvaluator, lambda: MinibossEvaluator(container))
    container.register_factory(IBatchRecorder, lambda: BatchRecorder(container))
    
    return container


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get the global container. Creates default if not set."""
    global _container
    if _container is None:
        _container = create_default_container()
    return _container


def set_container(container: Container):
    """Set a custom container (for testing or alternative implementations)."""
    global _container
    _container = container


def reset_container():
    """Reset the global container."""
    global _container
    _container = None
