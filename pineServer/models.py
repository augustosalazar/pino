"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from enum import Enum


class Operator(str, Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"


class ExerciseType(int, Enum):
    MULTIPLE_CHOICE = 1
    TEXT_INPUT = 2


class Exercise(BaseModel):
    """Single exercise"""
    exercise_type: ExerciseType
    operator: Operator
    operand_1: int
    operand_2: int
    correct_answer: int
    options: Optional[List[int]] = None  # Only for type 1
    difficulty_level: float


class ExerciseWithAnswer(Exercise):
    """Exercise with user's answer"""
    user_answer: int
    is_correct: bool
    time_taken_ms: int


class Institution(BaseModel):
    """Institution/Company model"""
    id: str = Field(..., alias="_id")
    name: str


class EnsureUserRequest(BaseModel):
    """Request to ensure user exists in database"""
    user_ref: str = Field(..., description="User's Roble auth ID")
    email: str = Field(..., description="User's email")
    username: Optional[str] = Field(None, description="User's display name")
    institution_ref: Optional[str] = Field(None, description="Institution reference ID")


class UpdateProfileRequest(BaseModel):
    """Request to update user profile"""
    age: Optional[int] = Field(None, description="User's age", ge=1, le=120)
    grade: Optional[str] = Field(None, description="User's grade/year")


class InstitutionStatsRequest(BaseModel):
    """Request to get institution statistics with filters"""
    institution_ref: str = Field(..., description="Institution reference ID")
    age_min: Optional[int] = Field(None, description="Minimum age filter")
    age_max: Optional[int] = Field(None, description="Maximum age filter")
    grade: Optional[str] = Field(None, description="Grade filter")


class StartSessionRequest(BaseModel):
    """Request to start a new session"""
    user_ref: str = Field(..., description="User's Roble auth ID")
    num_exercises: int = Field(10, ge=1, le=50, description="Number of exercises")
    batch_type: str = Field("regular", description="Type of batch: 'regular', 'miniboss', or 'endless'")


class StartSessionResponse(BaseModel):
    """Response with session and exercises"""
    session_id: str
    exercises: List[Exercise]
    user_profile: Dict[str, float]  # operator -> difficulty


class CompleteSessionRequest(BaseModel):
    """Request to complete a session"""
    exercises: List[ExerciseWithAnswer]


class CompleteSessionResponse(BaseModel):
    """Response after completing session"""
    session_id: str
    total_exercises: int
    correct_answers: int
    score_earned: int
    difficulty_adjustments: Dict[str, Dict[str, float]]  # operator -> {old, new}
    gamification: Optional[Dict] = None  # Gamification rewards info
    endless_info: Optional[Dict] = None  # For endless mode: streak, best_streak


class UserProfile(BaseModel):
    """User's difficulty profile"""
    user_id: str
    profiles: Dict[str, Dict]  # operator -> profile data


class UserStats(BaseModel):
    """User statistics"""
    user_id: str
    total_sessions: int
    total_exercises: int
    total_correct: int
    accuracy: float
    current_score: int
    difficulty_by_operator: Dict[str, float]


class Model(BaseModel):
    """Model configuration"""
    id: str = Field(..., alias="_id")
    model_name: str
    exercise_gen: str
    batch_generator: str
    difficulty_calculator: str
    description: Optional[str] = None
    active: bool = True


class ModelAssignment(BaseModel):
    """Model assignment configuration"""
    id: Optional[str] = Field(None, alias="_id")
    model_ref: str = Field(..., description="Model ID to assign")
    assignment_type: str = Field(..., description="Type: global, institution, grade, age, ab_test")
    institution_ref: Optional[str] = Field(None, description="Institution ID filter")
    grade: Optional[str] = Field(None, description="Grade filter")
    age_min: Optional[int] = Field(None, description="Minimum age filter")
    age_max: Optional[int] = Field(None, description="Maximum age filter")
    ab_group: Optional[str] = Field(None, description="A/B test group: A or B")
    priority: Optional[int] = Field(0, description="Priority (higher wins)")


# Analytics Models

class DifficultyChange(BaseModel):
    """Single difficulty change record"""
    timestamp: str
    operator: str
    previous_difficulty: float
    new_difficulty: float
    reason: str
    session_ref: str


class OperatorAnalytics(BaseModel):
    """Analytics for a specific operator"""
    operator: str
    current_difficulty: float
    difficulty_history: List[DifficultyChange]
    total_attempts: int
    total_correct: int
    success_rate: float


class UserAnalyticsResponse(BaseModel):
    """Detailed user analytics"""
    user_ref: str
    age: Optional[int]
    grade: Optional[Union[str, int]]  # Allow both string and int from DB
    institution_ref: Optional[str]
    total_sessions: int
    total_exercises: int
    overall_accuracy: float
    current_score: int
    operator_analytics: Dict[str, OperatorAnalytics]
    sessions_summary: List[Dict]  # List of session summaries


class CohortStats(BaseModel):
    """Statistics for a cohort"""
    operator: str
    avg_difficulty: float
    min_difficulty: float
    max_difficulty: float
    stddev: Optional[float]
    avg_success_rate: float


class CohortAnalyticsResponse(BaseModel):
    """Analytics for a group of users"""
    cohort_description: str
    user_count: int
    age_group: Optional[str]
    grade: Optional[Union[str, int]]  # Allow both string and int
    institution_ref: Optional[str]
    model_ref: Optional[str]
    difficulty_stats: Dict[str, CohortStats]
    overall_success_rate: float
    avg_session_score: float
    total_sessions: int


class ModelPerformanceResponse(BaseModel):
    """Performance metrics for a model"""
    model_ref: str
    total_users: int
    total_sessions: int
    total_exercises: int
    avg_success_rate: float
    difficulty_distribution: Dict[str, Dict[str, float]]  # operator -> {avg, min, max}
    sessions_over_time: List[Dict]  # Timeline data
