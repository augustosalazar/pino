# PINO - Adaptive Math Practice Platform

PINO is an adaptive learning platform for math practice with gamification features, designed to help students improve their arithmetic skills through personalized difficulty adjustment and engaging game mechanics.

## Project Structure

```
pino/
├── pineServer/              # Backend FastAPI server
│   ├── main.py             # API endpoints
│   ├── v2/                 # V2 Gamification system (active)
│   │   ├── config_manager.py
│   │   ├── exercise_generator.py
│   │   ├── batch_generator.py
│   │   ├── performance_evaluator.py
│   │   ├── scoring_calculator.py
│   │   ├── dominio_level_manager.py
│   │   ├── miniboss_detector.py
│   │   ├── miniboss_evaluator.py
│   │   ├── batch_recorder.py
│   │   └── models.py
│   ├── tests/              # Test suite
│   │   ├── test_database.py              # Roble integration tests
│   │   ├── test_database_offline.py      # SQLite offline tests
│   │   ├── test_v2_config_manager.py
│   │   ├── test_v2_evaluators.py
│   │   ├── test_v2_generators.py
│   │   ├── test_v2_miniboss.py
│   │   ├── test_v2_models.py
│   │   └── test_v2_persistence.py        # Batch recording tests
│   ├── roble_client.py     # Roble database client
│   ├── datetime_utils.py   # Timezone utilities (Colombia)
│   ├── container.py        # Dependency injection
│   └── requirements.txt
├── r_pino/                  # React Native mobile client
└── pythonClient/            # Python test client
```

## Features

### V2 Gamification System (Active)

- **Adaptive Difficulty**: Dynamic adjustment based on user performance
- **Dominio Levels**: 10 progressive difficulty levels (1-10)
- **Miniboss Challenges**: Special validation exercises to level up
- **Gamification**:
  - **PP (Pino Points)**: Session-based rewards
  - **PD (Pino Dollars)**: Global currency
  - **XP (Experience Points)**: Progress tracking
  - **Daily Streaks**: Consecutive day bonuses (up to 30 days)
- **Operations**: Addition, Subtraction, Multiplication, Division
- **Response Types**: Multiple choice and manual input
- **Endless Scroller Mode**: Continuous practice batches

### Database

- **Roble Backend**: PostgreSQL-based cloud database
- **Tables**:
  - `pine_users`: User accounts
  - `pine_user_gamification`: Points, XP, streaks
  - `pine_user_operations`: Per-operation difficulty levels
  - `pine_batches_completados`: Completed batch logs
  - `pine_mini_jefes_intentos`: Miniboss attempt records
  - `pine_exercise_sessions`: Historical session data
  - `pine_exercises`: Individual exercise records

## Getting Started

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- Roble database credentials (for production)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/augustosalazar/pino.git
   cd pino
   ```

2. **Install dependencies**
   ```bash
   cd pineServer
   pip install -r requirements.txt
   ```

3. **Configure environment**
   
   Create a `.env` file in `pineServer/` with your Roble credentials:
   ```env
   ROBLE_PROJECT_ID=your_project_id
   ROBLE_ADMIN_EMAIL=admin@example.com
   ROBLE_ADMIN_PASSWORD=your_password
   RUN_ROBLE_TESTS=0  # Set to 1 to enable integration tests
   ```

### Running the Server

**Windows:**
```bash
start_v2_server.bat
```

**Linux/Mac:**
```bash
cd pineServer
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Testing

The project has a comprehensive test suite with **28 tests** covering all V2 components.

### Test Organization

- **Offline Tests** (SQLite in-memory): Run without Roble connectivity
  - CRUD operations
  - Gamification logic (scoring, streaks)
  - Batch recording simulation
  
- **Online Tests** (Roble integration): Require credentials and `RUN_ROBLE_TESTS=1`
  - Schema validation
  - Database connectivity
  - Real persistence testing

### Running Tests

**Run all tests (offline only by default):**
```bash
python -m pytest pineServer/tests -v
```

**Run specific test categories:**
```bash
# Database tests only
python -m pytest pineServer/tests/test_database*.py -v

# V2 component tests
python -m pytest pineServer/tests/test_v2_*.py -v

# Specific test file
python -m pytest pineServer/tests/test_v2_generators.py -v
```

**Run with Roble integration tests:**
```bash
# Windows
$env:RUN_ROBLE_TESTS=1
python -m pytest pineServer/tests -v

# Linux/Mac
RUN_ROBLE_TESTS=1 python -m pytest pineServer/tests -v
```

**Using batch file (Windows):**
```bash
run_v2_tests.bat
```

### Test Coverage

| Component | Tests | Coverage |
|-----------|-------|----------|
| Config Manager | 3 | System config, difficulty config, helpers |
| Evaluators | 3 | Performance, scoring, level management |
| Generators | 4 | Interpolation, operations, batch distribution, miniboss |
| Miniboss | 2 | Detection, evaluation |
| Models | 5 | Exercise, results, state, enums |
| Persistence | 2 (online) + 2 (offline) | Batch recording, miniboss recording |
| Database | 2 (online) + 7 (offline) | CRUD, scoring, streaks, schema validation |

**Total: 28 tests** - 24-25 passing, 3-4 skipped (Roble tests when disabled)

### Expected Test Output

```
======================== test session starts =========================
collected 28 items

pineServer/tests/test_database.py::test_roble_connectivity SKIPPED
pineServer/tests/test_database.py::test_roble_schema_tables_exist SKIPPED
pineServer/tests/test_database_offline.py::test_insert_offline PASSED
pineServer/tests/test_database_offline.py::test_query_with_filters_offline PASSED
pineServer/tests/test_database_offline.py::test_update_offline PASSED
pineServer/tests/test_database_offline.py::test_delete_offline PASSED
pineServer/tests/test_database_offline.py::test_score_and_streak_offline PASSED
pineServer/tests/test_database_offline.py::test_record_regular_batch_offline PASSED
pineServer/tests/test_database_offline.py::test_record_miniboss_batch_offline PASSED
pineServer/tests/test_v2_config_manager.py::test_system_config PASSED
pineServer/tests/test_v2_config_manager.py::test_difficulty_config PASSED
pineServer/tests/test_v2_config_manager.py::test_helper_methods PASSED
pineServer/tests/test_v2_evaluators.py::test_performance_evaluator PASSED
pineServer/tests/test_v2_evaluators.py::test_scoring_calculator PASSED
pineServer/tests/test_v2_evaluators.py::test_level_manager PASSED
pineServer/tests/test_v2_generators.py::test_exercise_generator_interpolation PASSED
pineServer/tests/test_v2_generators.py::test_operations_logic PASSED
pineServer/tests/test_v2_generators.py::test_batch_distribution PASSED
pineServer/tests/test_v2_generators.py::test_miniboss_batch PASSED
pineServer/tests/test_v2_miniboss.py::test_miniboss_detector PASSED
pineServer/tests/test_v2_miniboss.py::test_miniboss_evaluator PASSED
pineServer/tests/test_v2_models.py::test_exercise PASSED
pineServer/tests/test_v2_models.py::test_exercise_result PASSED
pineServer/tests/test_v2_models.py::test_batch_result PASSED
pineServer/tests/test_v2_models.py::test_user_operation_state PASSED
pineServer/tests/test_v2_models.py::test_enums PASSED
pineServer/tests/test_v2_persistence.py::test_record_regular_batch SKIPPED
pineServer/tests/test_v2_persistence.py::test_record_miniboss_batch SKIPPED

================= 24 passed, 4 skipped in 3.10s ==================
```

## API Endpoints

### Core Endpoints

- `POST /v2/batch` - Get a new exercise batch
- `POST /v2/batch/submit` - Submit batch results
- `GET /v2/profile/{user_ref}` - Get user gamification profile
- `GET /v2/operations/{user_ref}` - Get user operation states
- `GET /v2/leaderboard` - Get global leaderboard

### Admin Endpoints

- `POST /admin/create-user` - Create new user
- `GET /admin/stats` - Get system statistics

Full API documentation available at `/docs` when server is running.

## Gamification Mechanics

### Scoring System

**Base Score Formula:**
```
score = (correct_exercises × (5 + difficulty)) + 10 - (2 × errors)
minimum score: 0
```

**Example:** 8/10 correct at difficulty 2.0 = `8×7 + 10 - 4 = 62 points`

### Streak System

- **Increment**: +1 for first qualifying batch of the day (≥4 correct)
- **Reset**: Skipping a day resets streak to 1
- **Same-day**: Multiple batches on same day don't increment
- **Maximum**: 30 days
- **Bonus**: `5 + (3 × streak_days)` PP per batch

### Level Progression

1. Start at **Level 1** (difficulty 1.0-2.0)
2. Complete batches with ≥80% accuracy to increase invisible level
3. When invisible level reaches threshold, **Miniboss** is triggered
4. Pass Miniboss (≥80% accuracy) to advance to next level
5. Repeat through **Level 10** (max)

### Miniboss Mechanics

- Triggered automatically when ready to level up
- 6 exercises at current level threshold
- Must achieve ≥80% to pass
- Success: Level up, rewards, reset batch counter
- Failure: Retry after more practice batches

## Timezone Configuration

The system uses **Colombia timezone (America/Bogota)** for all timestamps via `datetime_utils.py`:
- `now_utc_iso()` - Current time in Colombia timezone (ISO format)
- `parse_iso_to_bogota()` - Parse ISO string to Bogota time

## Development

### Adding New Tests

1. Create test file in `pineServer/tests/`
2. Name format: `test_<component>.py`
3. Use pytest fixtures for setup/teardown
4. Follow existing patterns (online vs offline)

### Code Organization

- **V2 System**: Modular components in `pineServer/v2/`
- **Dependency Injection**: Use `container.py` for singletons
- **Config Management**: Centralized in `config_manager.py`
- **Models**: Type-safe dataclasses in `models.py`

## Troubleshooting

### Tests Failing

1. **Import Errors**: Ensure you're in project root when running pytest
2. **Roble Tests Skipping**: Normal if `RUN_ROBLE_TESTS` not set
3. **Connection Errors**: Check `.env` credentials for Roble tests

### Server Issues

1. **Port in Use**: Kill existing uvicorn process or change port
2. **Database Errors**: Verify Roble credentials in `.env`
3. **Missing Tables**: Run `create_tables.py` to initialize schema

## Contributing

1. Create feature branch from `copilotMode`
2. Add tests for new functionality
3. Ensure all tests pass: `python -m pytest pineServer/tests -v`
4. Update documentation as needed

## License

[Your License Here]

## Contact

Repository: https://github.com/augustosalazar/pino
Owner: augustosalazar
