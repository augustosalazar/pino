"""
PineServer - Main FastAPI Application
Math exercise generation and tracking API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import json
import uuid
from datetime import datetime

from models import (
    StartSessionRequest, StartSessionResponse,
    CompleteSessionRequest, CompleteSessionResponse,
    UserProfile, UserStats, Operator, EnsureUserRequest,
    Institution, UpdateProfileRequest, InstitutionStatsRequest
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
        
        # Create session record
        session_data = {
            "user_ref": request.user_ref,
            "total_exercises": len(exercises),
            "correct_answers": 0,
            "avg_difficulty": sum(e.difficulty_level for e in exercises) / len(exercises),
            "total_time_ms": 0,
            "score_earned": 0
        }
        
        print(f"[DEBUG] Creating session record")
        result = roble_client.insert_records("pine_exercise_sessions", [session_data])
        
        if not result.get("inserted"):
            print(f"[ERROR] Failed to create session - no inserted records returned")
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        session_id = result["inserted"][0]["_id"]
        print(f"[DEBUG] Session created with ID: {session_id}")
        
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
                "score_earned": score_earned
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
