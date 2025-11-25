# R_PINE - Math Exercise Learning Platform

## Project Overview

R_PINE is a comprehensive math learning system consisting of three components:
1. **r_pine** - React Native mobile application
2. **pineServer** - Python middleware server
3. **Roble** - Authentication and database backend

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         R_PINE SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   r_pine     │         │  pineServer  │                 │
│  │              │ ◄─────► │              │                 │
│  │ React Native │         │    Python    │                 │
│  │              │         │              │                 │
│  └──────────────┘         └──────┬───────┘                 │
│                                   │                          │
│                                   ▼                          │
│                          ┌────────────────┐                 │
│                          │     Roble      │                 │
│                          │                │                 │
│                          │ Auth + DB      │                 │
│                          └────────────────┘                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## User Flow

### 1. Authentication & Initial State
- User logs into the app
- App displays user's current score
- Profile loads with difficulty levels per operator

### 2. Exercise Request
- App requests new exercise set from pineServer
- Server queries user's history from Roble
- Server analyzes performance patterns

### 3. Exercise Generation
- Server builds personalized exercise set
- Each exercise includes:
  - **Type**: Multiple choice (Type 1) or text input (Type 2)
  - **Operands**: Two numbers
  - **Operator**: +, -, *, /
  - **Options**: 4 choices for Type 1
  - **Correct Answer**: Solution
  - **Difficulty Level**: 1.0 - 10.0

### 4. User Interaction
- App presents each exercise
- Tracks statistics:
  - Time per exercise
  - Answer correctness
  - Session metadata

### 5. Results & Adaptation
- App sends stats to Roble
- Server adjusts difficulty based on performance
- User profile updated for next session

## Database Schema

### Table 1: users
**Purpose**: Core user profiles

| Column | Type | Description |
|--------|------|-------------|
| user_id | uuid | Primary key, matches Roble auth ID |
| email | varchar | Unique, not null |
| username | varchar | Display name |
| current_score | int4 | Accumulated points |
| created_at | timestamptz | Registration date |
| updated_at | timestamptz | Last profile update |

**Indexes**: email

### Table 2: exercise_sessions
**Purpose**: Group exercises into learning sessions

| Column | Type | Description |
|--------|------|-------------|
| session_id | uuid | Primary key |
| user_id | uuid | Foreign key → users |
| started_at | timestamptz | Session start |
| completed_at | timestamptz | Session end (nullable) |
| total_exercises | int4 | Count of exercises |
| correct_answers | int4 | Count of correct responses |
| avg_difficulty | numeric | Average difficulty |
| total_time_ms | int4 | Total milliseconds |
| score_earned | int4 | Points from this session |

**Indexes**: user_id, completed_at

### Table 3: exercises
**Purpose**: Individual exercise details and responses

| Column | Type | Description |
|--------|------|-------------|
| exercise_id | uuid | Primary key |
| session_id | uuid | Foreign key → exercise_sessions |
| user_id | uuid | Foreign key → users |
| exercise_type | int2 | 1=multiple choice, 2=input |
| operator | varchar | +, -, *, / |
| operand_1 | int4 | First number |
| operand_2 | int4 | Second number |
| correct_answer | int4 | Solution |
| user_answer | int4 | User's response (nullable) |
| options | jsonb | 4 choices for Type 1 (nullable) |
| difficulty_level | numeric | Calculated difficulty |
| is_correct | bool | Answer correctness (nullable) |
| time_taken_ms | int4 | Response time (nullable) |
| presented_at | timestamptz | When shown |
| answered_at | timestamptz | When answered (nullable) |

**Indexes**: session_id, user_id, operator, presented_at

### Table 4: user_difficulty_profile
**Purpose**: Track per-operator difficulty levels

| Column | Type | Description |
|--------|------|-------------|
| profile_id | uuid | Primary key |
| user_id | uuid | Foreign key → users |
| operator | varchar | +, -, *, / |
| current_difficulty | numeric | Current level (1.0-10.0) |
| success_rate | numeric | Recent success percentage |
| total_attempts | int4 | Historical attempt count |
| total_correct | int4 | Historical correct count |
| updated_at | timestamptz | Last adjustment |

**Unique Constraint**: (user_id, operator)
**Indexes**: (user_id, operator)

### Table 5: difficulty_adjustments
**Purpose**: History of difficulty changes

| Column | Type | Description |
|--------|------|-------------|
| adjustment_id | uuid | Primary key |
| user_id | uuid | Foreign key → users |
| session_id | uuid | Foreign key → sessions (nullable) |
| operator | varchar | +, -, *, / |
| previous_difficulty | numeric | Level before |
| new_difficulty | numeric | Level after |
| reason | varchar | Explanation |
| adjusted_at | timestamptz | When adjusted |

**Indexes**: user_id, adjusted_at

## Difficulty System

### Scale: 1.0 - 10.0

| Level | Range | Name | Operand Range | Example |
|-------|-------|------|---------------|---------|
| 1 | 1.0-2.0 | Very Easy | 1-9 | 3 + 5 = 8 |
| 2 | 2.1-3.5 | Easy | 1-25 | 8 + 17 = 25 |
| 3 | 3.6-5.0 | Intermediate | 10-99 | 45 + 67 = 112 |
| 4 | 5.1-7.0 | Medium-High | 10-250 | 89 + 156 = 245 |
| 5 | 7.1-8.5 | Difficult | 100-500 | 234 + 387 = 621 |
| 6 | 8.6-10.0 | Very Hard | 100-999 | 567 + 834 = 1401 |

### Operator Modifiers

Applied to base difficulty:
- **Addition (+)**: +0.0 (baseline)
- **Subtraction (-)**: +0.3
- **Multiplication (*)**: +0.5
- **Division (/)**: +0.8

Final difficulty clamped to [1.0, 10.0]

### Adjustment Rules

After each session, per operator:

| Success Rate | Adjustment | Reason |
|--------------|------------|--------|
| ≥ 90% | +1.0 | Complete mastery |
| 80-89% | +0.5 | Good performance |
| 51-79% | 0.0 | Optimal learning zone |
| 31-50% | -0.5 | Too challenging |
| ≤ 30% | -1.0 | Significantly too hard |

## Exercise Generation Algorithm

### High-Level Process

1. **Query User Profile**
   - Fetch difficulty levels for each operator
   - Initialize at 1.0 for new users

2. **Create Balanced Set**
   - Default: 10 exercises per session
   - Distribution: 40% addition, 20% each for -, *, /
   - Randomize order

3. **Generate Each Exercise**
   - Select operator
   - Get user's current difficulty for that operator
   - Calculate operand ranges based on difficulty
   - Generate valid operands (considering constraints)
   - Calculate correct answer
   - Randomly assign Type 1 (66%) or Type 2 (33%)
   - For Type 1: generate 3 plausible wrong answers
   - Apply operator modifier to difficulty

4. **Return Exercise Set**

### Operand Constraints

**Addition**: No constraints
**Subtraction**: operand_1 ≥ operand_2 (no negatives)
**Multiplication**: Adjusted ranges to avoid huge results
**Division**: operand_1 = operand_2 × quotient (exact division only)

### Option Generation (Type 1)

1. Include correct answer
2. Calculate variation: max(1, 20% of correct_answer)
3. Generate 3 unique wrong answers:
   - Small negative offset: [-variation, -1]
   - Small positive offset: [1, variation]
   - Large offsets: [-10, -1] or [1, 10]
4. Validate: positive, unique, ≠ correct
5. Shuffle all 4 options

## Scoring System

**Points per exercise**: difficulty_level × 10

Example:
- Difficulty 3.5 exercise = 35 points if correct
- Session with 7/10 correct at avg difficulty 4.2 = 294 points

## Operator Distribution

Per 10-exercise set:
- **3-4 additions** (40%)
- **2 subtractions** (20%)
- **2 multiplications** (20%)
- **2 divisions** (20%)

## Exercise Type Distribution

- **Type 1 (Multiple Choice)**: 66%
- **Type 2 (Text Input)**: 33%

## Admin Credentials

**Email**: admin@pine.com
**Password**: ThePassword!1

## Technology Stack

### r_pine (Mobile App)
- React Native
- TypeScript
- Expo

### pineServer (Middleware)
- Python 3.8+
- requests library
- FastAPI or Flask (to be implemented)

### Roble (Backend)
- PostgreSQL
- Authentication API
- Database API

## Data Flow Examples

### Example 1: New User First Session

1. User signs up → Roble creates auth user
2. pineServer creates user profile in `users` table
3. pineServer initializes difficulty profiles (all operators at 1.0)
4. App requests exercises
5. pineServer generates 10 easy exercises (operands 1-9)
6. User completes with 80% success
7. pineServer increases difficulty to 1.5 for all operators
8. Session stats saved to `exercise_sessions` and `exercises`

### Example 2: Experienced User

1. User logs in → current_score: 15,420
2. App requests exercises
3. pineServer checks difficulty profile:
   - Addition: 6.5
   - Subtraction: 5.8
   - Multiplication: 4.2
   - Division: 3.9
4. Generates mixed difficulty set
5. User struggles with division (40% success)
6. Division difficulty drops to 3.4
7. Other operators maintain or increase

## Next Implementation Steps

### Phase 1: Database Setup ✓
- [x] Define schema
- [x] Map to Roble types
- [x] Create table creation script

### Phase 2: pineServer Core
- [ ] Set up Flask/FastAPI framework
- [ ] Implement authentication with Roble
- [ ] Create exercise generation endpoint
- [ ] Create session submission endpoint
- [ ] Implement difficulty adjustment logic

### Phase 3: r_pine App
- [ ] Set up React Native project
- [ ] Create authentication screens
- [ ] Build exercise display components
- [ ] Implement answer input/selection
- [ ] Create progress tracking UI
- [ ] Connect to pineServer API

### Phase 4: Testing & Refinement
- [ ] Unit tests for algorithms
- [ ] Integration tests
- [ ] User experience testing
- [ ] Performance optimization
- [ ] Difficulty calibration

## Configuration Requirements

### Environment Variables

**pineServer**:
```
ROBLE_PROJECT_ID=your_project_id
ROBLE_BASE_URL=https://roble-api.openlab.uninorte.edu.co
ADMIN_EMAIL=admin@pine.com
ADMIN_PASSWORD=ThePassword!1
```

**r_pine**:
```
EXPO_PUBLIC_ROBLE_PROJECT_ID=your_project_id
EXPO_PUBLIC_API_URL=http://your-server-url
```

## Security Considerations

1. Admin credentials should be changed after initial setup
2. API endpoints should validate JWT tokens from Roble
3. Input validation on all user submissions
4. Rate limiting on exercise generation
5. Secure HTTPS communication

## Success Metrics

- User retention rate
- Average session completion time
- Difficulty progression rate
- Success rate distribution (target: 60-80%)
- User engagement (sessions per week)

---

**Project Start Date**: 2025-11-24
**Status**: Phase 1 - Database Design Complete
