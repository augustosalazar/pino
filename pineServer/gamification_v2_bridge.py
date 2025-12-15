"""
Bridge entre FastAPI y Gamificación V2

Este módulo actúa como adaptador para conectar los endpoints existentes de FastAPI
con la nueva lógica de negocio V2. Permite una migración limpia y gradual.
"""

from fastapi import HTTPException
from datetime import datetime
import json
from typing import List, Dict

from models import (
    StartSessionResponse, CompleteSessionResponse, 
    StartSessionRequest, CompleteSessionRequest,
    Exercise
)

from roble_client import roble_client

# V2 Components
from v2.batch_generator import get_batch_generator
from v2.miniboss_detector import get_miniboss_detector
from v2.miniboss_evaluator import get_miniboss_evaluator
from v2.performance_evaluator import get_performance_evaluator
from v2.scoring_calculator import get_scoring_calculator
from v2.dominio_level_manager import get_dominio_level_manager
from v2.batch_recorder import get_batch_recorder
from v2.config_manager import get_config_manager
from v2.models import (
    BatchType, UserOperationState, BatchResult, 
    ExerciseResult, UserGamificationState, Exercise as V2Exercise,
    Operacion, TipoRespuesta
)

# Cache en memoria para metadata de sesiones V2
# session_id -> metadata dict (evita alterar schema SQL existente)
_V2_SESSION_METADATA_CACHE = {}

# === START SESSION HANDLER ===

def _get_pending_exercises(user_ref: str, operacion: str, limit: int = 2) -> List[V2Exercise]:
    """Recupera ejercicios fallidos previamente para repaso"""
    try:
        # 1. Buscar pendientes no completados
        pending = roble_client.read_table("pine_pending_items", {
            "user_ref": user_ref,
            "operacion": operacion,
            "completado": False
        })
        
        if not pending: return []

        print(f"[V2] Found {len(pending)} pending exercises for review")
        
        # Filtrar los que ya se mostraron recientemente?
        # Por ahora tomamos los más antiguos (FIFO) para asegurar que se repasen
        pending.sort(key=lambda x: x.get('fecha_ultimo_fallo', ''))
        selection = pending[:limit]

        print(f"[V2] Selecting {len(selection)} pending exercises to include in batch")
        
        exercises = []
        for p in selection:
            ref = p.get("exercise_ref")
            if not ref: continue

            print(f"[V2] Including pending exercise with ref {ref} in batch")
            
            # Buscar detalle en pine_exercises
            ex_data_list = roble_client.read_table("pine_exercises", {"_id": ref})
            if ex_data_list:
                ex_rec = ex_data_list[0]

                print(f"[V2] Retrieved exercise data: {ex_rec}")
                
                # Mapear tipo respuesta legacy (int) a V2 (str)
                t_resp = TipoRespuesta.MULTIPLE_CHOICE if ex_rec.get("exercise_type") == 1 else TipoRespuesta.ABIERTA
                
                # Parsear opciones
                opciones = None
                if ex_rec.get("options"):
                    if isinstance(ex_rec["options"], str):
                        try:
                            opciones = json.loads(ex_rec["options"])
                        except: pass
                    elif isinstance(ex_rec["options"], list):
                        opciones = ex_rec["options"]
                
                ex_obj = V2Exercise(
                    operand_1=ex_rec["operand_1"],
                    operand_2=ex_rec["operand_2"],
                    operacion=operacion, # Asumimos misma op
                    respuesta_correcta=float(ex_rec["correct_answer"]),
                    dificultad=float(ex_rec["difficulty_level"]),
                    tipo_respuesta=t_resp,
                    opciones=opciones,
                    pending_ref=p.get("_id") # ID del registro pendiente para marcar completado
                )
                exercises.append(ex_obj)
                
        print(f"[V2] Retrieved {len(exercises)} pending exercises for review")
        return exercises
        
    except Exception as e:
        print(f"[V2 WARN] Error fetching pending exercises: {e}")
        return []

async def handle_start_session_v2(request: StartSessionRequest) -> StartSessionResponse:
    """Maneja el inicio de sesión usando lógica V2"""
    try:
        user_ref = request.user_ref
        print(f"[V2] Starting session for {user_ref}")
        
        # 1. Obtener estado actual del usuario (Operaciones desbloqueadas y niveles)
        ops_records = roble_client.read_table("pine_user_operations", {"user_ref": user_ref})
        
        # Si no tiene operaciones, asumir que es nuevo y desbloquear suma nivel 1
        if not ops_records:
            print("[V2] New user, initializing default operations")
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
                "updated_at": datetime.utcnow().isoformat()
            }
            roble_client.insert_records("pine_user_operations", [initial_op])
            ops_records = [initial_op]
            
        operations_state = [UserOperationState.from_db_record(r) for r in ops_records if r.get("unlocked")]
        
        if not operations_state:
            # Fallback if unlocked flag logic fails
             operations_state = [UserOperationState.from_db_record(r) for r in ops_records]
             
        # 2. Elegir operación para este batch
        # Estrategia simple: Round-robin o aleatorio ponderado por menor dominio
        # Por ahora: Aleatorio simple entre las desbloqueadas
        import random
        selected_op_state = random.choice(operations_state)
        operacion = selected_op_state.operacion
        
        print(f"[V2] Selected operation: {operacion} (Level {selected_op_state.nivel_invisible})")
        
        # 3. Determinar tipo de batch (Regular vs Miniboss vs Endless)
        # Por ahora StartSessionRequest no pide endless explícito, asumimos flujo normal
        batch_type = BatchType.REGULAR
        
        detector = get_miniboss_detector()
        is_boss = detector.is_miniboss_candidate(selected_op_state)
        
        if is_boss:
            batch_type = BatchType.MINIBOSS
            print(f"[V2] MINIBOSS TRIGGERED for {operacion}")
        
        # Recuperar ejercicios pendientes para batches regulares
        forced_exercises = []
        if batch_type == BatchType.REGULAR:
            forced_exercises = _get_pending_exercises(user_ref, operacion)
            print(f"[V2] Forcing {len(forced_exercises)} pending exercises into batch")

        # 4. Generar ejercicios
        batch_gen = get_batch_generator()
        v2_exercises = batch_gen.generate_batch(
            user_ref=user_ref,
            operacion=operacion,
            nivel_invisible=selected_op_state.nivel_invisible,
            batch_type=batch_type,
            forced_exercises=forced_exercises
        )
        
        legacy_exercises: List[Exercise] = []
        
        # Mapeo de operador string a Enum legacy
        from models import Operator, ExerciseType
        op_map = {
            "suma": Operator.ADD,
            "resta": Operator.SUBTRACT,
            "mult": Operator.MULTIPLY,
            "div": Operator.DIVIDE
        }
        
        for ex in v2_exercises:
            # Determinar tipo legacy
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
            
        # 6. Crear registro de sesión (pine_exercise_sessions)
        # IMPORTANTE: No guardamos metadata V2 en DB para evitar errores de schema
        session_data = {
            "user_ref": user_ref,
            "model_ref": "v2_adaptive", # Marcador
            "total_exercises": len(legacy_exercises),
            "correct_answers": 0,
            "avg_difficulty": sum(e.dificultad for e in v2_exercises) / len(v2_exercises),
            "total_time_ms": 0,
            "score_earned": 0
        }
        
        print(f"[DEBUG V2] Inserting session data: {session_data}")
        res = roble_client.insert_records("pine_exercise_sessions", [session_data])
        print(f"[DEBUG V2] Insert response: {res}")
        
        if not res or not res.get("inserted"):
            print(f"[ERROR V2] Insert failed. Response: {res}")
            raise HTTPException(status_code=500, detail="Failed to create V2 session")
            
        session_id = res["inserted"][0]["_id"]
        
        # Guardar metadata en cache memoria
        _V2_SESSION_METADATA_CACHE[session_id] = {
            "batch_type": batch_type,
            "operacion": operacion,
            "nivel_central": int(selected_op_state.nivel_invisible),
            "nivel_invisible": selected_op_state.nivel_invisible,
            "is_miniboss": is_boss,
            "exercises": v2_exercises # Guardamos objetos completos para recuperar pending_ref
        }
        print(f"[DEBUG V2] Metadata cached for session {session_id}")
        
        # 7. Construir respuesta
        # User profile mock para compatibilidad
        dummy_profile = {op.value: 1.0 for op in Operator}
        
        # Agregar flag is_miniboss en alguna parte si el frontend lo soporta
        # Como StartSessionResponse es estricto, tal vez lo metemos en user_profile? 
        # Hack: Usar 'miniboss' como key en user_profile
        if is_boss:
             dummy_profile['is_miniboss'] = 1.0
        
        return StartSessionResponse(
            session_id=session_id,
            exercises=legacy_exercises,
            user_profile=dummy_profile
        )
        
    except Exception as e:
        print(f"[V2 ERROR] Start Session: {e}")
        import traceback
        traceback.print_exc()
        raise e


# === COMPLETE SESSION HANDLER ===

async def handle_complete_session_v2(session_id: str, request: CompleteSessionRequest) -> CompleteSessionResponse:
    """Maneja la compleción de sesión usando lógica V2"""
    try:
        print(f"[V2] Completing session {session_id}")
        
        # 1. Recuperar sesión para obtener metadatos V2
        sessions = roble_client.read_table("pine_exercise_sessions", {"_id": session_id})
        if not sessions:
            raise HTTPException(status_code=404, detail="Session not found")
            
        session = sessions[0]
        user_ref = session.get("user_ref")
        
        # Leer metadatos V2 storeados en cache (preferido) o DB
        v2_meta = _V2_SESSION_METADATA_CACHE.get(session_id, {})
        
        # Fallback a DB si cache miss (no debería pasar en dev single-worker)
        if not v2_meta and session.get("v2_metadata"):
            try:
                v2_meta = json.loads(session.get("v2_metadata"))
            except: pass
            
        print(f"[DEBUG V2] Retrieved metadata for session: {v2_meta}")
            
        operacion_str = v2_meta.get("operacion", "suma")
        batch_type_str = v2_meta.get("batch_type", BatchType.REGULAR)
        nivel_invisible_antes = v2_meta.get("nivel_invisible", 1.0)
        
        # Si no hay metadatos, intentar recuperar de UserState (arriesgado porque pudo haber cambiado)
        # O asumir defaults seguros (mejor)
        if not v2_meta:
             print("[WARN V2] Metadata missing for session, assuming basics")
        
        # 2. Convertir resultados legacy a V2 ExerciseResult
        v2_results: List[ExerciseResult] = []
        op_map_rev = {'+': 'suma', '-': 'resta', '*': 'mult', '/': 'div'}
        original_exercises = v2_meta.get("exercises", [])
        
        for i, ex in enumerate(request.exercises):
            # Reconstruir objeto Exercise
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
            
            # Recuperar pending_ref del original cacheado
            if i < len(original_exercises):
                exercise_obj.pending_ref = original_exercises[i].pending_ref
            
            v2_res = ExerciseResult(
                exercise=exercise_obj,
                respuesta_usuario=ex.user_answer if ex.user_answer is not None else 0,
                es_correcto=ex.is_correct,
                tiempo_segundos=ex.time_taken_ms / 1000.0
            )
            v2_results.append(v2_res)
            
            # Si era un pendiente y se resolvió bien, marcar completado
            if v2_res.es_correcto and exercise_obj.pending_ref:
                try:
                    roble_client.update_record("pine_pending_items", exercise_obj.pending_ref, {
                        "completado": True
                    })
                    print(f"[V2] Pending item {exercise_obj.pending_ref} marked completed")
                except Exception as e:
                    print(f"[V2 WARN] Failed marking pending completed: {e}")
            
        # 3. Evaluar y Calcular
        # Performance
        perf_eval = get_performance_evaluator()
        nivel_invisible_nuevo = perf_eval.evaluate_performance(v2_results, nivel_invisible_antes)
        
        # Scoring
        score_calc = get_scoring_calculator()
        score_parts = score_calc.calculate_score_parts(v2_results)
        score_earned = score_parts["total"]
        
        # Miniboss check
        miniboss_aprobado = None
        if batch_type_str == BatchType.MINIBOSS:
            mb_eval = get_miniboss_evaluator()
            miniboss_aprobado = mb_eval.evaluate_miniboss(v2_results)
            
        if batch_type_str == BatchType.MINIBOSS:
            mb_eval = get_miniboss_evaluator()
            miniboss_aprobado = mb_eval.evaluate_miniboss(v2_results)

        # 3.5. Guardar ejercicios individuales en pine_exercises (Legacy Support)
        # Esto permite que los analíticos antiguos sigan funcionando
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
            print(f"[DEBUG V2] Legacy exercises saved: {len(exercise_records_legacy)}")
            
            # Vincular IDs generados con los resultados V2 para usarlos en pending_items
            if res_legacy and "inserted" in res_legacy:
                inserted_ids = [doc["_id"] for doc in res_legacy["inserted"]]
                for i, ex_res in enumerate(v2_results):
                    if i < len(inserted_ids):
                        ex_res.legacy_ref = inserted_ids[i]
                        
        except Exception as e:
            print(f"[V2 WARN] Failed to save legacy exercises (non-critical): {e}")
            
        # 4. Guardar resultados (BatchRecorder)
        recorder = get_batch_recorder()
        
        # Necesitamos estado actual de gamificación para streak
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
            miniboss_aprobado=miniboss_aprobado
        )
        
        success = recorder.record_batch(batch_result, current_gamif)
        
        # 5. Actualizar sesión legacy para mantener consistencia
        roble_client.update_record("pine_exercise_sessions", session_id, {
            "correct_answers": sum(1 for r in v2_results if r.es_correcto),
            "score_earned": score_earned,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        # 6. Responder
        # Ajustes de dificultad dummy para frontend legacy
        diff_adjustments = {
            operacion_str: {
                "old": nivel_invisible_antes,
                "new": nivel_invisible_nuevo
            }
        }
        
        # Gamification result legacy format (si el frontend lo espera)
        gamif_legacy = {
            "puntos_ganados": score_earned,
            "recompensas": {
                "pp_ganados": batch_result.pp_ganados,
                "pd": {"total_pd_global": batch_result.pd_ganados}, # Approx
                "xp_ganada": batch_result.xp_ganada
            },
            "level_up": miniboss_aprobado is True
        }
        
        return CompleteSessionResponse(
            session_id=session_id,
            total_exercises=len(v2_results),
            correct_answers=batch_result.ejercicios_correctos,
            score_earned=score_earned,
            difficulty_adjustments=diff_adjustments,
            gamification=gamif_legacy
        )
        
    except Exception as e:
        print(f"[V2 ERROR] Complete Session: {e}")
        import traceback
        traceback.print_exc()
        raise e
