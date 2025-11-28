"""
PineServer - Main FastAPI Application
Math exercise generation and tracking API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional
import json
import uuid
from datetime import datetime

from models import (
    StartSessionRequest, StartSessionResponse,
    CompleteSessionRequest, CompleteSessionResponse,
    UserProfile, UserStats, Operator, EnsureUserRequest,
    Institution, UpdateProfileRequest, InstitutionStatsRequest,
    UserAnalyticsResponse, CohortAnalyticsResponse, ModelPerformanceResponse,
    DifficultyChange, OperatorAnalytics, CohortStats
)
from roble_client import roble_client
from container import get_container

app = FastAPI(
    title="PineServer API",
    description="Math exercise generation and adaptive difficulty management",
    version="1.0.0"
)

# CORS middleware for React Native app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def determine_model_for_user(user_ref: str) -> str:
    """
    Determine which model to assign to a user based on model assignments.
    Priority order:
    1. Highest priority assignment that matches user criteria
    2. Falls back to 'basicModel' if no matches
    
    Args:
        user_ref: User's reference ID
        
    Returns:
        model_ref: Model ID to use for this user
    """
    try:
        # Get user data
        users = roble_client.read_table("pine_users", {"user_ref": user_ref})
        if not users:
            print(f"[WARNING] User {user_ref} not found, using basicModel")
            return "basicModel"
        
        user = users[0]
        user_age = user.get("age")
        user_grade = user.get("grade")
        user_institution = user.get("institution_ref")
        
        # Get all model assignments, ordered by priority (desc)
        assignments = roble_client.read_table("pine_model_assignments", {})
        
        if not assignments:
            print("[DEBUG] No model assignments found, using basicModel")
            return "basicModel"
        
        # Sort by priority (highest first)
        assignments.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        # Find first matching assignment
        for assignment in assignments:
            assignment_type = assignment.get("assignment_type")
            
            # Check if assignment matches user
            matches = True
            
            # Check institution filter
            if assignment.get("institution_ref"):
                if assignment["institution_ref"] != user_institution:
                    matches = False
                    continue
            
            # Check grade filter
            if assignment.get("grade"):
                if assignment["grade"] != user_grade:
                    matches = False
                    continue
            
            # Check age range filter
            age_min = assignment.get("age_min")
            age_max = assignment.get("age_max")
            if age_min is not None or age_max is not None:
                if user_age is None:
                    matches = False
                    continue
                if age_min is not None and user_age < age_min:
                    matches = False
                    continue
                if age_max is not None and user_age > age_max:
                    matches = False
                    continue
            
            # If all filters match, use this model
            if matches:
                model_ref = assignment.get("model_ref", "basicModel")
                print(f"[DEBUG] User {user_ref} matched assignment type '{assignment_type}' with model '{model_ref}'")
                return model_ref
        
        # No matches found, use default
        print(f"[DEBUG] No matching assignments for user {user_ref}, using basicModel")
        return "basicModel"
        
    except Exception as e:
        print(f"[ERROR] Failed to determine model for user {user_ref}: {e}")
        # Fallback to basicModel on error
        return "basicModel"


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "PineServer",
        "version": "1.0.0"
    }


@app.get("/api/institutions")
async def get_institutions():
    """
    Get all available institutions from pine_institutions table
    """
    try:
        institutions = roble_client.read_table("pine_institutions", {})
        return institutions
    except Exception as e:
        print(f"[ERROR] Exception in get_institutions: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users/ensure")
async def ensure_user(request: EnsureUserRequest):
    """
    Ensure user exists in pine_users table
    Creates user if doesn't exist, returns existing user if found
    Validates institution_ref for existing users
    """
    try:
        # Check if user exists
        users = roble_client.read_table("pine_users", {"user_ref": request.user_ref})
        
        if users and len(users) > 0:
            # User exists, validate institution if provided
            existing_user = users[0]
            if request.institution_ref:
                stored_institution = existing_user.get("institution_ref")
                if stored_institution and stored_institution != request.institution_ref:
                    raise HTTPException(
                        status_code=400,
                        detail="Institution mismatch. This account is associated with a different institution."
                    )
            
            return {
                "status": "existing",
                "user": existing_user
            }
        
        # User doesn't exist, create it
        user_data = {
            "user_ref": request.user_ref,
            "email": request.email,
            "username": request.username or request.email.split('@')[0],
            "current_score": 0,
            "user_type": 1  # Default: student
        }
        
        # Add institution_ref if provided
        if request.institution_ref:
            user_data["institution_ref"] = request.institution_ref
        
        result = roble_client.insert_records("pine_users", [user_data])
        
        if result.get("inserted") and len(result["inserted"]) > 0:
            return {
                "status": "created",
                "user": result["inserted"][0]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Exception in ensure_user: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/start", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest):
    """
    Start a new exercise session
    
    1. Get user's difficulty profile
    2. Generate personalized exercises
    3. Create session record
    4. Return exercises
    """
    try:
        print(f"[DEBUG] Starting session for user: {request.user_ref}")
        
        # Get user's difficulty profiles
        profiles = roble_client.read_table(
            "pine_user_difficulty_profile",
            {"user_ref": request.user_ref}
        )
        print(f"[DEBUG] Found {len(profiles)} difficulty profiles")
        
        # Build difficulty map
        difficulty_by_operator = {}
        for profile in profiles:
            operator = profile.get('operator')
            diff = profile.get('current_difficulty', 1.0)
            difficulty_by_operator[operator] = float(diff)
        
        # Initialize missing operators with default difficulty
        for op in ['+', '-', '*', '/']:
            if op not in difficulty_by_operator:
                difficulty_by_operator[op] = 1.0
                # Create initial profile
                print(f"[DEBUG] Creating initial profile for operator: {op}")
                roble_client.insert_records("pine_user_difficulty_profile", [{
                    "user_ref": request.user_ref,
                    "operator": op,
                    "current_difficulty": 1.0,
                    "success_rate": 0.0,
                    "total_attempts": 0,
                    "total_correct": 0
                }])
        
        print(f"[DEBUG] Difficulty map: {difficulty_by_operator}")
        
        # Generate exercises using injected batch generator
        container = get_container()
        print(f"[DEBUG] Generating {request.num_exercises} exercises")
        exercises = container.batch_generator.generate_batch(
            difficulty_by_operator,
            request.num_exercises
        )
        print(f"[DEBUG] Generated {len(exercises)} exercises")
        
        # Determine which model to use for this user
        model_ref = determine_model_for_user(request.user_ref)
        print(f"[DEBUG] Using model: {model_ref}")
        
        # Create session record
        session_data = {
            "user_ref": request.user_ref,
            "model_ref": model_ref,  # NOW POPULATED!
            "total_exercises": len(exercises),
            "correct_answers": 0,
            "avg_difficulty": sum(e.difficulty_level for e in exercises) / len(exercises),
            "total_time_ms": 0,
            "score_earned": 0
        }
        
        print(f"[DEBUG] Creating session record")
        result = roble_client.insert_records("pine_exercise_sessions", [session_data])
        print(f"[DEBUG] Insert result: {result}")
        
        if not result.get("inserted"):
            print(f"[ERROR] Failed to create session - no inserted records returned")
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        session_id = result["inserted"][0]["_id"]
        print(f"[DEBUG] Session created with ID: {session_id}")

        # Update with started_at (done separately to avoid potential insert schema issues)
        try:
            roble_client.update_record("pine_exercise_sessions", session_id, {
                "started_at": datetime.utcnow().isoformat()
            })
        except Exception as e:
            print(f"[WARN] Failed to set started_at: {e}")
        
        return StartSessionResponse(
            session_id=session_id,
            exercises=exercises,
            user_profile=difficulty_by_operator
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Exception in start_session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/{session_id}/complete", response_model=CompleteSessionResponse)
async def complete_session(session_id: str, request: CompleteSessionRequest):
    """
    Complete a session and save results
    
    1. Save exercise results
    2. Calculate score
    3. Adjust difficulty
    4. Update user profile
    5. Return summary
    """
    try:
        print(f"[DEBUG] Completing session: {session_id}")
        
        # Get session
        sessions = roble_client.read_table("pine_exercise_sessions", {"_id": session_id})
        if not sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[0]
        user_ref = session.get("user_ref")
        print(f"[DEBUG] Session user_ref: {user_ref}")
        
       # Calculate statistics
        container = get_container()
        total_exercises = len(request.exercises)
        correct_answers = sum(1 for e in request.exercises if e.is_correct)
        total_time = sum(e.time_taken_ms for e in request.exercises)
        score_earned = container.profile_evaluator.calculate_score(request.exercises)
        print(f"[DEBUG] Stats - Total: {total_exercises}, Correct: {correct_answers}, Score: {score_earned}")
        
        # Save individual exercises
        try:
            exercise_records = []
            for exercise in request.exercises:
                exercise_record = {
                    "session_ref": session_id,
                    "user_ref": user_ref,
                    "exercise_type": exercise.exercise_type.value,
                    "operator": exercise.operator.value,
                    "operand_1": exercise.operand_1,
                    "operand_2": exercise.operand_2,
                    "correct_answer": exercise.correct_answer,
                    "user_answer": exercise.user_answer,
                    "options": json.dumps(exercise.options) if exercise.options else None,
                    "difficulty_level": exercise.difficulty_level,
                    "is_correct": exercise.is_correct,
                    "time_taken_ms": exercise.time_taken_ms
                }
                exercise_records.append(exercise_record)
            
            roble_client.insert_records("pine_exercises", exercise_records)
            print(f"[DEBUG] Inserted {len(exercise_records)} exercise records")
        except Exception as e:
            print(f"[ERROR] Failed to insert exercises: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save exercises: {str(e)}")
        
        # Update session
        try:
            roble_client.update_record("pine_exercise_sessions", session_id, {
                "correct_answers": correct_answers,
                "total_time_ms": total_time,
                "score_earned": score_earned,
                "completed_at": datetime.utcnow().isoformat()
            })
            print(f"[DEBUG] Updated session record")
        except Exception as e:
            print(f"[ERROR] Failed to update session: {e}")
            # Continue anyway, not critical
        
        # Get current difficulty profiles
        try:
            profiles = roble_client.read_table(
                "pine_user_difficulty_profile",
                {"user_ref": user_ref}
            )
            print(f"[DEBUG] Found {len(profiles)} difficulty profiles")
            
            current_difficulty = {p['operator']: float(p.get('current_difficulty', 1.0)) for p in profiles}
        except Exception as e:
            print(f"[ERROR] Failed to read profiles: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to read profiles: {str(e)}")
        
        # Calculate difficulty adjustments using injected evaluator
        new_difficulty, adjustments = container.profile_evaluator.evaluate_performance(
            request.exercises,
            current_difficulty
        )
        print(f"[DEBUG] Calculated {len(adjustments)} difficulty adjustments")
        
        # Update difficulty profiles and save adjustments
        difficulty_changes = {}
        for adjustment in adjustments:
            operator = adjustment['operator']
            
            # Find profile _id for this operator
            profile = next((p for p in profiles if p['operator'] == operator), None)
            if profile:
                try:
                    # Update profile
                    roble_client.update_record("pine_user_difficulty_profile", profile['_id'], {
                        "current_difficulty": adjustment['new_difficulty'],
                        "success_rate": adjustment['success_rate'],
                        "total_attempts": profile.get('total_attempts', 0) + adjustment['total'],
                        "total_correct": profile.get('total_correct', 0) + adjustment['correct']
                    })
                    print(f"[DEBUG] Updated difficulty profile for {operator}")
                except Exception as e:
                    print(f"[ERROR] Failed to update profile for {operator}: {e}")
                    # Continue with other operators
                
                try:
                    # Save adjustment record
                    roble_client.insert_records("pine_difficulty_adjustments", [{
                        "user_ref": user_ref,
                        "session_ref": session_id,
                        "operator": operator,
                        "previous_difficulty": adjustment['previous_difficulty'],
                        "new_difficulty": adjustment['new_difficulty'],
                        "reason": adjustment['reason']
                    }])
                    print(f"[DEBUG] Saved adjustment record for {operator}")
                except Exception as e:
                    print(f"[ERROR] Failed to save adjustment for {operator}: {e}")
                
                difficulty_changes[operator] = {
                    "old": adjustment['previous_difficulty'],
                    "new": adjustment['new_difficulty']
                }
        
        # Update user score
        try:
            users = roble_client.read_table("pine_users", {"user_ref": user_ref})
            if users:
                user = users[0]
                new_score = user.get('current_score', 0) + score_earned
                roble_client.update_or_replace("pine_users", user['_id'], {
                    "current_score": new_score
                })
                print(f"[DEBUG] Updated user score to {new_score}")
        except Exception as e:
            print(f"[ERROR] Failed to update user score: {e}")
            # Continue anyway
        
        return CompleteSessionResponse(
            session_id=session_id,
            total_exercises=total_exercises,
            correct_answers=correct_answers,
            score_earned=score_earned,
            difficulty_adjustments=difficulty_changes
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error in complete_session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_ref}/profile", response_model=UserProfile)
async def get_user_profile(user_ref: str):
    """Get user's difficulty profile"""
    try:
        profiles = roble_client.read_table(
            "pine_user_difficulty_profile",
            {"user_ref": user_ref}
        )
        
        profile_data = {}
        for profile in profiles:
            operator = profile.get('operator')
            profile_data[operator] = {
                "current_difficulty": profile.get('current_difficulty'),
                "success_rate": profile.get('success_rate'),
                "total_attempts": profile.get('total_attempts'),
                "total_correct": profile.get('total_correct')
            }
        
        return UserProfile(
            user_id=user_ref,
            profiles=profile_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_ref}/stats", response_model=UserStats)
async def get_user_stats(user_ref: str):
    """Get user statistics"""
    try:
        # Get user data
        users = roble_client.read_table("pine_users", {"user_ref": user_ref})
        if not users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users[0]
        
        # Get sessions
        sessions = roble_client.read_table("pine_exercise_sessions", {"user_ref": user_ref})
        
        # Get all exercises
        exercises = roble_client.read_table("pine_exercises", {"user_ref": user_ref})
        
        # Get difficulty profiles
        profiles = roble_client.read_table("pine_user_difficulty_profile", {"user_ref": user_ref})
        
        # Calculate stats
        total_sessions = len(sessions)
        total_exercises = len(exercises)
        total_correct = sum(1 for e in exercises if e.get('is_correct'))
        accuracy = (total_correct / total_exercises * 100) if total_exercises > 0 else 0
        
        difficulty_by_operator = {
            p.get('operator'): float(p.get('current_difficulty', 1.0))
            for p in profiles
        }
        
        return UserStats(
            user_id=user_ref,
            total_sessions=total_sessions,
            total_exercises=total_exercises,
            total_correct=total_correct,
            accuracy=round(accuracy, 2),
            current_score=user.get('current_score', 0),
            difficulty_by_operator=difficulty_by_operator
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/users/{user_ref}/profile")
async def update_profile(user_ref: str, request: UpdateProfileRequest):
    """Update user profile (age, grade)"""
    try:
        print(f"[DEBUG] Updating profile for user: {user_ref}")
        
        update_data = {}
        if request.age is not None:
            update_data["age"] = request.age
        if request.grade is not None:
            update_data["grade"] = request.grade
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = roble_client.update_or_replace("pine_users", {"user_ref": user_ref}, update_data)
        print(f"[DEBUG] Profile updated successfully")
        
        users = roble_client.read_table("pine_users", {"user_ref": user_ref})
        if users and len(users) > 0:
            return {"status": "success", "user": users[0]}
        else:
            raise HTTPException(status_code=404, detail="User not found after update")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Exception in update_profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/institutions/{institution_ref}/stats")
async def get_institution_stats(institution_ref: str, filters: InstitutionStatsRequest):
    """Get institution statistics with filters (for admin users)"""
    try:
        print(f"[DEBUG] Getting institution stats for: {institution_ref}")
        
        query = {}
        institutions = roble_client.read_table("pine_institutions", {"_id": institution_ref})
        is_uninorte = False
        if institutions and len(institutions) > 0:
            institution_name = institutions[0].get("name", "").lower()
            is_uninorte = "uninorte" in institution_name
        
        if not is_uninorte:
            query["institution_ref"] = institution_ref
        
        all_users = roble_client.read_table("pine_users", query)
        
        filtered_users = []
        for user in all_users:
            if user.get("user_type", 1) != 1:
                continue
            if filters.age_min is not None and (user.get("age") is None or user.get("age") < filters.age_min):
                continue
            if filters.age_max is not None and (user.get("age") is None or user.get("age") > filters.age_max):
                continue
            if filters.grade is not None and user.get("grade") != filters.grade:
                continue
            filtered_users.append(user)
        
        total_students = len(filtered_users)
        total_score = sum(user.get("current_score", 0) for user in filtered_users)
        avg_score = total_score / total_students if total_students > 0 else 0
        
        all_sessions = []
        for user in filtered_users:
            sessions = roble_client.read_table("pine_exercise_sessions", {"user_ref": user["user_ref"]})
            all_sessions.extend(sessions)
        
        total_exercises = sum(s.get("total_exercises", 0) for s in all_sessions)
        total_correct = sum(s.get("correct_answers", 0) for s in all_sessions)
        overall_accuracy = (total_correct / total_exercises * 100) if total_exercises > 0 else 0
        
        unique_grades = list(set(user.get("grade") for user in all_users if user.get("grade") is not None))
        unique_grades.sort()
        
        ages = [user.get("age") for user in all_users if user.get("age") is not None]
        
        return {
            "total_students": total_students,
            "total_score": total_score,
            "average_score": round(avg_score, 2),
            "total_sessions": len(all_sessions),
            "total_exercises": total_exercises,
            "total_correct": total_correct,
            "overall_accuracy": round(overall_accuracy, 2),
            "filter_options": {
                "grades": unique_grades,
                "age_range": {"min": min(ages) if ages else None, "max": max(ages) if ages else None}
            },
            "is_uninorte": is_uninorte
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Exception in get_institution_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/institutions/{institution_ref}/users")
async def get_institution_users(institution_ref: str):
    """
    Get all users for a specific institution.
    Used by admin interface to populate user selector dropdown.
    """
    try:
        print(f"[DEBUG] Getting users for institution: {institution_ref}")
        
        # Get all users for this institution
        users = roble_client.read_table("pine_users", {"institution_ref": institution_ref})
        
        # Return user list with basic info
        user_list = [
            {
                "user_ref": u.get("user_ref"),
                "username": u.get("username"),
                "email": u.get("email"),
                "age": u.get("age"),
                "grade": u.get("grade"),
                "current_score": u.get("current_score", 0)
            }
            for u in users
        ]
        
        print(f"[DEBUG] Found {len(user_list)} users for institution {institution_ref}")
        return user_list
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Exception in get_institution_users: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/analytics/user/{user_ref}", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    user_ref: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Get detailed analytics for a specific user"""
    try:
        users = roble_client.read_table("pine_users", {"user_ref": user_ref})
        if not users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users[0]
        sessions = roble_client.read_table("pine_exercise_sessions", {"user_ref": user_ref})
        exercises = roble_client.read_table("pine_exercises", {"user_ref": user_ref})
        profiles = roble_client.read_table("pine_user_difficulty_profile", {"user_ref": user_ref})
        adjustments = roble_client.read_table("pine_difficulty_adjustments", {"user_ref": user_ref})
        
        total_correct = sum(1 for e in exercises if e.get('is_correct'))
        overall_accuracy = (total_correct / len(exercises) * 100) if exercises else 0
        
        operator_analytics = {}
        for operator in ['+', '-', '*', '/']:
            profile = next((p for p in profiles if p.get('operator') == operator), None)
            op_adjustments = [adj for adj in adjustments if adj.get('operator') == operator]
            
            difficulty_history = [
                DifficultyChange(
                    timestamp=adj.get('created_at', ''),
                    operator=adj.get('operator'),
                    previous_difficulty=float(adj.get('previous_difficulty', 0)),
                    new_difficulty=float(adj.get('new_difficulty', 0)),
                    reason=adj.get('reason', ''),
                    session_ref=adj.get('session_ref', '')
                )
                for adj in sorted(op_adjustments, key=lambda x: x.get('created_at', ''))
            ]
            
            if profile:
                operator_analytics[operator] = OperatorAnalytics(
                    operator=operator,
                    current_difficulty=float(profile.get('current_difficulty', 1.0)),
                    difficulty_history=difficulty_history,
                    total_attempts=profile.get('total_attempts', 0),
                    total_correct=profile.get('total_correct', 0),
                    success_rate=float(profile.get('success_rate', 0))
                )
        
        sessions_summary = [
            {
                "session_id": s.get('_id'),
                "created_at": s.get('created_at', ''),
                "started_at": s.get('started_at'),
                "completed_at": s.get('completed_at'),
                "model_ref": s.get('model_ref', ''),
                "total_exercises": s.get('total_exercises', 0),
                "correct_answers": s.get('correct_answers', 0),
                "score_earned": s.get('score_earned', 0),
                "avg_difficulty": s.get('avg_difficulty', 0),
                "total_time_ms": s.get('total_time_ms', 0)
            }
            for s in sorted(sessions, key=lambda x: x.get('created_at', ''), reverse=True)
        ]
        
        return UserAnalyticsResponse(
            user_ref=user_ref,
            age=user.get('age'),
            grade=user.get('grade'),
            institution_ref=user.get('institution_ref'),
            total_sessions=len(sessions),
            total_exercises=len(exercises),
            overall_accuracy=round(overall_accuracy, 2),
            current_score=user.get('current_score', 0),
            operator_analytics=operator_analytics,
            sessions_summary=sessions_summary
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] get_user_analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/cohort", response_model=CohortAnalyticsResponse)
async def get_cohort_analytics(
    age_group: Optional[str] = None,
    grade: Optional[str] = None,
    institution_ref: Optional[str] = None,
    model_ref: Optional[str] = None
):
    """Get analytics for a cohort of users"""
    try:
        user_filters = {}
        if grade:
            user_filters['grade'] = grade
        if institution_ref:
            user_filters['institution_ref'] = institution_ref
        
        all_users = roble_client.read_table("pine_users", user_filters)
        
        if age_group and '-' in age_group:
            age_min, age_max = map(int, age_group.split('-'))
            all_users = [u for u in all_users if u.get('age') and age_min <= u.get('age') <= age_max]
        
        if not all_users:
            raise HTTPException(status_code=404, detail="No users found")
        
        user_refs = [u['user_ref'] for u in all_users]
        
        all_sessions = []
        all_exercises = []
        all_profiles = []
        
        for user_ref in user_refs:
            sessions = roble_client.read_table("pine_exercise_sessions", {"user_ref": user_ref})
            if model_ref:
                sessions = [s for s in sessions if s.get('model_ref') == model_ref]
            all_sessions.extend(sessions)
            
            all_exercises.extend(roble_client.read_table("pine_exercises", {"user_ref": user_ref}))
            all_profiles.extend(roble_client.read_table("pine_user_difficulty_profile", {"user_ref": user_ref}))
        
        total_correct = sum(1 for e in all_exercises if e.get('is_correct'))
        overall_success_rate = (total_correct / len(all_exercises)) if all_exercises else 0
        avg_session_score = sum(s.get('score_earned', 0) for s in all_sessions) / len(all_sessions) if all_sessions else 0
        
        difficulty_stats = {}
        for operator in ['+', '-', '*', '/']:
            op_profiles = [p for p in all_profiles if p.get('operator') == operator]
            if op_profiles:
                difficulties = [float(p.get('current_difficulty', 1.0)) for p in op_profiles]
                success_rates = [float(p.get('success_rate', 0)) for p in op_profiles]
                
                avg_diff = sum(difficulties) / len(difficulties)
                variance = sum((d - avg_diff) ** 2 for d in difficulties) / len(difficulties)
                
                difficulty_stats[operator] = CohortStats(
                    operator=operator,
                    avg_difficulty=round(avg_diff, 2),
                    min_difficulty=round(min(difficulties), 2),
                    max_difficulty=round(max(difficulties), 2),
                    stddev=round(variance ** 0.5, 2),
                    avg_success_rate=round(sum(success_rates) / len(success_rates) * 100, 2)
                )
        
        desc_parts = [f"Ages {age_group}" if age_group else None,
                      f"Grade {grade}" if grade else None,
                      f"Institution {institution_ref}" if institution_ref else None,
                      f"Model {model_ref}" if model_ref else None]
        cohort_description = ", ".join([p for p in desc_parts if p]) or "All users"
        
        return CohortAnalyticsResponse(
            cohort_description=cohort_description,
            user_count=len(user_refs),
            age_group=age_group,
            grade=grade,
            institution_ref=institution_ref,
            model_ref=model_ref,
            difficulty_stats=difficulty_stats,
            overall_success_rate=round(overall_success_rate * 100, 2),
            avg_session_score=round(avg_session_score, 2),
            total_sessions=len(all_sessions)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] get_cohort_analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/model/{model_ref}", response_model=ModelPerformanceResponse)
async def get_model_performance(model_ref: str):
    """Get performance metrics for a specific model"""
    try:
        # Get ALL sessions first (Roble doesn't support model_ref as filter)
        all_sessions_raw = roble_client.read_table("pine_exercise_sessions", {})
        
        # Filter by model_ref in Python
        all_sessions = [s for s in all_sessions_raw if s.get('model_ref') == model_ref]
        
        if not all_sessions:
            return ModelPerformanceResponse(
                model_ref=model_ref, total_users=0, total_sessions=0,
                total_exercises=0, avg_success_rate=0,
                difficulty_distribution={}, sessions_over_time=[]
            )
        
        user_refs = list(set(s['user_ref'] for s in all_sessions))
        session_ids = [s['_id'] for s in all_sessions]
        
        all_exercises = []
        for session_id in session_ids:
            all_exercises.extend(roble_client.read_table("pine_exercises", {"session_ref": session_id}))
        
        total_correct = sum(1 for e in all_exercises if e.get('is_correct'))
        avg_success_rate = (total_correct / len(all_exercises) * 100) if all_exercises else 0
        
        difficulty_distribution = {}
        for operator in ['+', '-', '*', '/']:
            op_exercises = [e for e in all_exercises if e.get('operator') == operator]
            if op_exercises:
                difficulties = [e.get('difficulty_level', 1.0) for e in op_exercises]
                difficulty_distribution[operator] = {
                    "avg": round(sum(difficulties) / len(difficulties), 2),
                    "min": round(min(difficulties), 2),
                    "max": round(max(difficulties), 2)
                }
        
        sessions_by_date = {}
        for session in all_sessions:
            date = (session.get('created_at', '') or '')[:10]
            if date:
                sessions_by_date[date] = sessions_by_date.get(date, 0) + 1
        
        sessions_over_time = [{"date": d, "count": c} for d, c in sorted(sessions_by_date.items())]
        
        return ModelPerformanceResponse(
            model_ref=model_ref,
            total_users=len(user_refs),
            total_sessions=len(all_sessions),
            total_exercises=len(all_exercises),
            avg_success_rate=round(avg_success_rate, 2),
            difficulty_distribution=difficulty_distribution,
            sessions_over_time=sessions_over_time
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] get_model_performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Migration/Admin endpoint
@app.post("/api/admin/backfill-model-refs")
async def backfill_model_refs():
    """
    Backfill model_ref for existing sessions that don't have it.
    Sets all sessions without model_ref to 'basicModel'
    """
    try:
        # Get all sessions
        all_sessions = roble_client.read_table("pine_exercise_sessions", {})
        
        updated_count = 0
        for session in all_sessions:
            # If session doesn't have model_ref or it's empty
            if not session.get('model_ref'):
                try:
                    roble_client.update_record(
                        "pine_exercise_sessions",
                        session['_id'],
                        {"model_ref": "basicModel"}
                    )
                    updated_count += 1
                except Exception as e:
                    print(f"[WARNING] Failed to update session {session['_id']}: {e}")
        
        return {
            "success": True,
            "message": f"Updated {updated_count} sessions with basicModel",
            "total_sessions": len(all_sessions),
            "updated": updated_count
        }
    except Exception as e:
        print(f"[ERROR] backfill_model_refs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
