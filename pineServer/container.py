"""
Dependency Injection Container
Manages component lifecycle and injection
"""

from typing import Optional
from interfaces import IProblemGenerator, IBatchGenerator, IProfileEvaluator
from generators import StandardBatchGenerator  # Batch generator unchanged
from generators.gamification_problem_generator import GamificationProblemGenerator  # NEW
from evaluators import StandardProfileEvaluator


class ServiceContainer:
    """Container for managing dependencies"""
    
    def __init__(self):
        self._problem_generator: Optional[IProblemGenerator] = None
        self._batch_generator: Optional[IBatchGenerator] = None
        self._profile_evaluator: Optional[IProfileEvaluator] = None
    
    def set_problem_generator(self, generator: IProblemGenerator):
        """Inject problem generator implementation"""
        self._problem_generator = generator
    
    def set_batch_generator(self, generator: IBatchGenerator):
        """Inject batch generator implementation"""
        self._batch_generator = generator
    
    def set_profile_evaluator(self, evaluator: IProfileEvaluator):
        """Inject profile evaluator implementation"""
        self._profile_evaluator = evaluator
    
    @property
    def problem_generator(self) -> IProblemGenerator:
        """Get problem generator instance"""
        if self._problem_generator is None:
            raise RuntimeError("Problem generator not configured")
        return self._problem_generator
    
    @property
    def batch_generator(self) -> IBatchGenerator:
        """Get batch generator instance"""
        if self._batch_generator is None:
            raise RuntimeError("Batch generator not configured")
        return self._batch_generator
    
    @property
    def profile_evaluator(self) -> IProfileEvaluator:
        """Get profile evaluator instance"""
        if self._profile_evaluator is None:
            raise RuntimeError("Profile evaluator not configured")
        return self._profile_evaluator


def create_default_container() -> ServiceContainer:
    """
    Create container with gamification-aware implementations
    
    Uses:
    - GamificationProblemGenerator: Respects 5-level mastery system (Nivel 1-5)
    - StandardBatchGenerator: Respects operation unlocks
    - StandardProfileEvaluator: Adaptive difficulty tracking
    
    Returns:
        ServiceContainer configured with gamification implementations
    """
    container = ServiceContainer()
    
    # Create gamification-aware problem generator
    problem_gen = GamificationProblemGenerator()
    batch_gen = StandardBatchGenerator(problem_gen)
    profile_eval = StandardProfileEvaluator()
    
    # Inject into container
    container.set_problem_generator(problem_gen)
    container.set_batch_generator(batch_gen)
    container.set_profile_evaluator(profile_eval)
    
    return container


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get the global service container"""
    global _container
    if _container is None:
        _container = create_default_container()
    return _container


def set_container(container: ServiceContainer):
    """Set a custom service container (for testing or alternative implementations)"""
    global _container
    _container = container
