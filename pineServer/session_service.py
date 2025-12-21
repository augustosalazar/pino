"""
SessionService - Orchestrates exercise session lifecycle

Main entry point for session logic. Uses the container for all dependencies.
"""

import json
import random
from typing import List, Dict, Optional, Any
from datetime import datetime

from gamification_models import (
    Exercise, ExerciseResult, BatchResult, BatchType,
    UserOperationState, UserGamificationState, TipoRespuesta
)
from roble_client import roble_client
from datetime_utils import now_utc_iso


class SessionService:
    """
    Manages the complete session lifecycle.
    
    Usage:
        service = get_session_service()
        result = service.start_session(user_ref="123")
        completion = service.complete_session(session_id, results)
    """
    
    def __init__(self, container=None):
        self._container = container
        self._session_cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_container(self):
        if self._container:
            return self._container
        from container import get_container
        return get_container()
    
    @property
    def batch_generator(self):
        return self._get_container().batch_generator
    
    @property
    def performance_evaluator(self):
        return self._get_container().performance_evaluator
    
    @property
    def scoring_calculator(self):
        return self._get_container().scoring_calculator
    
    @property
    def miniboss_detector(self):
        return self._get_container().miniboss_detector
    
    @property
    def miniboss_evaluator(self):
        return self._get_container().miniboss_evaluator
    
    @property
    def batch_recorder(self):
        return self._get_container().batch_recorder
    
    def start_session(
        self,
        user_ref: str,
        num_exercises: int = 10,
        batch_type_override: Optional[str] = None,
        operacion_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a new exercise session."""
        print(f"[SessionService] Starting session for: {user_ref}")
        
        # Get or init user operations
        ops = roble_client.read_table("pine_user_operations", {"user_ref": user_ref})
        if not ops:
            ops = [self._init_user_operations(user_ref)]
        
        # Select operation
        states = [UserOperationState.from_db_record(r) for r in ops if r.get("unlocked")]
        if not states:
            states = [UserOperationState.from_db_record(r) for r in ops]
        
        if operacion_override:
            selected = next((s for s in states if s.operacion == operacion_override), states[0])
        else:
            selected = random.choice(states)
        
        # Determine batch type
        batch_type = self._determine_batch_type(batch_type_override, selected)
        is_boss = batch_type == BatchType.MINIBOSS
        
        # Get pending exercises for regular batches
        forced = []
        if batch_type == BatchType.REGULAR:
            forced = self._get_pending_exercises(user_ref, selected.operacion)
        
        # Generate batch
        exercises = self.batch_generator.generate_batch(
            user_ref=user_ref,
            operacion=selected.operacion,
            nivel_invisible=selected.nivel_invisible,
            batch_type=batch_type,
            forced_exercises=forced,
            num_exercises=num_exercises
        )
        
        # Create session
        session_id = self._create_session(user_ref, exercises)
        
        # Cache metadata
        self._session_cache[session_id] = {
            "batch_type": batch_type,
            "operacion": selected.operacion,
            "nivel_central": int(selected.nivel_invisible),
            "nivel_invisible": selected.nivel_invisible,
            "is_miniboss": is_boss,
            "exercises": exercises
        }
        
        return {
            "session_id": session_id,
            "exercises": exercises,
            "is_miniboss": is_boss,
            "operacion": selected.operacion,
            "batch_type": batch_type
        }
    
    def complete_session(
        self,
        session_id: str,
        exercise_results: List[ExerciseResult]
    ) -> Dict[str, Any]:
        """Complete a session and process results."""
        print(f"[SessionService] Completing session: {session_id}")
        
        # Get session
        sessions = roble_client.read_table("pine_exercise_sessions", {"_id": session_id})
        if not sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = sessions[0]
        user_ref = session.get("user_ref")
        
        # Get metadata
        meta = self._session_cache.get(session_id, {})
        if not meta and session.get("v2_metadata"):
            try: meta = json.loads(session.get("v2_metadata"))
            except: meta = {}
        
        operacion = meta.get("operacion", "suma")
        batch_type = meta.get("batch_type", BatchType.REGULAR)
        nivel_antes = meta.get("nivel_invisible", 1.0)
        original = meta.get("exercises", [])
        
        # Enrich with pending refs
        for i, r in enumerate(exercise_results):
            if i < len(original):
                r.exercise.pending_ref = original[i].pending_ref
        
        # Mark completed pending
        self._process_completed_pending(exercise_results)
        
        # Evaluate
        nivel_nuevo = self.performance_evaluator.evaluate_performance(exercise_results, nivel_antes)
        score_parts = self.scoring_calculator.calculate_score_parts(exercise_results)
        score = score_parts["total"]
        
        # Miniboss
        mb_passed = None
        if batch_type == BatchType.MINIBOSS:
            mb_passed = self.miniboss_evaluator.evaluate_miniboss(exercise_results)
        
        # Endless streak
        endless = self._calc_endless_streak(exercise_results, batch_type)
        
        # Save legacy exercises
        self._save_legacy_exercises(session_id, user_ref, exercise_results)
        
        # Build and record batch
        gamif = roble_client.read_table("pine_user_gamification", {"user_ref": user_ref})
        current_gamif = UserGamificationState.from_db_record(gamif[0]) if gamif else UserGamificationState(user_ref)
        
        batch_result = BatchResult(
            user_ref=user_ref,
            operacion=operacion,
            batch_type=batch_type,
            ejercicios=exercise_results,
            nivel_central=meta.get("nivel_central", 1),
            nivel_invisible_antes=nivel_antes,
            nivel_invisible_despues=nivel_nuevo,
            score_ganado=score,
            pp_ganados=self.scoring_calculator.calculate_pp(exercise_results),
            pd_ganados=self.scoring_calculator.calculate_pd(exercise_results),
            xp_ganada=self.scoring_calculator.calculate_xp(exercise_results),
            duracion_segundos=int(sum(r.tiempo_segundos for r in exercise_results)),
            miniboss_aprobado=mb_passed,
            endless_streak=endless if batch_type == BatchType.ENDLESS else None,
            session_ref=session_id
        )
        
        self.batch_recorder.record_batch(batch_result, current_gamif)
        
        # Update session
        roble_client.update_record("pine_exercise_sessions", session_id, {
            "correct_answers": sum(1 for r in exercise_results if r.es_correcto),
            "score_earned": score,
            "completed_at": now_utc_iso()
        })
        
        # Clean cache
        self._session_cache.pop(session_id, None)
        
        return {
            "session_id": session_id,
            "total_exercises": len(exercise_results),
            "correct_answers": batch_result.ejercicios_correctos,
            "score_earned": score,
            "difficulty_adjustments": {operacion: {"old": nivel_antes, "new": nivel_nuevo}},
            "gamification": {
                "puntos_ganados": score,
                "recompensas": {
                    "pp_ganados": batch_result.pp_ganados,
                    "pd": {"total_pd_global": batch_result.pd_ganados},
                    "xp_ganada": batch_result.xp_ganada
                },
                "level_up": mb_passed is True
            },
            "endless_info": self._get_endless_info(user_ref, endless, batch_type)
        }
    
    def _init_user_operations(self, user_ref: str) -> Dict:
        initial = {
            "user_ref": user_ref, "operacion": "suma", "nivel_dominio": 1,
            "nivel_invisible": 1.0, "pd_operacion": 0, "unlocked": True,
            "miniboss_completed": False, "miniboss_attempts": 0,
            "batches_desde_ultimo_miniboss": 0, "miniboss_fallos_consecutivos": 0,
            "total_ejercicios": 0, "total_correctos": 0, "updated_at": now_utc_iso()
        }
        roble_client.insert_records("pine_user_operations", [initial])
        return initial
    
    def _determine_batch_type(self, override: Optional[str], state: UserOperationState) -> str:
        if override == "endless": return BatchType.ENDLESS
        if override == "miniboss": return BatchType.MINIBOSS
        if override is None or override == "regular":
            if self.miniboss_detector.is_miniboss_candidate(state):
                return BatchType.MINIBOSS
        return BatchType.REGULAR
    
    def _get_pending_exercises(self, user_ref: str, operacion: str, limit: int = 2) -> List[Exercise]:
        try:
            pending = roble_client.read_table("pine_pending_items", {
                "user_ref": user_ref, "operacion": operacion, "completado": False
            })
            if not pending: return []
            
            pending.sort(key=lambda x: x.get('fecha_ultimo_fallo', ''))
            exercises = []
            for p in pending[:limit]:
                ref = p.get("exercise_ref")
                if not ref: continue
                ex_list = roble_client.read_table("pine_exercises", {"_id": ref})
                if ex_list:
                    ex = ex_list[0]
                    t = TipoRespuesta.MULTIPLE_CHOICE if ex.get("exercise_type") == 1 else TipoRespuesta.ABIERTA
                    opts = None
                    if ex.get("options"):
                        opts = json.loads(ex["options"]) if isinstance(ex["options"], str) else ex["options"]
                    exercises.append(Exercise(
                        operand_1=ex["operand_1"], operand_2=ex["operand_2"],
                        operacion=operacion, respuesta_correcta=float(ex["correct_answer"]),
                        dificultad=float(ex["difficulty_level"]), tipo_respuesta=t,
                        opciones=opts, pending_ref=p.get("_id")
                    ))
            return exercises
        except Exception as e:
            print(f"[SessionService] Pending error: {e}")
            return []
    
    def _create_session(self, user_ref: str, exercises: List[Exercise]) -> str:
        data = {
            "user_ref": user_ref, "model_ref": "v2_adaptive",
            "total_exercises": len(exercises), "correct_answers": 0,
            "avg_difficulty": sum(e.dificultad for e in exercises) / len(exercises) if exercises else 1.0,
            "total_time_ms": 0, "score_earned": 0
        }
        res = roble_client.insert_records("pine_exercise_sessions", [data])
        if not res or not res.get("inserted"):
            raise RuntimeError("Failed to create session")
        return res["inserted"][0]["_id"]
    
    def _process_completed_pending(self, results: List[ExerciseResult]):
        for r in results:
            if r.es_correcto and r.exercise.pending_ref:
                try: roble_client.update_record("pine_pending_items", r.exercise.pending_ref, {"completado": True})
                except: pass
    
    def _calc_endless_streak(self, results: List[ExerciseResult], batch_type: str) -> int:
        if batch_type != BatchType.ENDLESS: return 0
        streak = 0
        for r in results:
            if r.es_correcto: streak += 1
            else: break
        return streak
    
    def _save_legacy_exercises(self, session_id: str, user_ref: str, results: List[ExerciseResult]):
        try:
            records = [{
                "session_ref": session_id, "user_ref": user_ref,
                "exercise_type": "multiple_choice" if r.exercise.tipo_respuesta == TipoRespuesta.MULTIPLE_CHOICE else "text_input",
                "operator": {"suma": "+", "resta": "-", "mult": "*", "div": "/"}.get(r.exercise.operacion, "+"),
                "operand_1": r.exercise.operand_1, "operand_2": r.exercise.operand_2,
                "correct_answer": r.exercise.respuesta_correcta, "user_answer": r.respuesta_usuario,
                "options": json.dumps(r.exercise.opciones) if r.exercise.opciones else None,
                "difficulty_level": r.exercise.dificultad, "is_correct": r.es_correcto,
                "time_taken_ms": int(r.tiempo_segundos * 1000)
            } for r in results]
            
            res = roble_client.insert_records("pine_exercises", records)
            if res and "inserted" in res:
                for i, r in enumerate(results):
                    if i < len(res["inserted"]):
                        r.legacy_ref = res["inserted"][i]["_id"]
        except Exception as e:
            print(f"[SessionService] Legacy save error: {e}")
    
    def _get_endless_info(self, user_ref: str, streak: int, batch_type: str) -> Optional[Dict]:
        if batch_type != BatchType.ENDLESS: return None
        month = datetime.utcnow().strftime("%Y-%m")
        records = roble_client.read_table("pine_leaderboard_endless_mensual", {"user_ref": user_ref, "mes_id": month})
        best = records[0].get("mejor_streak", 0) if records else 0
        return {"streak": streak, "best_streak": best}


# Singleton accessor
_instance = None

def get_session_service() -> SessionService:
    global _instance
    if _instance is None:
        _instance = SessionService()
    return _instance

def set_session_service(service: SessionService):
    global _instance
    _instance = service
