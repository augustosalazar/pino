

@app.put("/api/users/{user_ref}/profile")
async def update_profile(user_ref: str, request: UpdateProfileRequest):
    """
    Update user profile (age, grade)
    """
    try:
        print(f"[DEBUG] Updating profile for user: {user_ref}")
        
        # Build update data
        update_data = {}
        if request.age is not None:
            update_data["age"] = request.age
        if request.grade is not None:
            update_data["grade"] = request.grade
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update user record
        result = roble_client.update_or_replace(
            "pine_users",
            {"user_ref": user_ref},
            update_data
        )
        
        print(f"[DEBUG] Profile updated successfully")
        
        # Get updated user
        users = roble_client.read_table("pine_users", {"user_ref": user_ref})
        if users and len(users) > 0:
            return {
                "status": "success",
                "user": users[0]
            }
        else:
            raise HTTPException(status_code=404, detail="User not found after update")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Exception in update_profile: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/institutions/{institution_ref}/stats")
async def get_institution_stats(institution_ref: str, filters: InstitutionStatsRequest):
    """
    Get aggregated statistics for an institution with filters
    Only accessible to admin users (user_type = 2)
    """
    try:
        print(f"[DEBUG] Getting institution stats for: {institution_ref}")
        
        # Build query filters
        query = {}
        
        # Check if institution is "Uninorte" - show all users
        institutions = roble_client.read_table("pine_institutions", {"_id": institution_ref})
        is_uninorte = False
        if institutions and len(institutions) > 0:
            institution_name = institutions[0].get("name", "").lower()
            is_uninorte = "uninorte" in institution_name
        
        if is_uninorte:
            # Show all users regardless of institution
            print("[DEBUG] Uninorte institution - showing all users")
        else:
            # Filter by institution
            query["institution_ref"] = institution_ref
        
        # Get all users matching base query
        all_users = roble_client.read_table("pine_users", query)
        
        # Apply age filters
        filtered_users = []
        for user in all_users:
            # Skip if not a student (only show students in stats)
            if user.get("user_type", 1) != 1:
                continue
                
            # Age filter
            if filters.age_min is not None:
                if user.get("age") is None or user.get("age") < filters.age_min:
                    continue
            if filters.age_max is not None:
                if user.get("age") is None or user.get("age") > filters.age_max:
                    continue
            
            # Grade filter
            if filters.grade is not None:
                if user.get("grade") != filters.grade:
                    continue
            
            filtered_users.append(user)
        
        print(f"[DEBUG] Found {len(filtered_users)} students matching filters")
        
        # Calculate aggregate statistics
        total_students = len(filtered_users)
        total_score = sum(user.get("current_score", 0) for user in filtered_users)
        avg_score = total_score / total_students if total_students > 0 else 0
        
        # Get session stats
        all_sessions = []
        for user in filtered_users:
            sessions = roble_client.read_table("pine_exercise_sessions", {"user_ref": user["user_ref"]})
            all_sessions.extend(sessions)
        
        total_sessions = len(all_sessions)
        completed_sessions = len([s for s in all_sessions if s.get("completed", False)])
        
        # Calculate total exercises and accuracy
        total_exercises = sum(s.get("total_exercises", 0) for s in all_sessions)
        total_correct = sum(s.get("correct_answers", 0) for s in all_sessions)
        overall_accuracy = (total_correct / total_exercises * 100) if total_exercises > 0 else 0
        
        # Get unique grades for filter options
        unique_grades = list(set(user.get("grade") for user in all_users if user.get("grade") is not None))
        unique_grades.sort()
        
        # Get age range for filter options
        ages = [user.get("age") for user in all_users if user.get("age") is not None]
        age_range = {
            "min": min(ages) if ages else None,
            "max": max(ages) if ages else None
        }
        
        return {
            "total_students": total_students,
            "total_score": total_score,
            "average_score": round(avg_score, 2),
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "total_exercises": total_exercises,
            "total_correct": total_correct,
            "overall_accuracy": round(overall_accuracy, 2),
            "filter_options": {
                "grades": unique_grades,
                "age_range": age_range
            },
            "is_uninorte": is_uninorte
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Exception in get_institution_stats: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
