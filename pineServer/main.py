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
    DifficultyChange, OperatorAnalytics, CohortStats, Exercise, ExerciseType
)
from roble_client import roble_client
from container import get_container

# Import test endpoints for V2
from gamification_v2_test_endpoints import router as v2_test_router
# Import V2 initialization module
from gamification_v2_init import initialize_v2_data

# ==================== GAMIFICATION V2 INTEGRATION ====================
import os
from datetime import datetime
from datetime_utils import now_utc_iso

# V2 Core Components
from v2.config_manager import get_config_manager
from v2.batch_generator import get_batch_generator
from v2.miniboss_detector import get_miniboss_detector
from v2.miniboss_evaluator import get_miniboss_evaluator
from v2.performance_evaluator import get_performance_evaluator
from v2.scoring_calculator import get_scoring_calculator
from v2.dominio_level_manager import get_dominio_level_manager
from v2.batch_recorder import get_batch_recorder
from v2.models import (
    BatchType, UserOperationState, BatchResult, 
    ExerciseResult, UserGamificationState, Exercise as V2Exercise,
    Operacion, TipoRespuesta
)

# V2 is always enabled (legacy flow removed)
USE_GAMIFICATION_V2 = True
print(f"[SYSTEM] Gamification V2 is ENABLED by default")

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

# Register V2 test endpoints (keep available)
app.include_router(v2_test_router)


# Startup event: Initialize V2 data if not present
@app.on_event("startup")
async def startup_event():
    """
    Initialize V2 configuration data on server startup
    """
    initialize_v2_data()



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
    Now also initializes and returns gamification profile
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
            
            # Get or create gamification profile for existing user
            from gamification_profile import obtener_perfil_completo
            perfil_gamificacion = await obtener_perfil_completo(request.user_ref)
            
            return {
                "status": "existing",
                "user": existing_user,
                "gamification": perfil_gamificacion
            }
        
        print(f"[DEBUG] User {request.user_ref} not found, creating new user")
        
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
        else:
            user_data["institution_ref"] = "5TdXBMzeFfju" # Default institution 
        
        result = roble_client.insert_records("pine_users", [user_data])
        
        if result.get("inserted") and len(result["inserted"]) > 0:
            new_user = result["inserted"][0]
            
            # Initialize gamification profile for new user
            from gamification_profile import inicializar_perfil_completo
            perfil_gamificacion = await inicializar_perfil_completo(request.user_ref)
            
            return {
                "status": "created",
                "user": new_user,
                "gamification": perfil_gamificacion
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
    2. Get user's unlocked operations (gamification)
    3. Generate personalized exercises (only for unlocked ops)
    4. Create session record
    5. Return exercises
    """
    try:
        print(f"[DEBUG] Starting session for user: {request.user_ref}")
        
        # ==================== V2 START SESSION (DEFAULT) ====================
        from typing import List
        from v2.models import Exercise as V2Exercise, TipoRespuesta

        # Helper to pull pending items into the batch
        def _get_pending_exercises(user_ref: str, operacion: str, limit: int = 2) -> List[V2Exercise]:
            try:
                pending = roble_client.read_table("pine_pending_items", {
                    "user_ref": user_ref,
                    "operacion": operacion,
                    "completado": False
                })
                if not pending:
                    return []
                pending.sort(key=lambda x: x.get('fecha_ultimo_fallo', ''))
                selection = pending[:limit]

                exercises: List[V2Exercise] = []
                for p in selection:
                    ref = p.get("exercise_ref")
                    if not ref:
                        continue
                    ex_data_list = roble_client.read_table("pine_exercises", {"_id": ref})
                    if ex_data_list:
                        ex_rec = ex_data_list[0]
                        t_resp = TipoRespuesta.MULTIPLE_CHOICE if ex_rec.get("exercise_type") == 1 else TipoRespuesta.ABIERTA
                        opciones = None
                        if ex_rec.get("options"):
                            if isinstance(ex_rec["options"], str):
                                try:
                                    opciones = json.loads(ex_rec["options"])
                                except Exception:
                                    pass
                            elif isinstance(ex_rec["options"], list):
                                opciones = ex_rec["options"]
                        ex_obj = V2Exercise(
                            operand_1=ex_rec["operand_1"],
                            operand_2=ex_rec["operand_2"],
                            operacion=operacion,
                            respuesta_correcta=float(ex_rec["correct_answer"]),
                            dificultad=float(ex_rec["difficulty_level"]),
                            tipo_respuesta=t_resp,
                            opciones=opciones,
                            pending_ref=p.get("_id")
                        )
                        exercises.append(ex_obj)
                return exercises
            except Exception as e:
                print(f"[V2 WARN] Error fetching pending exercises: {e}")
                return []

        # Cache for V2 session metadata (mimic bridge behavior)
        global _V2_SESSION_METADATA_CACHE
        try:
            _ = _V2_SESSION_METADATA_CACHE
        except NameError:
            _V2_SESSION_METADATA_CACHE = {}

        user_ref = request.user_ref
        ops_records = roble_client.read_table("pine_user_operations", {"user_ref": user_ref})
        if not ops_records:
            initial_op = {
                "user_ref": user_ref,
                "operacion": "suma",
                "nivel_dominio": 1,
                "nivel_invisible": 1.0,
                "pd_operacion": 0,
                "unlocked": True,
                "miniboss_completed": False,
                "miniboss_attempts": 0,
                "batches_desde_ultimo_miniboss": 0,
                "miniboss_fallos_consecutivos": 0,
                "total_ejercicios": 0,
                "total_correctos": 0,
                "updated_at": now_utc_iso()
            }
            roble_client.insert_records("pine_user_operations", [initial_op])
            ops_records = [initial_op]

        operations_state = [UserOperationState.from_db_record(r) for r in ops_records if r.get("unlocked")]
        if not operations_state:
            operations_state = [UserOperationState.from_db_record(r) for r in ops_records]

        import random
        selected_op_state = random.choice(operations_state)
        operacion = selected_op_state.operacion

        # Determine batch type: use explicit request type if provided, otherwise auto-detect
        batch_type = BatchType.REGULAR
        is_boss = False
        
        if request.batch_type == "endless":
            batch_type = BatchType.ENDLESS
        elif request.batch_type == "miniboss":
            batch_type = BatchType.MINIBOSS
            is_boss = True
        else:
            # Auto-detect miniboss for regular mode
            detector = get_miniboss_detector()
            is_boss = detector.is_miniboss_candidate(selected_op_state)
            if is_boss:
                batch_type = BatchType.MINIBOSS

        forced_exercises: List[V2Exercise] = []
        if batch_type == BatchType.REGULAR:
            forced_exercises = _get_pending_exercises(user_ref, operacion)

        batch_gen = get_batch_generator()
        v2_exercises = batch_gen.generate_batch(
            user_ref=user_ref,
            operacion=operacion,
            nivel_invisible=selected_op_state.nivel_invisible,
            batch_type=batch_type,
            forced_exercises=forced_exercises,
            num_exercises=request.num_exercises
        )

        legacy_exercises = []
        op_map = {
            "suma": Operator.ADD,
            "resta": Operator.SUBTRACT,
            "mult": Operator.MULTIPLY,
            "div": Operator.DIVIDE
        }
        for ex in v2_exercises:
            ex_type = ExerciseType.MULTIPLE_CHOICE if ex.tipo_respuesta == TipoRespuesta.MULTIPLE_CHOICE else ExerciseType.TEXT_INPUT
            legacy_exercises.append(Exercise(
                exercise_type=ex_type,
                operator=op_map.get(ex.operacion, Operator.ADD),
                operand_1=ex.operand_1,
                operand_2=ex.operand_2,
                correct_answer=ex.respuesta_correcta,
                options=ex.opciones,
                difficulty_level=ex.dificultad
            ))

        session_data = {
            "user_ref": user_ref,
            "model_ref": "v2_adaptive",
            "total_exercises": len(legacy_exercises),
            "correct_answers": 0,
            "avg_difficulty": sum(e.dificultad for e in v2_exercises) / len(v2_exercises),
            "total_time_ms": 0,
            "score_earned": 0
        }
        res = roble_client.insert_records("pine_exercise_sessions", [session_data])
        if not res or not res.get("inserted"):
            raise HTTPException(status_code=500, detail="Failed to create V2 session")
        session_id = res["inserted"][0]["_id"]

        _V2_SESSION_METADATA_CACHE[session_id] = {
            "batch_type": batch_type,
            "operacion": operacion,
            "nivel_central": int(selected_op_state.nivel_invisible),
            "nivel_invisible": selected_op_state.nivel_invisible,
            "is_miniboss": is_boss,
            "exercises": v2_exercises
        }

        dummy_profile = {op.value: 1.0 for op in Operator}
        if is_boss:
            dummy_profile['is_miniboss'] = 1.0

        return StartSessionResponse(
            session_id=session_id,
            exercises=legacy_exercises,
            user_profile=dummy_profile
        )
            
        # ==================== GET UNLOCKED OPERATIONS ====================
        # Get which operations the user has unlocked via gamification
        from gamification_unlocks import obtener_operaciones_disponibles
        
        unlocked_operations_names = await obtener_operaciones_disponibles(request.user_ref)
        print(f"[DEBUG] Unlocked operations: {unlocked_operations_names}")
        
        # Map Spanish names to operator symbols
        op_name_to_symbol = {
            'suma': '+',
            'resta': '-',
            'mult': '*',
            'div': '/'
        }
        
        unlocked_operators = [
            op_name_to_symbol[op_name] 
            for op_name in unlocked_operations_names 
            if op_name in op_name_to_symbol
        ]
        
        # Fallback: if nothing unlocked (shouldn't happen), give them addition
        if not unlocked_operators:
            print("[WARNING] No operations unlocked, defaulting to addition")
            unlocked_operators = ['+']
        
        print(f"[DEBUG] Unlocked operator symbols: {unlocked_operators}")
        
        # ==================== GET GAMIFICATION PD VALUES ====================
        # Get PD (Puntos de Dominio) for each operation from gamification system
        # This will be used to determine the nivel (1-5) for exercise generation
        from gamification_profile import obtener_perfil_completo
        
        perfil_completo = await obtener_perfil_completo(request.user_ref)
        operaciones_gamif = {op['operacion']: op for op in perfil_completo['operaciones']}
        
        # Map operation names to symbols and get their PD
        op_name_to_symbol_map = {
            'suma': '+',
            'resta': '-',
            'mult': '*',
            'div': '/'
        }
        
        # Build PD map for problem generator (using PD as "difficulty")
        # The gamification problem generator will convert PD to nivel (1-5)
        pd_by_operator = {}
        for op_name, op_symbol in op_name_to_symbol_map.items():
            if op_name in operaciones_gamif:
                pd_by_operator[op_symbol] = float(operaciones_gamif[op_name]['pd_operacion'])
            else:
                pd_by_operator[op_symbol] = 0.0  # Not unlocked yet
        
        print(f"[DEBUG] PD by operator: {pd_by_operator}")
        
        # For backward compatibility with old system, also keep difficulty profiles
        # But prioritize PD values for gamification
        profiles = roble_client.read_table(
            "pine_user_difficulty_profile",
            {"user_ref": request.user_ref}
        )
        print(f"[DEBUG] Found {len(profiles)} old difficulty profiles")
        
        # Build old difficulty map as fallback
        difficulty_by_operator = {}
        for profile in profiles:
            operator = profile.get('operator')
            diff = profile.get('current_difficulty', 1.0)
            difficulty_by_operator[operator] = float(diff)
        
        # Initialize missing operators with default
        for op in ['+', '-', '*', '/']:
            if op not in difficulty_by_operator:
                difficulty_by_operator[op] = 1.0
                # Create initial profile for tracking
                print(f"[DEBUG] Creating initial difficulty profile for operator: {op}")
                roble_client.insert_records("pine_user_difficulty_profile", [{
                    "user_ref": request.user_ref,
                    "operator": op,
                    "current_difficulty": 1.0,
                    "success_rate": 0.0,
                    "total_attempts": 0,
                    "total_correct": 0
                }])
        
        print(f"[DEBUG] Old difficulty map (fallback): {difficulty_by_operator}")
        
        # ==================== GET PENDING ITEMS ====================
        # Get pending items for this user (items that need review)
        # Only for UNLOCKED operations
        from gamification_batch import obtener_items_pendientes
        
        all_pending_items = []
        for op_name in unlocked_operations_names:
            pending = await obtener_items_pendientes(request.user_ref, op_name, limite=2)
            all_pending_items.extend(pending)
        
        print(f"[DEBUG] Found {len(all_pending_items)} pending items for review")
        
        # ==================== GENERATE EXERCISES ====================
        # Generate NEW exercises using gamification-aware batch generator
        # Uses PD values to determine nivel (1-5) for each operation
        # ONLY generates for unlocked operations
        container = get_container()
        
        # Reduce the number of new exercises to make room for pending items
        num_new_exercises = max(1, request.num_exercises - len(all_pending_items))
        print(f"[DEBUG] Generating {num_new_exercises} new exercises + {len(all_pending_items)} pending items")
        print(f"[DEBUG] Only using unlocked operations: {unlocked_operators}")
        print(f"[DEBUG] Using PD values for nivel-based generation")
        
        # Use PD values for gamification-aware generation
        # The GamificationProblemGenerator will convert PD to nivel (1-5)
        exercises = container.batch_generator.generate_batch(
            pd_by_operator,  # ← Use PD instead of old difficulty!
            num_new_exercises,
            unlocked_operations=unlocked_operators
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
                "started_at": now_utc_iso()
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
        
        # ==================== V2 COMPLETE SESSION (DEFAULT) ====================
        from typing import List
        from v2.models import Exercise as V2Exercise

        sessions = roble_client.read_table("pine_exercise_sessions", {"_id": session_id})
        if not sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        session = sessions[0]
        user_ref = session.get("user_ref")

        global _V2_SESSION_METADATA_CACHE
        v2_meta = _V2_SESSION_METADATA_CACHE.get(session_id, {})
        if not v2_meta and session.get("v2_metadata"):
            try:
                v2_meta = json.loads(session.get("v2_metadata"))
            except Exception:
                v2_meta = {}

        operacion_str = v2_meta.get("operacion", "suma")
        batch_type_str = v2_meta.get("batch_type", BatchType.REGULAR)
        nivel_invisible_antes = v2_meta.get("nivel_invisible", 1.0)

        v2_results: List[ExerciseResult] = []
        op_map_rev = {'+': 'suma', '-': 'resta', '*': 'mult', '/': 'div'}
        original_exercises: List[V2Exercise] = v2_meta.get("exercises", [])

        for i, ex in enumerate(request.exercises):
            op_v2 = op_map_rev.get(ex.operator.value, 'suma')
            exercise_obj = V2Exercise(
                operand_1=ex.operand_1,
                operand_2=ex.operand_2,
                operacion=op_v2,
                respuesta_correcta=ex.correct_answer,
                dificultad=ex.difficulty_level,
                tipo_respuesta="multiple_choice" if ex.exercise_type.value == "multiple_choice" else "abierta",
                opciones=ex.options
            )
            if i < len(original_exercises):
                exercise_obj.pending_ref = original_exercises[i].pending_ref
            v2_res = ExerciseResult(
                exercise=exercise_obj,
                respuesta_usuario=ex.user_answer if ex.user_answer is not None else 0,
                es_correcto=ex.is_correct,
                tiempo_segundos=ex.time_taken_ms / 1000.0
            )
            v2_results.append(v2_res)
            if v2_res.es_correcto and exercise_obj.pending_ref:
                try:
                    roble_client.update_record("pine_pending_items", exercise_obj.pending_ref, {"completado": True})
                except Exception as e:
                    print(f"[V2 WARN] Failed marking pending completed: {e}")

        perf_eval = get_performance_evaluator()
        nivel_invisible_nuevo = perf_eval.evaluate_performance(v2_results, nivel_invisible_antes)

        score_calc = get_scoring_calculator()
        score_parts = score_calc.calculate_score_parts(v2_results)
        score_earned = score_parts["total"]

        miniboss_aprobado = None
        if batch_type_str == BatchType.MINIBOSS:
            mb_eval = get_miniboss_evaluator()
            miniboss_aprobado = mb_eval.evaluate_miniboss(v2_results)

        # Calculate endless streak for endless mode
        endless_streak = 0
        if batch_type_str == BatchType.ENDLESS:
            for res in v2_results:
                if res.es_correcto:
                    endless_streak += 1
                else:
                    break  # Stop counting on first wrong answer

        try:
            exercise_records_legacy = []
            for ex in request.exercises:
                rec = {
                    "session_ref": session_id,
                    "user_ref": user_ref,
                    "exercise_type": ex.exercise_type.value,
                    "operator": ex.operator.value,
                    "operand_1": ex.operand_1,
                    "operand_2": ex.operand_2,
                    "correct_answer": ex.correct_answer,
                    "user_answer": ex.user_answer,
                    "options": json.dumps(ex.options) if ex.options else None,
                    "difficulty_level": ex.difficulty_level,
                    "is_correct": ex.is_correct,
                    "time_taken_ms": ex.time_taken_ms
                }
                exercise_records_legacy.append(rec)
            res_legacy = roble_client.insert_records("pine_exercises", exercise_records_legacy)
            if res_legacy and "inserted" in res_legacy:
                inserted_ids = [doc["_id"] for doc in res_legacy["inserted"]]
                for i, ex_res in enumerate(v2_results):
                    if i < len(inserted_ids):
                        ex_res.legacy_ref = inserted_ids[i]
        except Exception as e:
            print(f"[V2 WARN] Failed to save legacy exercises (non-critical): {e}")

        recorder = get_batch_recorder()
        gamif_recs = roble_client.read_table("pine_user_gamification", {"user_ref": user_ref})
        current_gamif = UserGamificationState.from_db_record(gamif_recs[0]) if gamif_recs else UserGamificationState(user_ref)
        batch_result = BatchResult(
            user_ref=user_ref,
            operacion=operacion_str,
            batch_type=batch_type_str,
            ejercicios=v2_results,
            nivel_central=v2_meta.get("nivel_central", 1),
            nivel_invisible_antes=nivel_invisible_antes,
            nivel_invisible_despues=nivel_invisible_nuevo,
            score_ganado=score_earned,
            pp_ganados=score_calc.calculate_pp(v2_results),
            pd_ganados=score_calc.calculate_pd(v2_results),
            xp_ganada=score_calc.calculate_xp(v2_results),
            duracion_segundos=int(sum(r.tiempo_segundos for r in v2_results)),
            miniboss_aprobado=miniboss_aprobado,
            endless_streak=endless_streak if batch_type_str == BatchType.ENDLESS else None
        )
        recorder.record_batch(batch_result, current_gamif)

        roble_client.update_record("pine_exercise_sessions", session_id, {
            "correct_answers": sum(1 for r in v2_results if r.es_correcto),
            "score_earned": score_earned,
            "completed_at": now_utc_iso()
        })

        diff_adjustments = {
            operacion_str: {
                "old": nivel_invisible_antes,
                "new": nivel_invisible_nuevo
            }
        }
        gamif_legacy = {
            "puntos_ganados": score_earned,
            "recompensas": {
                "pp_ganados": batch_result.pp_ganados,
                "pd": {"total_pd_global": batch_result.pd_ganados},
                "xp_ganada": batch_result.xp_ganada
            },
            "level_up": miniboss_aprobado is True
        }
        
        # For endless mode, get the best streak from the leaderboard
        endless_info = None
        if batch_type_str == BatchType.ENDLESS:
            from datetime import datetime
            current_month = datetime.utcnow().strftime("%Y-%m")
            endless_records = roble_client.read_table("pine_leaderboard_endless_mensual", {
                "user_ref": user_ref,
                "mes_id": current_month
            })
            best_streak = 0
            if endless_records:
                best_streak = endless_records[0].get("mejor_streak", 0)
            endless_info = {
                "streak": endless_streak,
                "best_streak": best_streak
            }
        
        return CompleteSessionResponse(
            session_id=session_id,
            total_exercises=len(v2_results),
            correct_answers=batch_result.ejercicios_correctos,
            score_earned=score_earned,
            difficulty_adjustments=diff_adjustments,
            gamification=gamif_legacy,
            endless_info=endless_info
        )
        
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
                "completed_at": now_utc_iso()
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
        
        # ==================== GAMIFICATION PROCESSING ====================
        # Process gamification rewards for this batch
        gamification_result = None
        try:
            from gamification_batch import procesar_batch_completo
            
            # Build results for gamification processor
            # Map operators to Spanish names
            op_map = {'+': 'suma', '-': 'resta', '*': 'mult', '/': 'div'}
            
            resultados_items = []
            for ex in request.exercises:
                # Determine if fue_primer_intento (first attempt)
                # For now, assume all are first attempt since we don't track retries yet
                # TODO: Add retry tracking in the future
                fue_primer_intento = True  # Simplified for now
                
                item_result = {
                    'exercise_id': f"{session_id}_{ex.operand_1}_{ex.operator.value}_{ex.operand_2}",
                    'fue_primer_intento': fue_primer_intento,
                    'es_correcto_final': ex.is_correct,
                    'operacion': op_map.get(ex.operator.value, 'suma'),
                    'dificultad': ex.difficulty_level
                }
                resultados_items.append(item_result)
            
            # Determine main operation for this batch
            # Use the most common operator
            operators_count = {}
            for ex in request.exercises:
                op_name = op_map.get(ex.operator.value, 'suma')
                operators_count[op_name] = operators_count.get(op_name, 0) + 1
            
            operacion_principal = max(operators_count, key=operators_count.get) if operators_count else 'suma'
            
            # Calculate average difficulty
            dificultad_media = sum(e.difficulty_level for e in request.exercises) / len(request.exercises) if request.exercises else 1.0
            
            print(f"[DEBUG] Processing gamification for {len(resultados_items)} items, operation: {operacion_principal}")
            
            gamification_result = await procesar_batch_completo(
                user_ref=user_ref,
                resultados_items=resultados_items,
                operacion_principal=operacion_principal,
                dificultad_media=dificultad_media
            )
            
            print(f"[DEBUG] Gamification processing complete: PP={gamification_result['recompensas']['pp_ganados']}, PD={gamification_result['recompensas']['pd']['total_pd_global']}, XP={gamification_result['recompensas']['xp_ganada']}")
            
        except Exception as e:
            print(f"[ERROR] Gamification processing failed (non-critical): {e}")
            import traceback
            traceback.print_exc()
            # Don't fail the entire request, gamification is supplementary
        
        # ==================== BUILD RESPONSE ====================
        
        response_data = {
            "session_id": session_id,
            "total_exercises": total_exercises,
            "correct_answers": correct_answers,
            "score_earned": score_earned,
            "difficulty_adjustments": difficulty_changes
        }
        
        # Add gamification data if available
        if gamification_result:
            response_data["gamification"] = gamification_result
        
        return CompleteSessionResponse(**response_data)
    
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
        
        # Don't return stats for admin users (they don't play the game)
        if user.get('user_type') == 2:
            raise HTTPException(
                status_code=403, 
                detail="Statistics not available for admin users"
            )
        
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


# ==================== GAMIFICATION ENDPOINTS ====================

@app.get("/api/users/{user_ref}/gamification")
async def get_gamification_profile(user_ref: str):
    """
    Get complete gamification profile for a user
    
    Returns:
    - Perfil de gamificación (PP, PD, XP, niveles, rachas)
    - Operaciones y niveles de dominio
    - Desbloqueos de operaciones y modos
    - Progreso hacia próximos desbloqueos
    """
    try:
        print(f"[DEBUG] Getting gamification profile for user: {user_ref}")
        
        from gamification_profile import obtener_perfil_completo
        from gamification_unlocks import (
            obtener_modos_disponibles,
            obtener_operaciones_disponibles,
            obtener_progreso_desbloqueos
        )
        
        # Get complete gamification profile
        perfil_completo = await obtener_perfil_completo(user_ref)
        
        # Get available modes
        modos_disponibles = await obtener_modos_disponibles(user_ref)
        
        # Get available operations
        operaciones_disponibles = await obtener_operaciones_disponibles(user_ref)
        
        # Get unlock progress
        progreso_desbloqueos = await obtener_progreso_desbloqueos(user_ref)
        
        return {
            "perfil": perfil_completo['perfil'],
            "operaciones": perfil_completo['operaciones'],
            "modos_disponibles": modos_disponibles,
            "operaciones_disponibles": operaciones_disponibles,
            "progreso_desbloqueos": progreso_desbloqueos
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Exception in get_gamification_profile: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MINI-JEFE ENDPOINTS ====================

@app.get("/api/minibosses")
async def get_minibosses_info():
    """
    Get information about all available minibosses
    """
    try:
        from gamification_miniboss import obtener_todos_minijefes
        
        minibosses = obtener_todos_minijefes()
        return {"minibosses": minibosses}
        
    except Exception as e:
        print(f"[ERROR] Exception in get_minibosses_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users/{user_ref}/miniboss/{operacion}/start")
async def start_miniboss(user_ref: str, operacion: str):
    """
    Start a miniboss challenge
    
    Args:
        user_ref: User reference
        operacion: Miniboss type ('suma', 'mult', 'div')
    
    Returns:
        Miniboss session with exercises
    """
    try:
        print(f"[DEBUG] Starting miniboss {operacion} for user: {user_ref}")
        
        from gamification_miniboss import (
            generar_batch_minijefe,
            obtener_info_minijefe,
            puede_acceder_minijefe
        )
        from gamification_profile import obtener_perfil_completo
        from gamification_unlocks import registrar_intento_minijefe
        
        # Get user profile to check access
        perfil = await obtener_perfil_completo(user_ref)
        
        # Check if user can access this miniboss
        puede_acceder, razon = puede_acceder_minijefe(operacion, perfil)
        if not puede_acceder:
            raise HTTPException(status_code=403, detail=razon)
        
        # Generate miniboss batch
        exercises = generar_batch_minijefe(operacion)
        
        # Get miniboss info
        miniboss_info = obtener_info_minijefe(operacion)
        
        # Register attempt
        await registrar_intento_minijefe(user_ref, operacion)
        
        # Create a special session for miniboss
        session_data = {
            "user_ref": user_ref,
            "model_ref": "miniboss",
            "total_exercises": len(exercises),
            "correct_answers": 0,
            "avg_difficulty": sum(e.difficulty_level for e in exercises) / len(exercises),
            "total_time_ms": 0,
            "score_earned": 0,
            # Miniboss-specific fields
            "session_type": "miniboss",
            "miniboss_exito": False
        }
        
        result = roble_client.insert_records("pine_exercise_sessions", [session_data])
        
        if not result.get("inserted"):
            raise HTTPException(status_code=500, detail="Failed to create miniboss session")
        
        session_id = result["inserted"][0]["_id"]
        
        # Update with started_at
        try:
            roble_client.update_record("pine_exercise_sessions", session_id, {
                "started_at": now_utc_iso()
            })
        except Exception as e:
            print(f"[WARN] Failed to set started_at: {e}")
        
        return {
            "session_id": session_id,
            "miniboss_info": miniboss_info,
            "exercises": exercises,
            "operacion": operacion
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Exception in start_miniboss: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users/{user_ref}/miniboss/{operacion}/complete")
async def complete_miniboss(user_ref: str, operacion: str, request: CompleteSessionRequest):
    """
    Complete a miniboss challenge
    
    Args:
        user_ref: User reference
        operacion: Miniboss type
        request: Session completion data
    
    Returns:
        Miniboss completion result with unlock status
    """
    try:
        print(f"[DEBUG] Completing miniboss {operacion} for user: {user_ref}")
        
        from gamification_miniboss import validar_completitud_minijefe
        from gamification_unlocks import marcar_minijefe_completado, verificar_y_desbloquear_operaciones
        
        # Calculate results
        total_exercises = len(request.exercises)
        correctos = sum(1 for e in request.exercises if e.is_correct)
        total_time_ms = sum(e.time_taken_ms for e in request.exercises)
        total_time_segundos = total_time_ms / 1000.0
        
        # Prepare results for validation
        ejercicios_resultados = [
            {
                'is_correct': e.is_correct,
                'fue_primer_intento': True  # TODO: Track retries properly
            }
            for e in request.exercises
        ]
        
        # Validate miniboss completion
        exito, detalles = validar_completitud_minijefe(
            operacion,
            ejercicios_resultados,
            total_time_segundos
        )
        
        print(f"[DEBUG] Miniboss result: {exito}, details: {detalles}")
        
        # If successful, mark as completed and try to unlock
        desbloqueo_info = None
        if exito:
            # Mark miniboss as completed
            await marcar_minijefe_completado(user_ref, operacion)
            
            # Try to unlock operations
            desbloqueos = await verificar_y_desbloquear_operaciones(user_ref)
            
            if any(desbloqueos.values()):
                desbloqueo_info = {
                    "hubo_desbloqueo": True,
                    "operaciones_desbloqueadas": [op for op, desbloq in desbloqueos.items() if desbloq]
                }
                print(f"[DEBUG] Unlocked operations: {desbloqueo_info['operaciones_desbloqueadas']}")
            else:
                desbloqueo_info = {"hubo_desbloqueo": False}
        
        # Update session (if we have session_id from somewhere)
        # For now, we'll skip session update since we don't have session_id in the path
        
        # Save individual exercises (similar to complete_session)
        # We'll extract session_id from the first exercise if stored, or skip for now
        
        return {
            "operacion": operacion,
            "exito": exito,
            "detalles": detalles,
            "desbloqueo": desbloqueo_info,
            "total_exercises": total_exercises,
            "correct_answers": correctos,
            "tiempo_total_segundos": round(total_time_segundos, 1)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Exception in complete_miniboss: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LEADERBOARD ENDPOINT ====================

@app.get("/api/leaderboard/weekly")
async def get_weekly_leaderboard(
    institution_ref: str = None,
    limit: int = 100
):
    """
    Get weekly leaderboard based on gamification scores
    
    Score = 0.4 × PP_week + 0.6 × PD_week
    
    Args:
        institution_ref: Optional filter by institution
        limit: Max number of users (default 100)
    
    Returns:
        Ranked list of users with scores
    """
    try:
        print(f"[DEBUG] Getting weekly leaderboard, institution: {institution_ref}, limit: {limit}")
        
        from gamification_core import calcular_score_semanal
        
        # Get all gamification profiles
        query = {}
        profiles = roble_client.read_table("pine_user_gamification", query)
        
        print(f"[DEBUG] Found {len(profiles)} gamification profiles")
        
        # If institution filter, get users from that institution
        user_refs_in_institution = None
        if institution_ref:
            users = roble_client.read_table("pine_users", {"institution_ref": institution_ref})
            user_refs_in_institution = set(u['user_ref'] for u in users)
            print(f"[DEBUG] Filtering by institution: {len(user_refs_in_institution)} users")
        
        # Calculate scores and build leaderboard
        leaderboard_entries = []
        
        for profile in profiles:
            user_ref = profile.get('user_ref')
            
            # Skip if not in institution filter
            if user_refs_in_institution and user_ref not in user_refs_in_institution:
                continue
            
            # Calculate weekly score
            pp_semana = profile.get('pp_semana', 0)
            pd_semana = profile.get('pd_semana', 0)
            score_semanal = calcular_score_semanal(pp_semana, pd_semana)
            
            # Get user info
            users = roble_client.read_table("pine_users", {"user_ref": user_ref})
            if not users:
                continue
            
            user = users[0]
            
            entry = {
                "user_ref": user_ref,
                "username": user.get('username', 'Unknown'),
                "email": user.get('email', ''),
                "pp_semana": pp_semana,
                "pd_semana": pd_semana,
                "score_semanal": round(score_semanal, 2),
                "nivel_jugador": profile.get('nivel_jugador', 1),
                "racha_dias": profile.get('racha_dias', 0),
                "institution_ref": user.get('institution_ref')
            }
            
            leaderboard_entries.append(entry)
        
        # Sort by score (descending)
        leaderboard_entries.sort(key=lambda x: x['score_semanal'], reverse=True)
        
        # Add rank
        for i, entry in enumerate(leaderboard_entries[:limit], start=1):
            entry['rank'] = i
        
        # Limit results
        top_users = leaderboard_entries[:limit]
        
        print(f"[DEBUG] Returning {len(top_users)} users in leaderboard")
        
        return {
            "leaderboard": top_users,
            "total_users": len(leaderboard_entries),
            "top_count": len(top_users),
            "institution_ref": institution_ref
        }
        
    except Exception as e:
        print(f"[ERROR] Exception in get_weekly_leaderboard: {e}")
        import traceback
        traceback.print_exc()
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
            user_type = user.get("user_type")
            
            # Only include students (user_type must be explicitly 1)
            # If user_type is None or missing, skip (don't assume student)
            if user_type != 1:
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
    Get all student users for a specific institution.
    Used by admin interface to populate user selector dropdown.
    Only returns students (user_type=1), not admins.
    """
    try:
        print(f"[DEBUG] Getting users for institution: {institution_ref}")
        
        # Get all users for this institution
        users = roble_client.read_table("pine_users", {"institution_ref": institution_ref})
        
        # Filter to only include students (user_type = 1), exclude admins
        student_users = [u for u in users if u.get("user_type", 1) == 1]
        
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
            for u in student_users
        ]
        
        print(f"[DEBUG] Found {len(user_list)} student users (excluding admins) for institution {institution_ref}")
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
                # Roble only has started_at and completed_at (no created_at field)
                "created_at": s.get('started_at') or s.get('completed_at', ''),
                "started_at": s.get('started_at', ''),
                "completed_at": s.get('completed_at', ''),
                "model_ref": s.get('model_ref', ''),
                "total_exercises": s.get('total_exercises', 0),
                "correct_answers": s.get('correct_answers', 0),
                "score_earned": s.get('score_earned', 0),
                "avg_difficulty": s.get('avg_difficulty', 0),
                "total_time_ms": s.get('total_time_ms', 0)
            }
            for s in sorted(sessions, key=lambda x: x.get('started_at', ''), reverse=True)
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
            # Use started_at since Roble doesn't have created_at
            date = (session.get('started_at', '') or '')[:10]
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
