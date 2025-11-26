# PineServer - R_PINE Math Exercise API

FastAPI server for generating adaptive math exercises and tracking user progress.

## Features

- ✅ Adaptive difficulty based on user performance
- ✅ Personalized exercise generation
- ✅ Session tracking and statistics
- ✅ Real-time difficulty adjustments
- ✅ RESTful API with automatic documentation

## Setup


### on Docker
```bash
docker build --tag pineserveri  .
```

```bash
 docker run -d -it -p 5050:8000 --env-file .env --restart unless-stopped --name pineserver pineserveri
```
### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```env
ROBLE_PROJECT_ID=your_project_id
ROBLE_BASE_URL=https://roble-api.openlab.uninorte.edu.co
ADMIN_EMAIL=admin@pine.com
ADMIN_PASSWORD=your_password
```

### 3. Run the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check

```http
GET /
```

**Response:**
```json
{
  "status": "ok",
  "service": "PineServer",
  "version": "1.0.0"
}
```

### 2. Start Session

```http
POST /api/sessions/start
```

**Request Body:**
```json
{
  "user_ref": "1c01b4d4-2927-4381-8741-659dd7a101af",
  "num_exercises": 10
}
```

**Response:**
```json
{
  "session_id": "abc123",
  "exercises": [
    {
      "exercise_type": 1,
      "operator": "+",
      "operand_1": 5,
      "operand_2": 3,
      "correct_answer": 8,
      "options": [8, 7, 9, 10],
      "difficulty_level": 1.5
    }
  ],
  "user_profile": {
    "+": 1.5,
    "-": 1.3,
    "*": 2.0,
    "/": 1.8
  }
}
```

### 3. Complete Session

```http
POST /api/sessions/{session_id}/complete
```

**Request Body:**
```json
{
  "exercises": [
    {
      "exercise_type": 1,
      "operator": "+",
      "operand_1": 5,
      "operand_2": 3,
      "correct_answer": 8,
      "options": [8, 7, 9, 10],
      "difficulty_level": 1.5,
      "user_answer": 8,
      "is_correct": true,
      "time_taken_ms": 5000
    }
  ]
}
```

**Response:**
```json
{
  "session_id": "abc123",
  "total_exercises": 10,
  "correct_answers": 7,
  "score_earned": 175,
  "difficulty_adjustments": {
    "+": {"old": 1.5, "new": 2.0}
  }
}
```

### 4. Get User Profile

```http
GET /api/users/{user_ref}/profile
```

**Response:**
```json
{
  "user_id": "user123",
  "profiles": {
    "+": {
      "current_difficulty": 2.0,
      "success_rate": 85.0,
      "total_attempts": 50,
      "total_correct": 42
    }
  }
}
```

### 5. Get User Stats

```http
GET /api/users/{user_ref}/stats
```

**Response:**
```json
{
  "user_id": "user123",
  "total_sessions": 15,
  "total_exercises": 150,
  "total_correct": 120,
  "accuracy": 80.0,
  "current_score": 2400,
  "difficulty_by_operator": {
    "+": 2.0,
    "-": 1.8,
    "*": 2.5,
    "/": 2.2
  }
}
```

## Project Structure

```
pineServer/
├── main.py                   # FastAPI application
├── models.py                 # Pydantic models
├── roble_client.py          # Roble database client
├── exercise_generator.py    # Exercise generation logic
├── difficulty_manager.py    # Difficulty adjustment logic
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## Difficulty System

### Levels (1.0 - 10.0)

| Level | Range | Operands | Example |
|-------|-------|----------|---------|
| 1 | 1.0-2.0 | 1-9 | 3 + 5 |
| 2 | 2.1-3.5 | 1-25 | 8 + 17 |
| 3 | 3.6-5.0 | 10-99 | 45 + 67 |
| 4 | 5.1-7.0 | 10-250 | 89 + 156 |
| 5 | 7.1-8.5 | 100-500 | 234 + 387 |
| 6 | 8.6-10.0 | 100-999 | 567 + 834 |

### Operator Modifiers

- Addition (+): +0.0
- Subtraction (-): +0.3
- Multiplication (*): +0.5
- Division (/): +0.8

### Adjustment Rules

| Success Rate | Adjustment | Reason |
|--------------|------------|--------|
| ≥ 90% | +1.0 | Complete mastery |
| 80-89% | +0.5 | Good performance |
| 51-79% | 0.0 | Optimal learning |
| 31-50% | -0.5 | Too challenging |
| ≤ 30% | -1.0 | Too hard |

## Exercise Distribution

Per 10-exercise set:
- 40% Addition (+)
- 20% Subtraction (-)
- 20% Multiplication (*)
- 20% Division (/)

## Testing

Test the server:

```bash
# Install dev dependencies (if needed)
pip install pytest httpx

# Run tests
pytest
```

Or use the test database script:

```bash
python test_database_v2.py
```

## Development

Enable auto-reload:

```bash
uvicorn main:app --reload
```

## Production

For production deployment:

1. Set proper CORS origins in `main.py`
2. Use environment variables from secure sources
3. Run with production ASGI server (Gunicorn + Uvicorn)
4. Enable HTTPS
5. Add rate limiting
6. Add authentication middleware

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## License

Copyright © 2025 R_PINE Project
