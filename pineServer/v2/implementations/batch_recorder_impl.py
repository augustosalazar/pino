"""
DefaultBatchRecorder - Default implementation of IBatchRecorder

Handles persistence of batch results and user state updates.
"""

import json
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any, List

from v2.interfaces import IBatchRecorder, IConfigManager
from v2.models import BatchResult, ExerciseResult, UserGamificationState, UserOperationState, BatchType
from roble_client import roble_client
from datetime_utils import now_colombia, now_utc_iso


class DefaultBatchRecorder(IBatchRecorder):
    """
    Default batch recorder that persists to database via roble_client.
    """
    
    def __init__(self, container=None):
        self._container = container
    
    @property
    def config_manager(self) -> IConfigManager:
        from v2.container import get_v2_container
        if self._container:
            return self._container.config_manager
        return get_v2_container().config_manager
    
    def record_batch(
        self,
        result: BatchResult,
        current_gamif_state: UserGamificationState
    ) -> bool:
        """
        Save batch and update all related state.
        
        Args:
            result: Complete batch result data
            current_gamif_state: Current gamification state for streak calculations
            
        Returns:
            True if all updates succeeded
        """
        try:
            # 1. Insert into pine_batches_completados
            batch_id = self._insert_batch_log(result)
            if not batch_id:
                print(f"[BatchRecorder] Error inserting batch log for {result.user_ref}")
                return False
                
            # 2. Update pine_user_operations
            self._update_user_operation(result)
            
            # 3. Update pine_user_gamification (including streak)
            self._update_user_gamification(result, current_gamif_state)
            
            # 3.5. Update pine_weekly_leaderboard
            self._update_weekly_leaderboard(result)
            
            # 3.6. Update pine_leaderboard_endless_mensual if endless mode
            if result.batch_type == BatchType.ENDLESS:
                self._update_endless_monthly_leaderboard(result)
            
            # 4. Log miniboss attempt if applicable
            if result.batch_type == BatchType.MINIBOSS:
                self._log_miniboss_attempt(result)
            
            # 5. Save failed items for review
            self._save_pending_items(result)
                
            return True
            
        except Exception as e:
            print(f"[BatchRecorder] Critical error saving batch: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _insert_batch_log(self, result: BatchResult) -> Optional[str]:
        """Insert historical batch record."""
        record = result.to_dict()
        
        if "ejercicios_data" in record:
            record["ejercicios_data"] = json.dumps(record["ejercicios_data"])

        record["session_ref"] = result.session_ref
            
        res = roble_client.insert_records("pine_batches_completados", [record])
        
        if res and res.get("inserted"):
            return res["inserted"][0].get("_id")
        return "temp_id"

    def _update_user_operation(self, result: BatchResult):
        """Update operation state (levels, counters)."""
        
        reset_miniboss_counter = False
        increment_fail_counter = False
        reset_fail_counter = False
        
        if result.batch_type == BatchType.MINIBOSS:
            reset_miniboss_counter = True
            if result.miniboss_aprobado:
                reset_fail_counter = True
            else:
                increment_fail_counter = True
        
        level_change = 0
        if result.batch_type == BatchType.MINIBOSS and result.miniboss_aprobado:
            level_change = 1
            
        current_ops = roble_client.read_table("pine_user_operations", {
            "user_ref": result.user_ref,
            "operacion": result.operacion
        })
        
        if not current_ops:
            op_state = UserOperationState(result.user_ref, result.operacion)
        else:
            op_state = UserOperationState.from_db_record(current_ops[0])
            
        # Apply changes
        op_state.nivel_invisible = result.nivel_invisible_despues
        if level_change > 0:
            op_state.nivel_dominio = min(5, op_state.nivel_dominio + level_change)
            
        op_state.pd_operacion += result.pd_ganados
        op_state.total_ejercicios += result.total_ejercicios
        op_state.total_correctos += result.ejercicios_correctos
        
        if reset_miniboss_counter:
            op_state.batches_desde_ultimo_miniboss = 0
        else:
            op_state.batches_desde_ultimo_miniboss += 1
            
        if reset_fail_counter:
            op_state.miniboss_fallos_consecutivos = 0
        elif increment_fail_counter:
            op_state.miniboss_fallos_consecutivos += 1
            
        if result.batch_type == BatchType.MINIBOSS and result.miniboss_aprobado:
            op_state.miniboss_completed = True
        
        record_id = current_ops[0].get("_id") if current_ops else None
        
        if record_id:
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
            roble_client.update_record("pine_user_operations", record_id, update_data)
        else:
            new_record = {
                "user_ref": op_state.user_ref,
                "operacion": op_state.operacion,
                "nivel_dominio": op_state.nivel_dominio,
                "nivel_invisible": op_state.nivel_invisible,
                "pd_operacion": op_state.pd_operacion,
                "updated_at": now_utc_iso()
            }
            roble_client.insert_records("pine_user_operations", [new_record])

    def _update_user_gamification(self, result: BatchResult, current_state: UserGamificationState):
        """Calculate and update streak, total points and player level."""
        
        streak_config = self.config_manager.get_streak_config()
        min_correct_streak = streak_config.get("min_correct", 4)
        
        today_str = now_colombia().date().isoformat()
        last_date_str = current_state.racha_ultima_fecha
        
        new_streak = current_state.racha_dias
        streak_updated = False
        
        if result.ejercicios_correctos >= min_correct_streak:
            if last_date_str == today_str:
                pass
            else:
                yesterday = (now_colombia().date() - timedelta(days=1)).isoformat()
                if last_date_str == yesterday:
                    new_streak += 1
                else:
                    new_streak = 1
                
                streak_updated = True
                
            max_days = streak_config.get("max_days", 30)
            if new_streak > max_days: 
                new_streak = max_days
        
        total_pp = current_state.pp_total + result.pp_ganados
        total_pd = current_state.pd_global + result.pd_ganados
        total_xp = current_state.xp_total + result.xp_ganada
        
        gamif_records = roble_client.read_table("pine_user_gamification", {"user_ref": result.user_ref})
        rec_id = gamif_records[0].get("_id") if gamif_records else None
        
        updates = {
            "pp_total": total_pp,
            "pd_global": total_pd,
            "xp_total": total_xp,
            "racha_dias": new_streak,
            "racha_maxima": max(current_state.racha_maxima, new_streak),
            "updated_at": now_utc_iso()
        }
        
        if streak_updated:
            updates["racha_ultima_fecha"] = today_str
            updates["dias_validos_streak"] = current_state.dias_validos_streak + 1
            
        if rec_id:
            roble_client.update_record("pine_user_gamification", rec_id, updates)
        else:
            updates["user_ref"] = result.user_ref
            roble_client.insert_records("pine_user_gamification", [updates])

    def _log_miniboss_attempt(self, result: BatchResult):
        """Record miniboss attempt."""
        pct = 0.0
        if result.total_ejercicios > 0:
            pct = round(result.ejercicios_correctos / result.total_ejercicios, 2)
            
        record = {
            "user_ref": result.user_ref,
            "mini_jefe": result.operacion,
            "exito": result.miniboss_aprobado,
            "items_correctos": result.ejercicios_correctos,
            "total_items": result.total_ejercicios,
            "porcentaje_acierto": pct,
            "tiempo_total_segundos": result.duracion_segundos if result.duracion_segundos else 0.0,
            "fecha": now_utc_iso()
        }
        
        res = roble_client.insert_records("pine_mini_jefes_intentos", [record])
        if res and not res.get("inserted"):
            print(f"[BatchRecorder] Warning: Failed to insert miniboss log: {res}")

    def _save_pending_items(self, result: BatchResult):
        """Identify errors and save to pine_pending_items."""
        failed_exercises = [
            ex for ex in result.ejercicios 
            if not ex.es_correcto and ex.legacy_ref
        ]
        
        if not failed_exercises:
            return

        if len(failed_exercises) > 8:
            print(f"[BatchRecorder] Too many failed exercises ({len(failed_exercises)}), skipping save.")
            return

        pending_records = []
        timestamp = now_utc_iso()
        
        for fail in failed_exercises:
            record = {
                "user_ref": result.user_ref,
                "exercise_ref": fail.legacy_ref,
                "operacion": fail.exercise.operacion,
                "dificultad": fail.exercise.dificultad,
                "intentos_fallidos": 1,
                "fecha_primer_fallo": timestamp,
                "fecha_ultimo_fallo": timestamp,
                "mostrado_nuevamente": False,
                "completado": False,
                "session_ref": result.session_ref,
            }
            pending_records.append(record)
            
        if pending_records:
            try:
                roble_client.insert_records("pine_pending_items", pending_records)
                print(f"[BatchRecorder] Saved {len(pending_records)} pending items")
            except Exception as e:
                print(f"[BatchRecorder] Failed to save pending items: {e}")

    def _get_week_dates(self, reference_date: date = None) -> tuple:
        """Calculate week start and end dates."""
        if reference_date is None:
            reference_date = now_colombia().date()
        
        days_since_monday = reference_date.weekday()
        monday = reference_date - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        
        fecha_inicio = datetime.combine(monday, datetime.min.time())
        fecha_fin = datetime.combine(sunday, datetime.max.time())
        
        return fecha_inicio, fecha_fin

    def _update_weekly_leaderboard(self, result: BatchResult):
        """Update or create weekly leaderboard record."""
        try:
            fecha_inicio, fecha_fin = self._get_week_dates()
            
            weekly_records = roble_client.read_table(
                "pine_weekly_leaderboard",
                {
                    "user_ref": result.user_ref,
                    "semana_id": self._generate_semana_id(fecha_inicio)
                }
            )
            
            if weekly_records:
                record = weekly_records[0]
                record_id = record.get("_id")
                
                updates = {
                    "pp_semana": record.get("pp_semana", 0) + result.pp_ganados,
                    "pd_semana": record.get("pd_semana", 0) + result.pd_ganados,
                    "score_semanal": round(
                        record.get("score_semanal", 0) + result.score_ganado,
                        2
                    ),
                }
                
                roble_client.update_record("pine_weekly_leaderboard", record_id, updates)
                
            else:
                new_record = {
                    "user_ref": result.user_ref,
                    "semana_id": self._generate_semana_id(fecha_inicio),
                    "pp_semana": result.pp_ganados,
                    "pd_semana": result.pd_ganados,
                    "score_semanal": result.score_ganado,
                    "ranking": 0,
                    "fecha_inicio": fecha_inicio.isoformat(),
                    "fecha_fin": fecha_fin.isoformat(),
                    "created_at": now_utc_iso(),
                }
                
                roble_client.insert_records("pine_weekly_leaderboard", [new_record])
                
            self._recalculate_weekly_rankings(fecha_inicio, fecha_fin)
            
        except Exception as e:
            print(f"[BatchRecorder] Warning: Failed to update weekly leaderboard: {e}")

    def _generate_semana_id(self, fecha_inicio: datetime) -> str:
        """Generate unique week ID."""
        fecha_date = fecha_inicio.date() if isinstance(fecha_inicio, datetime) else fecha_inicio
        iso_calendar = fecha_date.isocalendar()
        return f"{iso_calendar[0]}-W{iso_calendar[1]:02d}"

    def _recalculate_weekly_rankings(self, fecha_inicio: datetime, fecha_fin: datetime):
        """Recalculate rankings for the week."""
        try:
            semana_id = self._generate_semana_id(fecha_inicio)
            
            all_weekly = roble_client.read_table("pine_weekly_leaderboard", {})
            
            semana_records = [r for r in all_weekly if r.get("semana_id") == semana_id]
            
            if not semana_records:
                return
            
            sorted_records = sorted(
                semana_records,
                key=lambda x: (x.get("pp_semana", 0), x.get("score_semanal", 0)),
                reverse=True
            )
            
            for rank, record in enumerate(sorted_records, start=1):
                record_id = record.get("_id")
                if record_id and record.get("ranking") != rank:
                    roble_client.update_record(
                        "pine_weekly_leaderboard",
                        record_id,
                        {"ranking": rank}
                    )
            
        except Exception as e:
            print(f"[BatchRecorder] Warning: Failed to recalculate weekly rankings: {e}")

    def _get_month_dates(self, reference_date: date = None) -> tuple:
        """Calculate month start and end dates."""
        if reference_date is None:
            reference_date = now_colombia().date()
        
        fecha_inicio = reference_date.replace(day=1)
        
        if reference_date.month == 12:
            fecha_fin = reference_date.replace(year=reference_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fecha_fin = reference_date.replace(month=reference_date.month + 1, day=1) - timedelta(days=1)
        
        return fecha_inicio, fecha_fin

    def _generate_mes_id(self, fecha_inicio: date) -> str:
        """Generate unique month ID."""
        return fecha_inicio.strftime("%Y-%m")

    def _update_endless_monthly_leaderboard(self, result: BatchResult):
        """Update or create endless monthly leaderboard record."""
        try:
            if result.endless_streak is None:
                return
            
            fecha_inicio, fecha_fin = self._get_month_dates()
            mes_id = self._generate_mes_id(fecha_inicio)
            
            monthly_records = roble_client.read_table(
                "pine_leaderboard_endless_mensual",
                {"user_ref": result.user_ref, "mes_id": mes_id}
            )
            
            if monthly_records:
                record = monthly_records[0]
                record_id = record.get("_id")
                
                current_best = record.get("mejor_streak", 0)
                new_streak = result.endless_streak
                
                updates = {
                    "total_intentos": record.get("total_intentos", 0) + 1,
                    "updated_at": now_utc_iso(),
                }
                
                if new_streak > current_best:
                    updates["mejor_streak"] = new_streak
                
                roble_client.update_record("pine_leaderboard_endless_mensual", record_id, updates)
                
            else:
                new_record = {
                    "user_ref": result.user_ref,
                    "mes_id": mes_id,
                    "mejor_streak": result.endless_streak,
                    "total_intentos": 1,
                    "ranking": 0,
                    "fecha_inicio": fecha_inicio.isoformat(),
                    "fecha_fin": fecha_fin.isoformat(),
                    "created_at": now_utc_iso(),
                    "updated_at": now_utc_iso(),
                }
                
                roble_client.insert_records("pine_leaderboard_endless_mensual", [new_record])
                
            self._recalculate_endless_monthly_rankings(fecha_inicio, fecha_fin)
            
        except Exception as e:
            print(f"[BatchRecorder] Warning: Failed to update endless monthly leaderboard: {e}")

    def _recalculate_endless_monthly_rankings(self, fecha_inicio: date, fecha_fin: date):
        """Recalculate rankings for the month."""
        try:
            mes_id = self._generate_mes_id(fecha_inicio)
            
            all_monthly = roble_client.read_table("pine_leaderboard_endless_mensual", {})
            
            mes_records = [r for r in all_monthly if r.get("mes_id") == mes_id]
            
            if not mes_records:
                return
            
            sorted_records = sorted(
                mes_records,
                key=lambda x: (x.get("mejor_streak", 0), x.get("total_intentos", 0)),
                reverse=True
            )
            
            for rank, record in enumerate(sorted_records, start=1):
                record_id = record.get("_id")
                if record_id and record.get("ranking") != rank:
                    roble_client.update_record(
                        "pine_leaderboard_endless_mensual",
                        record_id,
                        {"ranking": rank, "updated_at": now_utc_iso()}
                    )
            
        except Exception as e:
            print(f"[BatchRecorder] Warning: Failed to recalculate endless monthly rankings: {e}")
