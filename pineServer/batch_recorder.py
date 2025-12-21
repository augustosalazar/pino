"""
BatchRecorder - Records batch results and updates user state

Implements IBatchRecorder interface.
Handles all persistence operations.
"""

import json
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any, List

from interfaces import IBatchRecorder
from gamification_models import BatchResult, ExerciseResult, UserGamificationState, UserOperationState, BatchType
from roble_client import roble_client
from datetime_utils import now_colombia, now_utc_iso


class BatchRecorder(IBatchRecorder):
    """
    Records batch results to database and updates user state.
    """
    
    def __init__(self, container=None):
        self._container = container
    
    @property
    def config_manager(self):
        if self._container:
            return self._container.config_manager
        from config_manager import get_config_manager
        return get_config_manager()
    
    def record_batch(self, result: BatchResult, current_gamif_state: UserGamificationState) -> bool:
        """Record batch results and update all related state."""
        try:
            self._insert_batch_log(result)
            self._update_user_operation(result)
            self._update_user_gamification(result, current_gamif_state)
            self._update_weekly_leaderboard(result)
            
            if result.batch_type == BatchType.ENDLESS:
                self._update_endless_monthly_leaderboard(result)
            if result.batch_type == BatchType.MINIBOSS:
                self._log_miniboss_attempt(result)
            
            self._save_pending_items(result)
            return True
            
        except Exception as e:
            print(f"[BatchRecorder] Error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _insert_batch_log(self, result: BatchResult) -> Optional[str]:
        record = result.to_dict()
        if "ejercicios_data" in record:
            record["ejercicios_data"] = json.dumps(record["ejercicios_data"])
        record["session_ref"] = result.session_ref
        res = roble_client.insert_records("pine_batches_completados", [record])
        return res["inserted"][0].get("_id") if res and res.get("inserted") else "temp_id"

    def _update_user_operation(self, result: BatchResult):
        reset_mb = result.batch_type == BatchType.MINIBOSS
        level_up = reset_mb and result.miniboss_aprobado
        
        current_ops = roble_client.read_table("pine_user_operations", {
            "user_ref": result.user_ref, "operacion": result.operacion
        })
        
        op_state = UserOperationState.from_db_record(current_ops[0]) if current_ops else UserOperationState(result.user_ref, result.operacion)
        
        op_state.nivel_invisible = result.nivel_invisible_despues
        if level_up: op_state.nivel_dominio = min(5, op_state.nivel_dominio + 1)
        
        op_state.pd_operacion += result.pd_ganados
        op_state.total_ejercicios += result.total_ejercicios
        op_state.total_correctos += result.ejercicios_correctos
        
        if reset_mb:
            op_state.batches_desde_ultimo_miniboss = 0
            if result.miniboss_aprobado:
                op_state.miniboss_fallos_consecutivos = 0
                op_state.miniboss_completed = True
            else:
                op_state.miniboss_fallos_consecutivos += 1
        else:
            op_state.batches_desde_ultimo_miniboss += 1
        
        record_id = current_ops[0].get("_id") if current_ops else None
        update_data = {
            "nivel_invisible": op_state.nivel_invisible,
            "nivel_dominio": op_state.nivel_dominio,
            "pd_operacion": op_state.pd_operacion,
            "batches_desde_ultimo_miniboss": op_state.batches_desde_ultimo_miniboss,
            "miniboss_fallos_consecutivos": op_state.miniboss_fallos_consecutivos,
            "total_ejercicios": op_state.total_ejercicios,
            "total_correctos": op_state.total_correctos,
            "miniboss_completed": op_state.miniboss_completed,
            "updated_at": now_utc_iso()
        }
        
        if record_id:
            roble_client.update_record("pine_user_operations", record_id, update_data)
        else:
            update_data["user_ref"] = op_state.user_ref
            update_data["operacion"] = op_state.operacion
            roble_client.insert_records("pine_user_operations", [update_data])

    def _update_user_gamification(self, result: BatchResult, current: UserGamificationState):
        streak_config = self.config_manager.get_streak_config()
        min_correct = streak_config.get("min_correct", 4)
        
        today = now_colombia().date().isoformat()
        new_streak = current.racha_dias
        streak_updated = False
        
        if result.ejercicios_correctos >= min_correct:
            if current.racha_ultima_fecha != today:
                yesterday = (now_colombia().date() - timedelta(days=1)).isoformat()
                new_streak = current.racha_dias + 1 if current.racha_ultima_fecha == yesterday else 1
                streak_updated = True
            new_streak = min(new_streak, streak_config.get("max_days", 30))
        
        updates = {
            "pp_total": current.pp_total + result.pp_ganados,
            "pd_global": current.pd_global + result.pd_ganados,
            "xp_total": current.xp_total + result.xp_ganada,
            "racha_dias": new_streak,
            "racha_maxima": max(current.racha_maxima, new_streak),
            "updated_at": now_utc_iso()
        }
        if streak_updated:
            updates["racha_ultima_fecha"] = today
            updates["dias_validos_streak"] = current.dias_validos_streak + 1
        
        gamif = roble_client.read_table("pine_user_gamification", {"user_ref": result.user_ref})
        if gamif:
            roble_client.update_record("pine_user_gamification", gamif[0]["_id"], updates)
        else:
            updates["user_ref"] = result.user_ref
            roble_client.insert_records("pine_user_gamification", [updates])

    def _log_miniboss_attempt(self, result: BatchResult):
        pct = round(result.ejercicios_correctos / result.total_ejercicios, 2) if result.total_ejercicios else 0
        roble_client.insert_records("pine_mini_jefes_intentos", [{
            "user_ref": result.user_ref,
            "mini_jefe": result.operacion,
            "exito": result.miniboss_aprobado,
            "items_correctos": result.ejercicios_correctos,
            "total_items": result.total_ejercicios,
            "porcentaje_acierto": pct,
            "tiempo_total_segundos": result.duracion_segundos or 0,
            "fecha": now_utc_iso()
        }])

    def _save_pending_items(self, result: BatchResult):
        failed = [ex for ex in result.ejercicios if not ex.es_correcto and ex.legacy_ref]
        if not failed or len(failed) > 8: return
        
        timestamp = now_utc_iso()
        records = [{
            "user_ref": result.user_ref,
            "exercise_ref": f.legacy_ref,
            "operacion": f.exercise.operacion,
            "dificultad": f.exercise.dificultad,
            "intentos_fallidos": 1,
            "fecha_primer_fallo": timestamp,
            "fecha_ultimo_fallo": timestamp,
            "mostrado_nuevamente": False,
            "completado": False,
            "session_ref": result.session_ref,
        } for f in failed]
        
        try:
            roble_client.insert_records("pine_pending_items", records)
        except Exception as e:
            print(f"[BatchRecorder] Failed to save pending: {e}")

    def _get_week_dates(self, ref: date = None):
        if ref is None: ref = now_colombia().date()
        monday = ref - timedelta(days=ref.weekday())
        return datetime.combine(monday, datetime.min.time()), datetime.combine(monday + timedelta(days=6), datetime.max.time())

    def _update_weekly_leaderboard(self, result: BatchResult):
        try:
            start, end = self._get_week_dates()
            week_id = f"{start.date().isocalendar()[0]}-W{start.date().isocalendar()[1]:02d}"
            
            existing = roble_client.read_table("pine_weekly_leaderboard", {"user_ref": result.user_ref, "semana_id": week_id})
            
            if existing:
                rec = existing[0]
                roble_client.update_record("pine_weekly_leaderboard", rec["_id"], {
                    "pp_semana": rec.get("pp_semana", 0) + result.pp_ganados,
                    "pd_semana": rec.get("pd_semana", 0) + result.pd_ganados,
                    "score_semanal": round(rec.get("score_semanal", 0) + result.score_ganado, 2)
                })
            else:
                roble_client.insert_records("pine_weekly_leaderboard", [{
                    "user_ref": result.user_ref,
                    "semana_id": week_id,
                    "pp_semana": result.pp_ganados,
                    "pd_semana": result.pd_ganados,
                    "score_semanal": result.score_ganado,
                    "ranking": 0,
                    "fecha_inicio": start.isoformat(),
                    "fecha_fin": end.isoformat(),
                    "created_at": now_utc_iso()
                }])
        except Exception as e:
            print(f"[BatchRecorder] Weekly leaderboard error: {e}")

    def _update_endless_monthly_leaderboard(self, result: BatchResult):
        if result.endless_streak is None: return
        try:
            today = now_colombia().date()
            month_start = today.replace(day=1)
            month_id = month_start.strftime("%Y-%m")
            
            existing = roble_client.read_table("pine_leaderboard_endless_mensual", {"user_ref": result.user_ref, "mes_id": month_id})
            
            if existing:
                rec = existing[0]
                updates = {"total_intentos": rec.get("total_intentos", 0) + 1, "updated_at": now_utc_iso()}
                if result.endless_streak > rec.get("mejor_streak", 0):
                    updates["mejor_streak"] = result.endless_streak
                roble_client.update_record("pine_leaderboard_endless_mensual", rec["_id"], updates)
            else:
                if today.month == 12:
                    month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
                    
                roble_client.insert_records("pine_leaderboard_endless_mensual", [{
                    "user_ref": result.user_ref,
                    "mes_id": month_id,
                    "mejor_streak": result.endless_streak,
                    "total_intentos": 1,
                    "ranking": 0,
                    "fecha_inicio": month_start.isoformat(),
                    "fecha_fin": month_end.isoformat(),
                    "created_at": now_utc_iso(),
                    "updated_at": now_utc_iso()
                }])
        except Exception as e:
            print(f"[BatchRecorder] Endless leaderboard error: {e}")


# Singleton accessor (backward compatibility)
_instance = None

def get_batch_recorder():
    global _instance
    if _instance is None:
        _instance = BatchRecorder()
    return _instance
