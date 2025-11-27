# Pino Research Analytics & Model Management System - Implementation Plan

## Current State Analysis

### Currently Collected Data
1. **User Stats** (pine_users):
   - current_score
   - Basic profile info

2. **Session Data** (pine_exercise_sessions):
   - total_exercises, correct_answers
   - avg_difficulty, total_time_ms, score_earned
   - **NEW:** model_ref (references pine_models)

3. **Exercise Data** (pine_exercises):
   - exercise_type, operator
   - operand_1, operand_2, correct_answer, user_answer
   - difficulty_level
   - is_correct, time_taken_ms

4. **Difficulty Profiles** (pine_user_difficulty_profile):
   - operator, current_difficulty
   - success_rate, total_attempts, total_correct

5. **Difficulty Changes** (pine_difficulty_changes):
   - operator, previous_difficulty, new_difficulty
   - success_rate, avg_time_ms
   - adjustment_reason, total, correct

### Missing Data for Research
1. **User Demographics**:
   - age
   - grade/level
   - age_group (calculated field)

2. **Session Context**:
   - timestamp/date (for trend analysis)
   - model_ref is added but not yet populated

3. **Model Configuration** (pine_models):
   - modelName, exerciseGen, batchGenerator, difficultyCalculator
   - Created with "basicModel" as default

---

## Phase 1: Enhanced Data Collection & Model Integration

### 1.1 Update User Model
**File:** `pineServer/models.py`
```python
class User(BaseModel):
    user_ref: str
    email: str
    username: str
    current_score: int
    institution_ref: Optional[str]
    age: Optional[int]  # NEW
    grade: Optional[str]  # NEW (e.g., "K", "1", "2", etc.)
    age_group: Optional[str]  # NEW: calculated field (e.g., "5-7", "8-10", "11-13")
```

### 1.2 Model Configuration System
**File:** `pineServer/models.py`
```python
class ModelConfig(BaseModel):
    id: str = Field(..., alias="_id")
    model_name: str
    exercise_gen: str  # Class name or identifier
    batch_generator: str
    difficulty_calculator: str
    description: Optional[str]
    active: bool = True
    created_at: Optional[str]

class ModelAssignment(BaseModel):
    model_ref: str
    assignment_type: str  # "global", "institution", "grade", "age", "ab_test"
    institution_ref: Optional[str]
    grade: Optional[str]
    age_min: Optional[int]
    age_max: Optional[int]
    ab_group: Optional[str]  # "A" or "B"
    priority: int = 0  # Higher priority wins in conflicts
```

### 1.3 Update Session to Track Model
**File:** `pineServer/main.py` - start_session endpoint
```python
# Determine which model to use
model_ref = determine_model_for_user(user_ref, age, grade, institution_ref)

session_data = {
    "user_ref": request.user_ref,
    "model_ref": model_ref,  # Now populated!
    "total_exercises": len(exercises),
    # ... rest
}
```

---

## Phase 2: Advanced Analytics API

### 2.1 New Analytics Endpoints

#### Get Detailed User Analytics
```python
@app.get("/api/analytics/user/{user_ref}")
async def get_user_analytics(
    user_ref: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """
    Returns:
    - Difficulty progression over time (per operator)
    - Factors affecting each difficulty change
    - Session-by-session breakdown
    - Model performance comparison (if user used multiple models)
    """
```

#### Get Cohort Analytics
```python
@app.get("/api/analytics/cohort")
async def get_cohort_analytics(
    age_group: Optional[str] = None,
    grade: Optional[str] = None,
    institution_ref: Optional[str] = None,
    model_ref: Optional[str] = None
):
    """
    Returns:
    - Average difficulty by operator for cohort
    - Success rate trends
    - Comparison across different cohorts
    """
```

#### Get Model Performance
```python
@app.get("/api/analytics/model/{model_ref}")
async def get_model_performance(model_ref: str):
    """
    Returns:
    - Total users using this model
    - Average success rates
    - Difficulty distribution
    - Comparison with other models
    """
```

### 2.2 Difficulty Change Analysis
```python
@app.get("/api/analytics/difficulty-changes/{user_ref}")
async def get_difficulty_changes(user_ref: str, operator: Optional[str] = None):
    """
    Returns detailed log of difficulty changes with:
    - timestamp
    - previous_difficulty → new_difficulty
    - success_rate that triggered change
    - avg_time_ms
    - adjustment_reason
    - session context
    """
```

---

## Phase 3: Admin Dashboard Frontend

### 3.1 New Admin Stats Page
**File:** `r_pino/app/admin-stats.tsx` (new file)

Components:
1. **User Selector Dropdown**
   - Search/filter users
   - Group by institution/grade/age

2. **Difficulty Progression Chart**
   - Line chart showing difficulty over time for each operator
   - Interactive: hover to see session details
   - Show what factors caused each change

3. **Cohort Comparison View**
   - Select multiple cohorts (by age group, grade, institution)
   - Compare difficulty progression
   - Show distribution charts

4. **Model Performance Dashboard**
   - Table showing all models
   - Metrics: # users, avg success rate, avg difficulty
   - A/B test results comparison

5. **Session Detail Drill-Down**
   - Click on any data point to see session details
   - View individual exercises
   - See exact difficulty calculation factors

### 3.2 Visualization Libraries
Consider adding:
- `react-native-svg-charts` for React Native
- `victory-native` for cross-platform charts
- Or for web-only admin: use `recharts` or `chart.js`

---

## Phase 4: Model Management System

### 4.1 Model Assignment Logic
```python
def determine_model_for_user(user_ref: str, age: int, grade: str, institution_ref: str) -> str:
    """
    Priority order:
    1. User-specific override (if exists in DB)
    2. A/B test assignment
    3. Age-group specific
    4. Grade-specific
    5. Institution-specific
    6. Global default (basicModel)
    """
    # Query pine_model_assignments ordered by priority
    # Return first match
```

### 4.2 Model Assignment API
```python
@app.post("/api/admin/model-assignment")
async def create_model_assignment(assignment: ModelAssignment):
    """
    Assign a model to:
    - All users
    - Specific institution
    - Specific grade level
    - Age range
    - A/B test group
    """

@app.get("/api/admin/model-assignments")
async def list_model_assignments():
    """List all current model assignments"""
```

### 4.3 Dynamic Model Loading (Future Enhancement)
```python
# Instead of hardcoded container
def get_container_for_model(model_ref: str) -> ServiceContainer:
    model = roble_client.read_table("pine_models", {"_id": model_ref})[0]
    
    # Dynamically instantiate based on model config
    problem_gen = instantiate_class(model["exercise_gen"])
    batch_gen = instantiate_class(model["batch_generator"])
    difficulty_calc = instantiate_class(model["difficulty_calculator"])
    
    container = ServiceContainer()
    container.set_problem_generator(problem_gen)
    container.set_batch_generator(batch_gen)
    container.set_profile_evaluator(difficulty_calc)
    
    return container
```

---

## Implementation Roadmap

### Sprint 1: Data Foundation (Week 1)
- [ ] Add age and grade to pine_users table
- [ ] Update user registration to collect age/grade
- [ ] Add model_ref population in start_session
- [ ] Create pine_model_assignments table
- [ ] Implement determine_model_for_user() logic

### Sprint 2: Analytics Backend (Week 2)
- [ ] Implement user analytics endpoint with time-series data
- [ ] Implement cohort analytics endpoint
- [ ] Implement difficulty changes detailed endpoint
- [ ] Add model performance analytics

### Sprint 3: Admin Dashboard UI (Week 3)
- [ ] Create admin stats page layout
- [ ] Implement user selector dropdown
- [ ] Add difficulty progression charts
- [ ] Create cohort comparison view

### Sprint 4: Advanced Features (Week 4)
- [ ] Model assignment management UI
- [ ] A/B test configuration
- [ ] Export data for external analysis
- [ ] Real-time dashboard updates

---

## Data Examples

### Difficulty Change Tracking
```json
{
  "user_ref": "abc123",
  "operator": "+",
  "session_id": "sess_456",
  "timestamp": "2025-11-27T10:00:00Z",
  "previous_difficulty": 3.0,
  "new_difficulty": 3.5,
  "factors": {
    "success_rate": 0.85,
    "avg_time_ms": 4500,
    "total_attempts": 10,
    "correct_count": 8,
    "adjustment_reason": "High success rate, above 80% threshold"
  },
  "model_ref": "basicModel"
}
```

### Cohort Analytics Response
```json
{
  "cohort": {
    "age_group": "8-10",
    "grade": "3",
    "size": 45
  },
  "difficulty_stats": {
    "+": {"avg": 3.2, "min": 1.0, "max": 5.5, "stddev": 1.1},
    "-": {"avg": 3.8, "min": 1.5, "max": 6.0, "stddev": 1.3},
    "*": {"avg": 2.5, "min": 1.0, "max": 4.5, "stddev": 0.9},
    "/": {"avg": 2.1, "min": 1.0, "max": 3.8, "stddev": 0.7}
  },
  "success_rate": 0.76,
  "avg_session_score": 145
}
```

---

## Next Steps

Would you like me to:
1. **Start with Phase 1**: Update the data model to include age/grade and implement model assignment?
2. **Start with Analytics**: Create the detailed analytics endpoints first?
3. **Start with UI**: Create the admin dashboard with mock data?
4. **All together**: Implement the full system incrementally?

Let me know your priority and I'll begin implementation!
