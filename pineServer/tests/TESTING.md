# Test Documentation

## Test Suite Overview

All tests are located in `pineServer/tests/` directory.

**Total Tests:** 28
- **Passing:** 25 (offline tests)
- **Skipped:** 3 (Roble integration tests - require credentials)

## Test Files

### Database Tests

#### `test_database.py` - Roble Integration (Online)
**Status:** Requires `RUN_ROBLE_TESTS=1` and `.env` credentials

Tests:
- `test_roble_connectivity` - Verifies Roble API is reachable
- `test_roble_schema_tables_exist` - Validates all required tables exist with correct schema
  - pine_users
  - pine_user_difficulty_profile
  - pine_exercise_sessions
  - pine_exercises
  - pine_difficulty_adjustments
  - pine_user_gamification (V2)
  - pine_user_operations (V2)
  - pine_batches_completados (V2)
  - pine_mini_jefes_intentos (V2)

#### `test_database_offline.py` - SQLite Offline Tests
**Status:** Always runs (no external dependencies)

Tests:
- `test_insert_offline` - Insert user, profiles, sessions, exercises
- `test_query_with_filters_offline` - Query with filters
- `test_update_offline` - Update user records
- `test_delete_offline` - Delete records
- `test_score_and_streak_offline` - Scoring formula and streak logic
- `test_record_regular_batch_offline` - Batch completion recording
- `test_record_miniboss_batch_offline` - Miniboss recording and level up

### V2 Component Tests

#### `test_v2_config_manager.py`
Tests:
- `test_system_config` - System-wide configuration
- `test_difficulty_config` - Per-operation difficulty settings
- `test_helper_methods` - Utility methods (get_by_level, level_exists)

#### `test_v2_evaluators.py`
Tests:
- `test_performance_evaluator` - User performance evaluation
- `test_scoring_calculator` - Score calculation logic
- `test_level_manager` - Level-up logic and thresholds

#### `test_v2_generators.py`
Tests:
- `test_exercise_generator_interpolation` - Exercise difficulty interpolation
- `test_operations_logic` - Operation-specific generation logic
- `test_batch_distribution` - Exercise distribution in batches
- `test_miniboss_batch` - Miniboss batch generation

#### `test_v2_miniboss.py`
Tests:
- `test_miniboss_detector` - Detection of miniboss trigger conditions
- `test_miniboss_evaluator` - Evaluation of miniboss completion

#### `test_v2_models.py`
Tests:
- `test_exercise` - Exercise model validation
- `test_exercise_result` - ExerciseResult model
- `test_batch_result` - BatchResult model
- `test_user_operation_state` - UserOperationState model
- `test_enums` - Enum types (Operacion, TipoRespuesta, BatchType)

#### `test_v2_persistence.py` - Batch Recording (Online)
**Status:** Requires `RUN_ROBLE_TESTS=1` and `.env` credentials

Tests:
- `test_record_regular_batch` - Regular batch persistence
- `test_record_miniboss_batch` - Miniboss batch persistence

## Running Tests

### Quick Commands

```bash
# Run all tests (offline only by default)
python -m pytest pineServer/tests -v

# Run with quiet output
python -m pytest pineServer/tests -q

# Run specific file
python -m pytest pineServer/tests/test_v2_generators.py -v

# Run specific test
python -m pytest pineServer/tests/test_v2_generators.py::test_batch_distribution -v

# Run with coverage
python -m pytest pineServer/tests --cov=pineServer/v2 --cov-report=html
```

### Enable Roble Tests

**Windows:**
```powershell
$env:RUN_ROBLE_TESTS=1
python -m pytest pineServer/tests -v
```

**Linux/Mac:**
```bash
RUN_ROBLE_TESTS=1 python -m pytest pineServer/tests -v
```

**Batch file (Windows):**
```bash
run_v2_tests.bat
```

## Test Configuration

### Environment Variables

- `RUN_ROBLE_TESTS` - Enable/disable Roble integration tests (default: 0)
  - Set to `1`, `true`, `True`, `yes`, or `on` to enable

### Required `.env` for Roble Tests

```env
ROBLE_PROJECT_ID=your_project_id
ROBLE_ADMIN_EMAIL=admin@example.com
ROBLE_ADMIN_PASSWORD=your_password
RUN_ROBLE_TESTS=1
```

## Test Patterns

### Offline Tests (SQLite)
- Use in-memory SQLite database
- No external dependencies
- Fast execution
- Test business logic and calculations

### Online Tests (Roble)
- Require database credentials
- Test actual schema and connectivity
- Gated behind `RUN_ROBLE_TESTS` flag
- Automatically skipped if credentials missing

### Fixtures
- `@pytest.fixture(scope="function")` - Fresh state per test
- `@pytest.fixture(scope="session")` - Shared across all tests
- `@pytest.fixture(autouse=True)` - Auto-applied to tests

## Expected Output

### Successful Run (Offline Only)
```
======================== test session starts =========================
collected 28 items

pineServer/tests/test_database.py::test_roble_connectivity PASSED
pineServer/tests/test_database.py::test_roble_schema_tables_exist SKIPPED
pineServer/tests/test_database_offline.py::test_insert_offline PASSED
pineServer/tests/test_database_offline.py::test_query_with_filters_offline PASSED
pineServer/tests/test_database_offline.py::test_update_offline PASSED
pineServer/tests/test_database_offline.py::test_delete_offline PASSED
pineServer/tests/test_database_offline.py::test_score_and_streak_offline PASSED
pineServer/tests/test_database_offline.py::test_record_regular_batch_offline PASSED
pineServer/tests/test_database_offline.py::test_record_miniboss_batch_offline PASSED
... (more tests)

================= 25 passed, 3 skipped in 6.72s ==================
```

### With Roble Tests Enabled
```
================= 28 passed in 12.45s ==================
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'pineServer'**
- Ensure you're running pytest from the project root
- Check that `pineServer/` exists in current directory

**Tests are skipped**
- Normal for Roble tests if `RUN_ROBLE_TESTS` not set
- Check `.env` file exists with valid credentials

**Fixture errors**
- Check that `__init__.py` exists in `pineServer/tests/`
- Verify pytest is installed: `pip install pytest`

**Database connection errors (Roble tests)**
- Verify credentials in `.env`
- Check network connectivity
- Ensure Roble API is accessible

## Adding New Tests

### Template

```python
"""
Test description
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pineServer.v2.your_module import YourClass

def test_your_feature():
    # Arrange
    instance = YourClass()
    
    # Act
    result = instance.your_method()
    
    # Assert
    assert result == expected_value
```

### Best Practices

1. **One test per function/method**
2. **Use descriptive test names**
3. **Follow AAA pattern** (Arrange, Act, Assert)
4. **Use fixtures for setup/teardown**
5. **Test edge cases and error conditions**
6. **Keep tests independent** (no test should depend on another)

## CI/CD Integration

For continuous integration, add to your pipeline:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    pip install -r pineServer/requirements.txt
    python -m pytest pineServer/tests -v --junitxml=test-results.xml

# For Roble tests in CI (use secrets)
- name: Run Integration Tests
  env:
    RUN_ROBLE_TESTS: 1
    ROBLE_PROJECT_ID: ${{ secrets.ROBLE_PROJECT_ID }}
    ROBLE_ADMIN_EMAIL: ${{ secrets.ROBLE_ADMIN_EMAIL }}
    ROBLE_ADMIN_PASSWORD: ${{ secrets.ROBLE_ADMIN_PASSWORD }}
  run: python -m pytest pineServer/tests -v
```
