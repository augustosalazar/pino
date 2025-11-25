# Modular Architecture with Dependency Injection

## Overview

The PineServer has been refactored to use **Dependency Injection** for three core components, allowing you to easily swap implementations without changing the main code.

## Architecture

### 1. **Interfaces** (`interfaces.py`)

Defines contracts that all implementations must follow:

- **`IProblemGenerator`**: Generates a single exercise problem
- **`IBatchGenerator`**: Creates batches of exercises  
- **`IProfileEvaluator`**: Evaluates performance and adjusts difficulty

### 2. **Implementations**

#### Standard Implementations (Default)
- **`StandardProblemGenerator`** (`generators/problem_generator.py`)
  - Generates math problems with adaptive difficulty
  - Supports +, -, *, / operators
  - Creates both multiple-choice and text-input exercises

- **`StandardBatchGenerator`** (`generators/batch_generator.py`)
  - Creates balanced exercise sets
  - Default distribution: 40% +, 20% -, 20% *, 20% /
  - Uses injected `IProblemGenerator`

- **`StandardProfileEvaluator`** (`evaluators/profile_evaluator.py`)
  - Evaluates user performance
  - Adjusts difficulty based on success rate
  - Calculates session scores

#### Future: Custom Implementations
You can create alternative implementations by:
1. Implementing the interface (e.g., `class MyGenerator(IProblemGenerator)`)
2. Injecting it into the container

### 3. **Dependency Injection Container** (`container.py`)

Manages component lifecycle and injection:

```python
from container import get_container

# Get the global container
container = get_container()

# Use injected components
exercises = container.batch_generator.generate_batch(difficulty, 10)
score = container.profile_evaluator.calculate_score(exercises)
```

## Usage Examples

### Using Default Implementations

```python
# The default container is auto-configured
from container import get_container

container = get_container()

# Generate a single problem
from models import Operator
problem = container.problem_generator.generate_problem(Operator.ADD, 2.5)

# Generate a batch
batch = container.batch_generator.generate_batch({'+': 2.0, '-': 1.5}, 10)

# Evaluate performance
new_diff, adjustments = container.profile_evaluator.evaluate_performance(
    completed_exercises,
    current_difficulty
)
```

### Creating Custom Implementations

```python
from interfaces import IProblemGenerator
from models import Exercise, Operator

class EasyProblemGenerator(IProblemGenerator):
    """Custom generator that makes all problems easy"""
    
    def generate_problem(self, operator: Operator, difficulty: float) -> Exercise:
        # Your custom logic here
        return Exercise(...)

# Inject your custom implementation
from container import get_container, ServiceContainer

container = ServiceContainer()
container.set_problem_generator(EasyProblemGenerator())
# ... set other components

# Use custom container
from container import set_container
set_container(container)
```

### Testing with Mock Implementations

```python
from interfaces import IProfileEvaluator

class MockProfileEvaluator(IProfileEvaluator):
    """Test double for unit testing"""
    
    def evaluate_performance(self, exercises, current_diff):
        # Return predictable results for testing
        return ({'+'1.0}, [])
    
    def calculate_score(self, exercises):
        return len(exercises) * 10  # Simple scoring for tests

# In your test
container = ServiceContainer()
container.set_profile_evaluator(MockProfileEvaluator())
# ... test your code
```

## Component Responsibilities

### IProblemGenerator
- **Input**: Operator, difficulty level
- **Output**: Single exercise with problem and answer
- **Responsibility**: Generate one valid math problem

### IBatchGenerator  
- **Input**: Difficulty by operator, number of exercises
- **Output**: List of exercises
- **Responsibility**: Create balanced exercise sets
- **Dependencies**: Uses `IProblemGenerator`

### IProfileEvaluator
- **Input**: Completed exercises, current difficulty
- **Output**: New difficulty levels, adjustment records, scores
- **Responsibility**: Performance evaluation and difficulty adjustment

## Benefits

1. **Testability**: Easy to mock components for unit tests
2. **Flexibility**: Swap implementations without changing main code
3. **Separation of Concerns**: Clear boundaries between components
4. **Extensibility**: Add new implementations without modifying existing code

## File Structure

```
pineServer/
├── interfaces.py              # Interface definitions
├── container.py               # Dependency injection container
├── generators/
│   ├── __init__.py
│   ├── problem_generator.py   # Standard problem generator
│   └── batch_generator.py     # Standard batch generator
├── evaluators/
│   ├── __init__.py
│   └── profile_evaluator.py   # Standard profile evaluator
└── main.py                    # FastAPI app using injected components
```

## Migration from Old Code

The old global instances have been replaced:
- ❌ `exercise_generator.generate_exercise_set()`
- ✅ `container.batch_generator.generate_batch()`

- ❌ `difficulty_manager.calculate_score()`
- ✅ `container.profile_evaluator.calculate_score()`

- ❌ `difficulty_manager.calculate_adjustments()`
- ✅ `container.profile_evaluator.evaluate_performance()`
