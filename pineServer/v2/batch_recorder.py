"""
BatchRecorder - Motor de persistencia V2

Responsable de guardar los resultados de los batches y actualizar el estado
del usuario en la base de datos. Es el único componente que escribe en la BD
para garantizar integridad.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from roble_client import roble_client
from v2.models import BatchResult, ExerciseResult, UserGamificationState, UserOperationState, BatchType
from v2.config_manager import get_config_manager

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
            
            # 4. Registrar intento de miniboss si aplica
            if result.batch_type == BatchType.MINIBOSS:
                self._log_miniboss_attempt(result)
                
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
                "updated_at": datetime.utcnow().isoformat()
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
                "updated_at": datetime.utcnow().isoformat()
                # ... otros campos default
            }
            roble_client.insert_records("pine_user_operations", [new_record])

    def _update_user_gamification(self, result: BatchResult, current_state: UserGamificationState):
        """Calcula y actualiza streak, puntos totales y nivel de jugador"""
        
        streak_config = self.config_manager.get_streak_config()
        min_correct_streak = streak_config.get("min_correct", 4)
        
        # 1. Calcular Streak lógica
        today_str = datetime.utcnow().date().isoformat()
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
                yesterday = (datetime.utcnow().date() - timedelta(days=1)).isoformat()
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
            "updated_at": datetime.utcnow().isoformat()
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
        record = {
            "user_ref": result.user_ref,
            "operacion": result.operacion,
            "nivel_intentado": result.nivel_central, # Asumiendo que nivel central = nivel a aprobar
            "aprobado": result.miniboss_aprobado,
            "score": result.score_ganado,
            "correctos": result.ejercicios_correctos,
            "total": result.total_ejercicios,
            "created_at": datetime.utcnow().isoformat()
        }
        roble_client.insert_records("pine_mini_jefes_intentos", [record])

# Singleton
_batch_recorder_instance = None
def get_batch_recorder():
    global _batch_recorder_instance
    if _batch_recorder_instance is None:
        _batch_recorder_instance = BatchRecorder()
    return _batch_recorder_instance
