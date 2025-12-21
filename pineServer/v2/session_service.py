"""
SessionService - Orchestrates exercise session lifecycle

This is the main entry point for session logic, encapsulating
all the V2 gamification flow in a clean, testable service.
"""

import json
import random
from typing import List, Dict, Optional, Any
from datetime import datetime

from v2.interfaces import (
    IBatchGenerator, IPerformanceEvaluator, IScoringCalculator,
    IMinibossDetector, IMinibossEvaluator, IBatchRecorder
)
from v2.models import (
    Exercise, ExerciseResult, BatchResult, BatchType,
    UserOperationState, UserGamificationState, TipoRespuesta
)
from roble_client import roble_client
from datetime_utils import now_utc_iso


class SessionService:
    """
    Service that manages the complete session lifecycle.
    
    Responsibilities:
    - Starting sessions (generating exercises)
    - Completing sessions (evaluating results, updating state)
    - Managing session metadata cache
    
    All dependencies are injected via the container.
    """
    
    def __init__(self, container=None):
        """
        Initialize with optional container for dependency injection.
        
        Args:
            container: V2Container instance, or None to use global
        """
        self._container = container
        self._session_cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_container(self):
        """Get the container (injected or global)."""
        if self._container:
            return self._container
        from v2.container import get_v2_container
        return get_v2_container()
    
    @property
    def batch_generator(self) -> IBatchGenerator:
        return self._get_container().batch_generator
    
    @property
    def performance_evaluator(self) -> IPerformanceEvaluator:
        return self._get_container().performance_evaluator
    
    @property
    def scoring_calculator(self) -> IScoringCalculator:
        return self._get_container().scoring_calculator
    
    @property
    def miniboss_detector(self) -> IMinibossDetector:
        return self._get_container().miniboss_detector
    
    @property
    def miniboss_evaluator(self) -> IMinibossEvaluator:
        return self._get_container().miniboss_evaluator
    
    @property
    def batch_recorder(self) -> IBatchRecorder:
        return self._get_container().batch_recorder
    
    def start_session(
        self,
        user_ref: str,
        num_exercises: int = 10,
        batch_type_override: Optional[str] = None,
        operacion_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a new exercise session.
        
        Args:
            user_ref: User identifier
            num_exercises: Number of exercises to generate
            batch_type_override: Force a specific batch type ('regular', 'miniboss', 'endless')
            operacion_override: Force a specific operation
            
        Returns:
            Dict with session_id, exercises, metadata
        """
        print(f"[SessionService] Starting session for user: {user_ref}")
        
        # 1. Get or initialize user operations
        ops_records = roble_client.read_table("pine_user_operations", {"user_ref": user_ref})
        if not ops_records:
            ops_records = [self._initialize_user_operations(user_ref)]
        
        # 2. Select operation (unlocked ones or override)
        operations_state = [
            UserOperationState.from_db_record(r) 
            for r in ops_records 
            if r.get("unlocked")
        ]
        if not operations_state:
            operations_state = [UserOperationState.from_db_record(r) for r in ops_records]
        
        if operacion_override:
            selected_op_state = next(
                (op for op in operations_state if op.operacion == operacion_override),
                operations_state[0]
            )
        else:
            selected_op_state = random.choice(operations_state)
        
        operacion = selected_op_state.operacion
        
        # 3. Determine batch type
        batch_type = self._determine_batch_type(
            batch_type_override, 
            selected_op_state
        )
        is_boss = batch_type == BatchType.MINIBOSS
        
        # 4. Get pending exercises for regular batches
        forced_exercises: List[Exercise] = []
        if batch_type == BatchType.REGULAR:
            forced_exercises = self._get_pending_exercises(user_ref, operacion)
        
        # 5. Generate batch
        exercises = self.batch_generator.generate_batch(
            user_ref=user_ref,
            operacion=operacion,
            nivel_invisible=selected_op_state.nivel_invisible,
            batch_type=batch_type,
            forced_exercises=forced_exercises,
            num_exercises=num_exercises
        )
        
        # 6. Create session record
        session_id = self._create_session_record(user_ref, exercises)
        
        # 7. Cache session metadata
        self._session_cache[session_id] = {
            "batch_type": batch_type,
            "operacion": operacion,
            "nivel_central": int(selected_op_state.nivel_invisible),
            "nivel_invisible": selected_op_state.nivel_invisible,
            "is_miniboss": is_boss,
            "exercises": exercises
        }
        
        return {
            "session_id": session_id,
            "exercises": exercises,
            "is_miniboss": is_boss,
            "operacion": operacion,
            "batch_type": batch_type
        }
    
    def complete_session(
        self,
        session_id: str,
        exercise_results: List[ExerciseResult]
    ) -> Dict[str, Any]:
        """
        Complete a session and process results.
        
        Args:
            session_id: The session ID to complete
            exercise_results: List of exercise results from the client
            
        Returns:
            Dict with score, difficulty changes, gamification rewards, etc.
        """
        print(f"[SessionService] Completing session: {session_id}")
        
        # 1. Get session and metadata
        sessions = roble_client.read_table("pine_exercise_sessions", {"_id": session_id})
        if not sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = sessions[0]
        user_ref = session.get("user_ref")
        
        # Get cached metadata or try to recover from DB
        v2_meta = self._session_cache.get(session_id, {})
        if not v2_meta and session.get("v2_metadata"):
            try:
                v2_meta = json.loads(session.get("v2_metadata"))
            except Exception:
                v2_meta = {}
        
        operacion = v2_meta.get("operacion", "suma")
        batch_type = v2_meta.get("batch_type", BatchType.REGULAR)
        nivel_invisible_antes = v2_meta.get("nivel_invisible", 1.0)
        original_exercises = v2_meta.get("exercises", [])
        
        # 2. Enrich results with pending refs
        for i, result in enumerate(exercise_results):
            if i < len(original_exercises):
                result.exercise.pending_ref = original_exercises[i].pending_ref
        
        # 3. Mark completed pending items
        self._process_completed_pending_items(exercise_results)
        
        # 4. Evaluate performance
        nivel_invisible_nuevo = self.performance_evaluator.evaluate_performance(
            exercise_results, 
            nivel_invisible_antes
        )
        
        # 5. Calculate scores
        score_parts = self.scoring_calculator.calculate_score_parts(exercise_results)
        score_earned = score_parts["total"]
        
        # 6. Evaluate miniboss if applicable
        miniboss_aprobado = None
        if batch_type == BatchType.MINIBOSS:
            miniboss_aprobado = self.miniboss_evaluator.evaluate_miniboss(exercise_results)
        
        # 7. Calculate endless streak
        endless_streak = self._calculate_endless_streak(exercise_results, batch_type)
        
        # 8. Save legacy exercise records and get IDs
        self._save_legacy_exercises(session_id, user_ref, exercise_results)
        
        # 9. Build and record batch result
        gamif_recs = roble_client.read_table("pine_user_gamification", {"user_ref": user_ref})
        current_gamif = (
            UserGamificationState.from_db_record(gamif_recs[0]) 
            if gamif_recs 
            else UserGamificationState(user_ref)
        )
        
        batch_result = BatchResult(
            user_ref=user_ref,
            operacion=operacion,
            batch_type=batch_type,
            ejercicios=exercise_results,
            nivel_central=v2_meta.get("nivel_central", 1),
            nivel_invisible_antes=nivel_invisible_antes,
            nivel_invisible_despues=nivel_invisible_nuevo,
            score_ganado=score_earned,
            pp_ganados=self.scoring_calculator.calculate_pp(exercise_results),
            pd_ganados=self.scoring_calculator.calculate_pd(exercise_results),
            xp_ganada=self.scoring_calculator.calculate_xp(exercise_results),
            duracion_segundos=int(sum(r.tiempo_segundos for r in exercise_results)),
            miniboss_aprobado=miniboss_aprobado,
            endless_streak=endless_streak if batch_type == BatchType.ENDLESS else None,
            session_ref=session_id
        )
        
        self.batch_recorder.record_batch(batch_result, current_gamif)
        
        # 10. Update session record
        roble_client.update_record("pine_exercise_sessions", session_id, {
            "correct_answers": sum(1 for r in exercise_results if r.es_correcto),
            "score_earned": score_earned,
            "completed_at": now_utc_iso()
        })
        
        # 11. Clean up cache
        if session_id in self._session_cache:
            del self._session_cache[session_id]
        
        # 12. Build response
        return {
            "session_id": session_id,
            "total_exercises": len(exercise_results),
            "correct_answers": batch_result.ejercicios_correctos,
            "score_earned": score_earned,
            "difficulty_adjustments": {
                operacion: {
                    "old": nivel_invisible_antes,
                    "new": nivel_invisible_nuevo
                }
            },
            "gamification": {
                "puntos_ganados": score_earned,
                "recompensas": {
                    "pp_ganados": batch_result.pp_ganados,
                    "pd": {"total_pd_global": batch_result.pd_ganados},
                    "xp_ganada": batch_result.xp_ganada
                },
                "level_up": miniboss_aprobado is True
            },
            "endless_info": self._get_endless_info(user_ref, endless_streak, batch_type)
        }
    
    def _initialize_user_operations(self, user_ref: str) -> Dict[str, Any]:
        """Initialize default operation state for new user."""
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
        return initial_op
    
    def _determine_batch_type(
        self, 
        override: Optional[str], 
        op_state: UserOperationState
    ) -> str:
        """Determine the batch type based on override or auto-detection."""
        if override == "endless":
            return BatchType.ENDLESS
        elif override == "miniboss":
            return BatchType.MINIBOSS
        elif override is None or override == "regular":
            # Auto-detect miniboss
            if self.miniboss_detector.is_miniboss_candidate(op_state):
                return BatchType.MINIBOSS
        return BatchType.REGULAR
    
    def _get_pending_exercises(self, user_ref: str, operacion: str, limit: int = 2) -> List[Exercise]:
        """Get pending review exercises for the user."""
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

            exercises: List[Exercise] = []
            for p in selection:
                ref = p.get("exercise_ref")
                if not ref:
                    continue
                    
                ex_data_list = roble_client.read_table("pine_exercises", {"_id": ref})
                if ex_data_list:
                    ex_rec = ex_data_list[0]
                    t_resp = (
                        TipoRespuesta.MULTIPLE_CHOICE 
                        if ex_rec.get("exercise_type") == 1 
                        else TipoRespuesta.ABIERTA
                    )
                    opciones = None
                    if ex_rec.get("options"):
                        if isinstance(ex_rec["options"], str):
                            try:
                                opciones = json.loads(ex_rec["options"])
                            except Exception:
                                pass
                        elif isinstance(ex_rec["options"], list):
                            opciones = ex_rec["options"]
                    
                    ex_obj = Exercise(
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
            print(f"[SessionService] Error fetching pending exercises: {e}")
            return []
    
    def _create_session_record(self, user_ref: str, exercises: List[Exercise]) -> str:
        """Create a session record in the database."""
        session_data = {
            "user_ref": user_ref,
            "model_ref": "v2_adaptive",
            "total_exercises": len(exercises),
            "correct_answers": 0,
            "avg_difficulty": sum(e.dificultad for e in exercises) / len(exercises) if exercises else 1.0,
            "total_time_ms": 0,
            "score_earned": 0
        }
        
        res = roble_client.insert_records("pine_exercise_sessions", [session_data])
        if not res or not res.get("inserted"):
            raise RuntimeError("Failed to create session")
        
        return res["inserted"][0]["_id"]
    
    def _process_completed_pending_items(self, results: List[ExerciseResult]):
        """Mark pending items as completed if answered correctly."""
        for result in results:
            if result.es_correcto and result.exercise.pending_ref:
                try:
                    roble_client.update_record(
                        "pine_pending_items", 
                        result.exercise.pending_ref, 
                        {"completado": True}
                    )
                except Exception as e:
                    print(f"[SessionService] Failed marking pending completed: {e}")
    
    def _calculate_endless_streak(
        self, 
        results: List[ExerciseResult], 
        batch_type: str
    ) -> int:
        """Calculate endless streak (consecutive correct answers from start)."""
        if batch_type != BatchType.ENDLESS:
            return 0
        
        streak = 0
        for res in results:
            if res.es_correcto:
                streak += 1
            else:
                break
        return streak
    
    def _save_legacy_exercises(
        self, 
        session_id: str, 
        user_ref: str, 
        results: List[ExerciseResult]
    ):
        """Save exercises to legacy pine_exercises table and update result refs."""
        try:
            records = []
            for result in results:
                rec = {
                    "session_ref": session_id,
                    "user_ref": user_ref,
                    "exercise_type": (
                        "multiple_choice" 
                        if result.exercise.tipo_respuesta == TipoRespuesta.MULTIPLE_CHOICE 
                        else "text_input"
                    ),
                    "operator": self._operacion_to_operator(result.exercise.operacion),
                    "operand_1": result.exercise.operand_1,
                    "operand_2": result.exercise.operand_2,
                    "correct_answer": result.exercise.respuesta_correcta,
                    "user_answer": result.respuesta_usuario,
                    "options": json.dumps(result.exercise.opciones) if result.exercise.opciones else None,
                    "difficulty_level": result.exercise.dificultad,
                    "is_correct": result.es_correcto,
                    "time_taken_ms": int(result.tiempo_segundos * 1000)
                }
                records.append(rec)
            
            res = roble_client.insert_records("pine_exercises", records)
            if res and "inserted" in res:
                inserted_ids = [doc["_id"] for doc in res["inserted"]]
                for i, result in enumerate(results):
                    if i < len(inserted_ids):
                        result.legacy_ref = inserted_ids[i]
                        
        except Exception as e:
            print(f"[SessionService] Failed to save legacy exercises: {e}")
    
    def _operacion_to_operator(self, operacion: str) -> str:
        """Convert operation name to operator symbol."""
        mapping = {"suma": "+", "resta": "-", "mult": "*", "div": "/"}
        return mapping.get(operacion, "+")
    
    def _get_endless_info(
        self, 
        user_ref: str, 
        endless_streak: int, 
        batch_type: str
    ) -> Optional[Dict[str, int]]:
        """Get endless info including best streak for response."""
        if batch_type != BatchType.ENDLESS:
            return None
        
        current_month = datetime.utcnow().strftime("%Y-%m")
        endless_records = roble_client.read_table("pine_leaderboard_endless_mensual", {
            "user_ref": user_ref,
            "mes_id": current_month
        })
        
        best_streak = 0
        if endless_records:
            best_streak = endless_records[0].get("mejor_streak", 0)
        
        return {
            "streak": endless_streak,
            "best_streak": best_streak
        }


# Singleton accessor
_session_service: Optional[SessionService] = None


def get_session_service() -> SessionService:
    """Get the global session service instance."""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service


def set_session_service(service: SessionService):
    """Set a custom session service (for testing)."""
    global _session_service
    _session_service = service
