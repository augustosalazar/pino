"""
V2 Dependency Injection Container

Central registry for all injectable components.
Supports registration, resolution, and lazy initialization.
"""

from typing import Optional, Type, TypeVar, Callable, Dict, Any
from v2.interfaces import (
    IExerciseGenerator, IBatchGenerator, IPerformanceEvaluator,
    IScoringCalculator, IMinibossDetector, IMinibossEvaluator,
    IBatchRecorder, IConfigManager, IDominioLevelManager
)


T = TypeVar('T')


class V2Container:
    """
    Dependency Injection container for V2 gamification system.
    
    Supports:
    - Singleton instances (default)
    - Factory registration for custom instantiation
    - Easy swapping of implementations for testing or A/B testing
    """
    
    def __init__(self):
        self._instances: Dict[type, Any] = {}
        self._factories: Dict[type, Callable[[], Any]] = {}
        
    def register_instance(self, interface: Type[T], instance: T) -> 'V2Container':
        """
        Register a specific instance for an interface.
        
        Args:
            interface: The interface type (e.g., IExerciseGenerator)
            instance: The implementation instance
            
        Returns:
            self for chaining
        """
        self._instances[interface] = instance
        return self
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> 'V2Container':
        """
        Register a factory function for lazy instantiation.
        
        Args:
            interface: The interface type
            factory: Callable that creates the implementation
            
        Returns:
            self for chaining
        """
        self._factories[interface] = factory
        return self
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve an implementation for the given interface.
        
        Args:
            interface: The interface type to resolve
            
        Returns:
            Implementation instance
            
        Raises:
            RuntimeError: If no implementation is registered
        """
        # Check if we have an instance cached
        if interface in self._instances:
            return self._instances[interface]
        
        # Check if we have a factory
        if interface in self._factories:
            instance = self._factories[interface]()
            self._instances[interface] = instance  # Cache for future calls
            return instance
        
        raise RuntimeError(f"No implementation registered for {interface.__name__}")
    
    def has(self, interface: Type[T]) -> bool:
        """Check if an interface has a registered implementation."""
        return interface in self._instances or interface in self._factories
    
    def clear(self):
        """Clear all registrations (useful for testing)."""
        self._instances.clear()
        self._factories.clear()
    
    # Convenience properties for common services
    @property
    def exercise_generator(self) -> IExerciseGenerator:
        return self.resolve(IExerciseGenerator)
    
    @property
    def batch_generator(self) -> IBatchGenerator:
        return self.resolve(IBatchGenerator)
    
    @property
    def performance_evaluator(self) -> IPerformanceEvaluator:
        return self.resolve(IPerformanceEvaluator)
    
    @property
    def scoring_calculator(self) -> IScoringCalculator:
        return self.resolve(IScoringCalculator)
    
    @property
    def miniboss_detector(self) -> IMinibossDetector:
        return self.resolve(IMinibossDetector)
    
    @property
    def miniboss_evaluator(self) -> IMinibossEvaluator:
        return self.resolve(IMinibossEvaluator)
    
    @property
    def batch_recorder(self) -> IBatchRecorder:
        return self.resolve(IBatchRecorder)
    
    @property
    def config_manager(self) -> IConfigManager:
        return self.resolve(IConfigManager)
    
    @property
    def dominio_level_manager(self) -> IDominioLevelManager:
        return self.resolve(IDominioLevelManager)


def create_default_v2_container() -> V2Container:
    """
    Create a container with all default implementations registered.
    
    This is the standard setup for production use.
    """
    from v2.implementations.exercise_generator_impl import DefaultExerciseGenerator
    from v2.implementations.batch_generator_impl import DefaultBatchGenerator
    from v2.implementations.performance_evaluator_impl import DefaultPerformanceEvaluator
    from v2.implementations.scoring_calculator_impl import DefaultScoringCalculator
    from v2.implementations.miniboss_detector_impl import DefaultMinibossDetector
    from v2.implementations.miniboss_evaluator_impl import DefaultMinibossEvaluator
    from v2.implementations.batch_recorder_impl import DefaultBatchRecorder
    from v2.implementations.config_manager_impl import DefaultConfigManager
    from v2.implementations.dominio_level_manager_impl import DefaultDominioLevelManager
    
    container = V2Container()
    
    # Register config first (other services depend on it)
    container.register_factory(IConfigManager, DefaultConfigManager)
    container.register_factory(IDominioLevelManager, lambda: DefaultDominioLevelManager(container))
    
    # Register generators
    container.register_factory(IExerciseGenerator, lambda: DefaultExerciseGenerator(container))
    container.register_factory(IBatchGenerator, lambda: DefaultBatchGenerator(container))
    
    # Register evaluators
    container.register_factory(IPerformanceEvaluator, DefaultPerformanceEvaluator)
    container.register_factory(IScoringCalculator, lambda: DefaultScoringCalculator(container))
    container.register_factory(IMinibossDetector, lambda: DefaultMinibossDetector(container))
    container.register_factory(IMinibossEvaluator, lambda: DefaultMinibossEvaluator(container))
    
    # Register recorder
    container.register_factory(IBatchRecorder, lambda: DefaultBatchRecorder(container))
    
    return container


# Global container instance
_v2_container: Optional[V2Container] = None


def get_v2_container() -> V2Container:
    """Get the global V2 container. Creates default if not set."""
    global _v2_container
    if _v2_container is None:
        _v2_container = create_default_v2_container()
    return _v2_container


def set_v2_container(container: V2Container):
    """Set a custom V2 container (for testing or alternative implementations)."""
    global _v2_container
    _v2_container = container


def reset_v2_container():
    """Reset the global container to None (forces re-creation on next access)."""
    global _v2_container
    _v2_container = None
