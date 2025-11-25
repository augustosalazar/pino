"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
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


class EnsureUserRequest(BaseModel):
    """Request to ensure user exists in database"""
    user_ref: str = Field(..., description="User's Roble auth ID")
    email: str = Field(..., description="User's email")
    username: Optional[str] = Field(None, description="User's display name")


class StartSessionRequest(BaseModel):
    """Request to start a new session"""
    user_ref: str = Field(..., description="User's Roble auth ID")
    num_exercises: int = Field(10, ge=1, le=50, description="Number of exercises")


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
