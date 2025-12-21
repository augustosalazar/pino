# V2 Architecture - Refactored PineServer

## Overview

The V2 gamification system has been refactored to use a clean **Dependency Injection** architecture.
This enables:

- **Testability**: Easy mocking of components for unit tests
- **Flexibility**: Swap implementations for A/B testing
- **Maintainability**: Clear interfaces and single responsibility
- **Extensibility**: Create new implementations without modifying core code

## Directory Structure

```
v2/
├── __init__.py              # Package exports
├── interfaces.py            # Abstract base classes (contracts)
├── container.py             # Dependency injection container
├── session_service.py       # Main orchestration layer
├── session_routes.py        # FastAPI router (optional)
├── models.py                # Data models and DTOs
│
├── implementations/         # Default implementations
│   ├── __init__.py
│   ├── config_manager_impl.py
│   ├── dominio_level_manager_impl.py
│   ├── exercise_generator_impl.py
│   ├── batch_generator_impl.py
│   ├── performance_evaluator_impl.py
│   ├── scoring_calculator_impl.py
│   ├── miniboss_detector_impl.py
│   ├── miniboss_evaluator_impl.py
│   └── batch_recorder_impl.py
│
├── examples/                # Example custom implementations
│   ├── __init__.py
│   └── custom_implementations.py
│
└── (legacy files)           # Old singleton-based files (deprecated)
    ├── exercise_generator.py
    ├── batch_generator.py
    ├── performance_evaluator.py
    ├── scoring_calculator.py
    ├── miniboss_detector.py
    ├── miniboss_evaluator.py
    ├── batch_recorder.py
    └── config_manager.py
```

## Core Interfaces

All injectable components implement these interfaces defined in `interfaces.py`:

| Interface | Purpose |
|-----------|---------|
| `IExerciseGenerator` | Generates individual exercises |
| `IBatchGenerator` | Generates batches of exercises |
| `IPerformanceEvaluator` | Evaluates performance, adjusts difficulty |
| `IScoringCalculator` | Calculates PP, PD, XP, and score |
| `IMinibossDetector` | Determines when miniboss should appear |
| `IMinibossEvaluator` | Evaluates miniboss pass/fail |
| `IBatchRecorder` | Persists batch results to database |
| `IConfigManager` | Provides configuration data |
| `IDominioLevelManager` | Manages domain level calculations |

## Usage Examples

### 1. Using the Default Container

```python
from v2.container import get_v2_container

# Get the global container with default implementations
container = get_v2_container()

# Access any component
exercises = container.batch_generator.generate_batch(
    user_ref="user123",
    operacion="suma",
    nivel_invisible=2.5,
    batch_type="regular"
)
```

### 2. Using the Session Service

```python
from v2.session_service import get_session_service

service = get_session_service()

# Start a session
result = service.start_session(
    user_ref="user123",
    num_exercises=10,
    batch_type_override="regular"
)

# Complete a session
completion = service.complete_session(
    session_id=result["session_id"],
    exercise_results=results
)
```

### 3. Creating Custom Implementations

```python
from v2.interfaces import IPerformanceEvaluator
from v2.container import V2Container, set_v2_container

class MyCustomEvaluator(IPerformanceEvaluator):
    def evaluate_performance(self, resultados, nivel_actual):
        # Custom logic here
        return nivel_actual + 0.5

# Replace in the container
container = get_v2_container()
container.register_instance(IPerformanceEvaluator, MyCustomEvaluator())
```

### 4. A/B Testing Setup

```python
from v2.examples.custom_implementations import create_ab_test_container
from v2.container import set_v2_container

# Determine variant (from feature flags, random, etc.)
variant = "treatment" if user_in_treatment_group else "control"

# Set up the appropriate container
container = create_ab_test_container(variant)
set_v2_container(container)

# Now all service calls will use the configured implementations
```

### 5. Unit Testing with Mocks

```python
import pytest
from v2.examples.custom_implementations import create_test_container_with_mocks
from v2.container import set_v2_container, reset_v2_container
from v2.session_service import SessionService

@pytest.fixture
def mock_container():
    container = create_test_container_with_mocks()
    set_v2_container(container)
    yield container
    reset_v2_container()

def test_session_scoring(mock_container):
    service = SessionService(container=mock_container)
    # Test with predictable mock behavior
    ...
```

## Migration from Legacy Code

The legacy singleton-based files (`get_exercise_generator()`, etc.) are still available for backward compatibility but are **deprecated**. New code should use:

1. **For endpoints**: Use `SessionService` or the new `session_routes.py` router
2. **For direct component access**: Use `get_v2_container()` 
3. **For testing**: Create custom containers with mock implementations

## Integrating with main.py

To use the new session routes in main.py:

```python
from v2.session_routes import router as v2_session_router

# Include the router (replaces existing session endpoints)
app.include_router(v2_session_router)
```

Or use the SessionService directly in existing endpoints:

```python
from v2.session_service import get_session_service

@app.post("/api/sessions/start")
async def start_session(request: StartSessionRequest):
    service = get_session_service()
    result = service.start_session(
        user_ref=request.user_ref,
        num_exercises=request.num_exercises,
        batch_type_override=request.batch_type
    )
    # ... convert and return
```

## Performance Considerations

- The container uses **lazy instantiation** - components are created only when first accessed
- Instances are cached as **singletons** within the container
- Database connections are handled by `roble_client` (external to DI)

## Future Enhancements

- [ ] Add scoped lifetime support (per-request instances)
- [ ] Add async interface variants
- [ ] Add configuration-driven implementation selection
- [ ] Add metrics/observability hooks
