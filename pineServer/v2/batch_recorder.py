"""
BatchRecorder - Motor de persistencia V2

Responsable de guardar los resultados de los batches y actualizar el estado
del usuario en la base de datos. Es el único componente que escribe en la BD
para garantizar integridad.
"""

import sys
import os
import json
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from roble_client import roble_client
from v2.models import BatchResult, ExerciseResult, UserGamificationState, UserOperationState, BatchType
from v2.config_manager import get_config_manager
from datetime_utils import now_colombia, now_utc_iso

class BatchRecorder:
    
    def __init__(self):
        self.config_manager = get_config_manager()
    
    def record_batch(self, result: BatchResult, current_gamif_state: UserGamificationState) -> bool:
        """
        Guarda el batch y actualiza todos los estados relacionados.
        
        Args:
            result: Objeto con todos los resultados del batch
            current_gamif_state: Estado actual de gamificación (para calcular streak)
            
        Returns:
            True si todo se guardó correctamente
        """
        try:
            # 1. Insertar en pine_batches_completados
            batch_id = self._insert_batch_log(result)
            if not batch_id:
                print(f"[BatchRecorder] Error inserting batch log for {result.user_ref}")
                return False
                
            # 2. Actualizar pine_user_operations
            self._update_user_operation(result)
            
            # 3. Actualizar pine_user_gamification (incluyendo streak)
            self._update_user_gamification(result, current_gamif_state)
            
            # 3.5. Actualizar pine_weekly_leaderboard
            self._update_weekly_leaderboard(result)
            
            # 4. Registrar intento de miniboss si aplica
            if result.batch_type == BatchType.MINIBOSS:
                self._log_miniboss_attempt(result)
            
            # 5. Guardar items fallidos para repaso
            self._save_pending_items(result)
                
            return True
            
        except Exception as e:
            print(f"[BatchRecorder] Critical error saving batch: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _insert_batch_log(self, result: BatchResult) -> Optional[str]:
        """Inserta el registro histórico del batch"""
        record = result.to_dict()
        
        # Serializar ejercicios_data a string JSON si es necesario para Roble
        if "ejercicios_data" in record:
            record["ejercicios_data"] = json.dumps(record["ejercicios_data"])

        record["session_ref"] = result.session_ref
            
        res = roble_client.insert_records("pine_batches_completados", [record])
        
        if res and res.get("inserted"):
            return res["inserted"][0].get("_id") # Retornar ID generado temporalmente (aunque Roble usa INT id)
        return "temp_id" # Fallback si no devuelve ID pero no falla

    def _update_user_operation(self, result: BatchResult):
        """Actualiza el estado de la operación (niveles, contadores)"""
        
        # Lógica de contadores de Miniboss
        reset_miniboss_counter = False
        increment_fail_counter = False
        reset_fail_counter = False
        
        if result.batch_type == BatchType.MINIBOSS:
            reset_miniboss_counter = True # Resetear contador de batches
            if result.miniboss_aprobado:
                reset_fail_counter = True
            else:
                increment_fail_counter = True
        
        # Preparar update
        # Nota: Roble no soporta "incrementar" atómicamente directo en update simple usualmente,
        # pero aquí asumimos que podemos calcular los valores finales o que update_or_replace maneja lógica de merge.
        # Dado que roble_client es simple, lo ideal es leer-modificar-escribir o usar SQL directo si pudiéramos.
        # Asumiremos un patrón "Upsert" inteligente o update parcial.
        
        # Para simplificar y dado que tenemos el estado "despues", enviamos el valor absoluto.
        # Pero necesitamos leer el estado actual de la BD para contadores acumulativos si no los tenemos en memoria.
        # Asumiremos que result.nivel_invisible_despues ES el nuevo valor absoluto.
        
        # Necesitamos saber el nivel dominio nuevo.
        # Si fue miniboss aprobado, sube.
        level_change = 0
        if result.batch_type == BatchType.MINIBOSS and result.miniboss_aprobado:
            level_change = 1
            
        # Como no tenemos el objeto "estado operación anterior" completo aquí, 
        # hacemos una query para obtenerlo y actualizarlo.
        current_ops = roble_client.read_table("pine_user_operations", {
            "user_ref": result.user_ref,
            "operacion": result.operacion
        })
        
        if not current_ops:
            # Crear nuevo registro
            op_state = UserOperationState(result.user_ref, result.operacion)
        else:
            op_state = UserOperationState.from_db_record(current_ops[0])
            
        # Aplicar cambios
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
             op_state.miniboss_completed = True # Completó miniboss del nivel anterior
        
        # Guardar en BD (update por user_ref + operacion)
        # roble_client.update_or_replace busca por _id, así que necesitamos el ID si existe
        record_id = current_ops[0].get("_id") if current_ops else None
        
        if record_id:
            # Update campos específicos para no sobrescribir todo si no queremos
            # Pero UserOperationState tiene todo lo importante
            # Mapear de vuelta a dict
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
            # Usar internal method o implementar update_record en client si existe
            # Asumimos que podemos usar insert_records con lógica de upsert o delete+insert manual
            # roble_client.py tiene update_record que usa _id
            roble_client.update_record("pine_user_operations", record_id, update_data)
        else:
            # Insertar nuevo
            new_record = {
                "user_ref": op_state.user_ref,
                "operacion": op_state.operacion,
                "nivel_dominio": op_state.nivel_dominio,
                "nivel_invisible": op_state.nivel_invisible,
                "pd_operacion": op_state.pd_operacion,
                "updated_at": now_utc_iso()
                # ... otros campos default
            }
            roble_client.insert_records("pine_user_operations", [new_record])

    def _update_user_gamification(self, result: BatchResult, current_state: UserGamificationState):
        """Calcula y actualiza streak, puntos totales y nivel de jugador"""
        
        streak_config = self.config_manager.get_streak_config()
        min_correct_streak = streak_config.get("min_correct", 4)
        
        # 1. Calcular Streak lógica
        today_str = now_colombia().date().isoformat()
        last_date_str = current_state.racha_ultima_fecha
        
        new_streak = current_state.racha_dias
        streak_updated = False
        
        if result.ejercicios_correctos >= min_correct_streak:
            # Fue un día productivo
            if last_date_str == today_str:
                # Ya contó hoy, no aumenta racha pero mantiene
                pass
            else:
                # Verificar si es consecutivo
                yesterday = (now_colombia().date() - timedelta(days=1)).isoformat()
                if last_date_str == yesterday:
                    new_streak += 1
                else:
                    # Se rompió la racha (o es nueva)
                    # Si la última vez fue hoy, no pasa nada
                    # Si no es ayer ni hoy, reset a 1 (porque hoy cumplió)
                    new_streak = 1
                
                streak_updated = True
                
            # Limitar streak máxima
            max_days = streak_config.get("max_days", 30)
            if new_streak > max_days: new_streak = max_days
            
        # Si no cumplió mínimo de correctos, NO reseteamos racha inmediatamente,
        # el usuario puede intentar de nuevo hoy. 
        # La racha solo se pierde si pasa el día sin actividad válida.
        # (Esta lógica de reseteo al consultar debería estar al inicio de sesión, aquí solo sumamos)
        
        # 2. Calcular Puntos Totales
        total_pp = current_state.pp_total + result.pp_ganados
        total_pd = current_state.pd_global + result.pd_ganados
        total_xp = current_state.xp_total + result.xp_ganada
        
        # 3. Actualizar BD
        # Buscar ID del registro de gamificación
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
            # Incrementar días válidos global
            updates["dias_validos_streak"] = current_state.dias_validos_streak + 1
            
        if rec_id:
            roble_client.update_record("pine_user_gamification", rec_id, updates)
        else:
            # Crear si no existe
            updates["user_ref"] = result.user_ref
            roble_client.insert_records("pine_user_gamification", [updates])

    def _log_miniboss_attempt(self, result: BatchResult):
        """Registra el intento de miniboss"""
        
        # Calcular porcentaje
        pct = 0.0
        if result.total_ejercicios > 0:
            pct = round(result.ejercicios_correctos / result.total_ejercicios, 2)
            
        record = {
            "user_ref": result.user_ref,
            "mini_jefe": result.operacion, # Schema expects 'mini_jefe'
            "exito": result.miniboss_aprobado, # Schema expects 'exito'
            "items_correctos": result.ejercicios_correctos, # Schema expects 'items_correctos'
            "total_items": result.total_ejercicios, # Schema expects 'total_items'
            "porcentaje_acierto": pct,
            "tiempo_total_segundos": result.duracion_segundos if result.duracion_segundos else 0.0,
            "fecha": now_utc_iso()
        }
        
        # Opcional: Si el miniboss desbloquea algo, calcularlo
        # Por ahora lo dejamos nulo o lo calculamos si tenemos la logica
        # record["operacion_desbloqueada"] = ...
        
        res = roble_client.insert_records("pine_mini_jefes_intentos", [record])
        if res and not res.get("inserted"):
             print(f"[BatchRecorder] Warning: Failed to insert miniboss log: {res}")

    def _save_pending_items(self, result: BatchResult):
        """Identifica errores y los guarda en pine_pending_items usando el esquema existente"""
        # Solo consideramos ejercicios fallidos que tienen referencia legacy
        failed_exercises = [
            ex for ex in result.ejercicios 
            if not ex.es_correcto and ex.legacy_ref
        ]
        
        if not failed_exercises:
            return

        if len(failed_exercises) > 8:
            print(f"[BatchRecorder] Too many failed exercises ({len(failed_exercises)}), skipping save to pending items.")
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
        """
        Calcula fecha_inicio y fecha_fin de la semana actual.
        Colombia: Semana = Lunes a Domingo
        
        Returns:
            (fecha_inicio, fecha_fin) como datetime objetos en UTC
        """
        if reference_date is None:
            reference_date = now_colombia().date()
        
        # Lunes = 0, Domingo = 6
        days_since_monday = reference_date.weekday()  # 0=Monday
        monday = reference_date - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        
        # Convertir a datetime en UTC (inicio de lunes y fin de domingo)
        fecha_inicio = datetime.combine(monday, datetime.min.time())
        fecha_fin = datetime.combine(sunday, datetime.max.time())
        
        return fecha_inicio, fecha_fin

    def _update_weekly_leaderboard(self, result: BatchResult):
        """
        Actualiza o crea registro en pine_weekly_leaderboard.
        
        Acumula PP, PD y score para la semana actual y gestiona ranking.
        """
        try:
            fecha_inicio, fecha_fin = self._get_week_dates()
            
            # Buscar si ya existe registro para esta semana
            weekly_records = roble_client.read_table(
                "pine_weekly_leaderboard",
                {
                    "user_ref": result.user_ref,
                    "semana_id": self._generate_semana_id(fecha_inicio)
                }
            )
            
            if weekly_records:
                # Actualizar existente
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
                print(f"[BatchRecorder] Updated weekly leaderboard for {result.user_ref}")
                
            else:
                # Insertar nuevo
                new_record = {
                    "user_ref": result.user_ref,
                    "semana_id": self._generate_semana_id(fecha_inicio),
                    "pp_semana": result.pp_ganados,
                    "pd_semana": result.pd_ganados,
                    "score_semanal": result.score_ganado,
                    "ranking": 0,  # Se calculará al final de la semana
                    "fecha_inicio": fecha_inicio.isoformat(),
                    "fecha_fin": fecha_fin.isoformat(),
                    "created_at": now_utc_iso(),
                }
                
                roble_client.insert_records("pine_weekly_leaderboard", [new_record])
                print(f"[BatchRecorder] Created new weekly leaderboard entry for {result.user_ref}")
                
            # Opcionalmente, recalcular rankings para la semana
            self._recalculate_weekly_rankings(fecha_inicio, fecha_fin)
            
        except Exception as e:
            print(f"[BatchRecorder] Warning: Failed to update weekly leaderboard: {e}")
            # No fallar el batch completo si el leaderboard falla

    def _generate_semana_id(self, fecha_inicio: datetime) -> str:
        """
        Genera un ID único para la semana basado en la fecha de inicio.
        Formato: YYYY-W## (ej: 2025-W02)
        """
        fecha_date = fecha_inicio.date() if isinstance(fecha_inicio, datetime) else fecha_inicio
        iso_calendar = fecha_date.isocalendar()
        return f"{iso_calendar[0]}-W{iso_calendar[1]:02d}"

    def _recalculate_weekly_rankings(self, fecha_inicio: datetime, fecha_fin: datetime):
        """
        Recalcula los rankings (posiciones) para todos los usuarios en la semana.
        Ordena por pp_semana descendente (primario) y score_semanal (secundario).
        """
        try:
            semana_id = self._generate_semana_id(fecha_inicio)
            
            # Obtener todos los registros de la semana
            all_weekly = roble_client.read_table(
                "pine_weekly_leaderboard",
                {}  # Sin filtro, obtenemos todos
            )
            
            # Filtrar por semana_id
            semana_records = [
                r for r in all_weekly
                if r.get("semana_id") == semana_id
            ]
            
            if not semana_records:
                return
            
            # Ordenar: primero PP (desc), luego score (desc)
            sorted_records = sorted(
                semana_records,
                key=lambda x: (
                    x.get("pp_semana", 0),
                    x.get("score_semanal", 0)
                ),
                reverse=True
            )
            
            # Asignar rankings
            for rank, record in enumerate(sorted_records, start=1):
                record_id = record.get("_id")
                if record_id and record.get("ranking") != rank:
                    roble_client.update_record(
                        "pine_weekly_leaderboard",
                        record_id,
                        {"ranking": rank}
                    )
            
            print(f"[BatchRecorder] Recalculated rankings for week {semana_id}: {len(sorted_records)} users")
            
        except Exception as e:
            print(f"[BatchRecorder] Warning: Failed to recalculate weekly rankings: {e}")
            # No es crítico, no fallar el batch

# Singleton
_batch_recorder_instance = None
def get_batch_recorder():
    global _batch_recorder_instance
    if _batch_recorder_instance is None:
        _batch_recorder_instance = BatchRecorder()
    return _batch_recorder_instance
