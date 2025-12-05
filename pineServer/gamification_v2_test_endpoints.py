"""
Gamification V2 - Test Endpoints
Endpoints para probar las nuevas tablas y modificaciones del sistema V2
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import json

from roble_client import roble_client

router = APIRouter(prefix="/api/v2/test", tags=["gamification_v2_test"])


# ==================== MODELS ====================

class UpdateNivelInvisibleRequest(BaseModel):
    user_ref: str
    operacion: str
    nivel_invisible: float


class CreateBatchRequest(BaseModel):
    user_ref: str
    operacion: str
    batch_type: str  # 'regular', 'miniboss', 'endless'
    nivel_central: int
    ejercicios_correctos: int
    total_ejercicios: int = 10


class ConfigDificultadRequest(BaseModel):
    operacion: str
    nivel: int
    min_operando_1: int
    max_operando_1: int
    min_operando_2: int
    max_operando_2: int
    max_resultado: Optional[int] = None
    tipo_respuesta: str = "multiple_choice"
    num_opciones: Optional[int] = 4
    max_tiempo_segundos: int = 30
    dificultad_score: float = 1.0


# ==================== ENDPOINTS DE VERIFICACIÓN ====================

@router.get("/verify/tables")
async def verify_tables():
    """
    Verifica que todas las tablas nuevas existan
    """
    try:
        results = {}
        
        # Verificar tablas nuevas
        new_tables = [
            "pine_batches_completados",
            "pine_configuracion_dificultad",
            "pine_leaderboard_endless_mensual",
            "pine_configuracion_sistema"
        ]
        
        for table_name in new_tables:
            try:
                # Intentar leer la tabla (vacía está bien)
                data = roble_client.read_table(table_name, {})
                results[table_name] = {
                    "exists": True,
                    "count": len(data) if data else 0
                }
            except Exception as e:
                results[table_name] = {
                    "exists": False,
                    "error": str(e)
                }
        
        # Verificar tabla modificada
        try:
            ops = roble_client.read_table("pine_user_operations", {})
            if ops and len(ops) > 0:
                sample = ops[0]
                results["pine_user_operations"] = {
                    "exists": True,
                    "has_nivel_invisible": "nivel_invisible" in sample,
                    "has_batches_desde_ultimo_miniboss": "batches_desde_ultimo_miniboss" in sample,
                    "has_miniboss_fallos_consecutivos": "miniboss_fallos_consecutivos" in sample,
                    "sample_fields": list(sample.keys())
                }
            else:
                results["pine_user_operations"] = {
                    "exists": True,
                    "note": "No records yet to verify fields"
                }
        except Exception as e:
            results["pine_user_operations"] = {
                "exists": False,
                "error": str(e)
            }
        
        # Verificar pine_user_gamification
        try:
            gamif = roble_client.read_table("pine_user_gamification", {})
            if gamif and len(gamif) > 0:
                sample = gamif[0]
                results["pine_user_gamification"] = {
                    "exists": True,
                    "has_racha_maxima": "racha_maxima" in sample,
                    "has_dias_validos_streak": "dias_validos_streak" in sample,
                    "sample_fields": list(sample.keys())
                }
            else:
                results["pine_user_gamification"] = {
                    "exists": True,
                    "note": "No records yet to verify fields"
                }
        except Exception as e:
            results["pine_user_gamification"] = {
                "exists": False,
                "error": str(e)
            }
        
        return {
            "status": "verification_complete",
            "tables": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/system")
async def get_system_config():
    """
    Obtiene toda la configuración del sistema
    """
    try:
        config = roble_client.read_table("pine_configuracion_sistema", {})
        return {
            "status": "success",
            "count": len(config) if config else 0,
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/difficulty/{operacion}/{nivel}")
async def get_difficulty_config(operacion: str, nivel: int):
    """
    Obtiene la configuración de dificultad para una operación y nivel
    """
    try:
        config = roble_client.read_table("pine_configuracion_dificultad", {
            "operacion": operacion,
            "nivel": nivel,
            "activa": True
        })
        
        if not config or len(config) == 0:
            return {
                "status": "not_found",
                "operacion": operacion,
                "nivel": nivel
            }
        
        return {
            "status": "success",
            "config": config[0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ENDPOINTS DE MODIFICACIÓN ====================

@router.post("/operations/update-nivel-invisible")
async def update_nivel_invisible(request: UpdateNivelInvisibleRequest):
    """
    Actualiza el nivel invisible de una operación para un usuario
    """
    try:
        # Buscar la operación del usuario
        operations = roble_client.read_table("pine_user_operations", {
            "user_ref": request.user_ref,
            "operacion": request.operacion
        })
        
        if not operations or len(operations) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Operation {request.operacion} not found for user {request.user_ref}"
            )
        
        operation = operations[0]
        operation_id = operation["id"]
        
        # Actualizar nivel invisible
        roble_client.update_record("pine_user_operations", operation_id, {
            "nivel_invisible": request.nivel_invisible,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        # Leer el registro actualizado
        updated = roble_client.read_table("pine_user_operations", {"id": operation_id})
        
        return {
            "status": "updated",
            "operation": updated[0] if updated else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batches/create")
async def create_test_batch(request: CreateBatchRequest):
    """
    Crea un batch de prueba en pine_batches_completados
    """
    try:
        # Calcular nivel invisible antes/después (simulado)
        nivel_invisible_antes = 1.5
        nivel_invisible_despues = 1.5
        
        # Ajustar según desempeño
        success_rate = request.ejercicios_correctos / request.total_ejercicios
        if success_rate >= 0.8:
            nivel_invisible_despues += 0.2
        elif success_rate < 0.4:
            nivel_invisible_despues -= 0.1
        
        # Generar ejercicios de prueba
        ejercicios_data = []
        for i in range(request.total_ejercicios):
            ejercicios_data.append({
                "num": i + 1,
                "operand_1": 5,
                "operand_2": 3,
                "respuesta_correcta": 8,
                "respuesta_usuario": 8 if i < request.ejercicios_correctos else 7,
                "es_correcto": i < request.ejercicios_correctos,
                "dificultad": 1.5,
                "tiempo_segundos": 3.5,
                "fue_retry": False
            })
        
        # Calcular puntuación
        dificultad_promedio = 1.5
        score_ganado = request.ejercicios_correctos * (5 + dificultad_promedio) + 10 - (2 * (request.total_ejercicios - request.ejercicios_correctos))
        score_ganado = max(0, int(score_ganado))
        
        # Crear registro
        batch_data = {
            "user_ref": request.user_ref,
            "batch_type": request.batch_type,
            "operacion": request.operacion,
            "nivel_central": request.nivel_central,
            "nivel_invisible_antes": nivel_invisible_antes,
            "nivel_invisible_despues": nivel_invisible_despues,
            "total_ejercicios": request.total_ejercicios,
            "ejercicios_correctos": request.ejercicios_correctos,
            "dificultad_promedio": dificultad_promedio,
            "score_ganado": score_ganado,
            "pp_ganados": request.total_ejercicios,
            "pd_ganados": request.ejercicios_correctos * 2,
            "xp_ganada": request.ejercicios_correctos * 10,
            "ejercicios_data": json.dumps(ejercicios_data),
            "completado_en": datetime.utcnow().isoformat(),
            "duracion_segundos": 60
        }
        
        # Agregar datos específicos de miniboss o endless
        if request.batch_type == "miniboss":
            batch_data["miniboss_aprobado"] = success_rate >= 0.8
        elif request.batch_type == "endless":
            batch_data["endless_streak"] = request.ejercicios_correctos
        
        result = roble_client.insert_records("pine_batches_completados", [batch_data])
        
        return {
            "status": "created",
            "batch": result.get("inserted", [{}])[0] if result.get("inserted") else None,
            "score_ganado": score_ganado,
            "nivel_invisible_change": nivel_invisible_despues - nivel_invisible_antes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/difficulty/add")
async def add_difficulty_config(request: ConfigDificultadRequest):
    """
    Agrega una nueva configuración de dificultad
    """
    try:
        config_data = {
            "operacion": request.operacion,
            "nivel": request.nivel,
            "min_operando_1": request.min_operando_1,
            "max_operando_1": request.max_operando_1,
            "min_operando_2": request.min_operando_2,
            "max_operando_2": request.max_operando_2,
            "max_resultado": request.max_resultado,
            "tipo_respuesta": request.tipo_respuesta,
            "num_opciones": request.num_opciones,
            "max_tiempo_segundos": request.max_tiempo_segundos,
            "dificultad_score": request.dificultad_score,
            "config_version": 1,
            "activa": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = roble_client.insert_records("pine_configuracion_dificultad", [config_data])
        
        return {
            "status": "created",
            "config": result.get("inserted", [{}])[0] if result.get("inserted") else None
        }
        
    except Exception as e:
        # Probablemente UNIQUE constraint violation
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f"Configuration for {request.operacion} nivel {request.nivel} already exists"
            )
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ENDPOINTS DE CONSULTA ====================

@router.get("/user/{user_ref}/operations")
async def get_user_operations(user_ref: str):
    """
    Obtiene todas las operaciones de un usuario con los nuevos campos
    """
    try:
        operations = roble_client.read_table("pine_user_operations", {
            "user_ref": user_ref
        })
        
        if not operations:
            return {
                "status": "not_found",
                "user_ref": user_ref,
                "operations": []
            }
        
        # Resaltar los nuevos campos
        formatted_ops = []
        for op in operations:
            formatted_ops.append({
                "operacion": op.get("operacion"),
                "nivel_dominio": op.get("nivel_dominio"),
                "nivel_invisible": op.get("nivel_invisible"),  # NUEVO
                "pd_operacion": op.get("pd_operacion"),
                "unlocked": op.get("unlocked"),
                "miniboss_completed": op.get("miniboss_completed"),
                "miniboss_attempts": op.get("miniboss_attempts"),
                "batches_desde_ultimo_miniboss": op.get("batches_desde_ultimo_miniboss"),  # NUEVO
                "miniboss_fallos_consecutivos": op.get("miniboss_fallos_consecutivos"),  # NUEVO
                "total_ejercicios": op.get("total_ejercicios"),
                "total_correctos": op.get("total_correctos")
            })
        
        return {
            "status": "success",
            "user_ref": user_ref,
            "count": len(formatted_ops),
            "operations": formatted_ops
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_ref}/batches")
async def get_user_batches(user_ref: str, limit: int = 10):
    """
    Obtiene el historial de batches de un usuario
    """
    try:
        batches = roble_client.read_table("pine_batches_completados", {
            "user_ref": user_ref
        })
        
        if not batches:
            return {
                "status": "no_batches",
                "user_ref": user_ref,
                "batches": []
            }
        
        # Ordenar por fecha (más recientes primero)
        batches_sorted = sorted(
            batches,
            key=lambda x: x.get("completado_en", ""),
            reverse=True
        )[:limit]
        
        # Formatear respuesta
        formatted_batches = []
        for batch in batches_sorted:
            formatted_batches.append({
                "id": batch.get("id"),
                "batch_type": batch.get("batch_type"),
                "operacion": batch.get("operacion"),
                "nivel_central": batch.get("nivel_central"),
                "nivel_invisible_antes": batch.get("nivel_invisible_antes"),
                "nivel_invisible_despues": batch.get("nivel_invisible_despues"),
                "ejercicios_correctos": f"{batch.get('ejercicios_correctos')}/{batch.get('total_ejercicios')}",
                "score_ganado": batch.get("score_ganado"),
                "pp_ganados": batch.get("pp_ganados"),
                "miniboss_aprobado": batch.get("miniboss_aprobado"),
                "endless_streak": batch.get("endless_streak"),
                "completado_en": batch.get("completado_en")
            })
        
        return {
            "status": "success",
            "user_ref": user_ref,
            "count": len(formatted_batches),
            "batches": formatted_batches
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_ref}/gamification")
async def get_user_gamification(user_ref: str):
    """
    Obtiene el perfil de gamificación con los nuevos campos
    """
    try:
        gamif = roble_client.read_table("pine_user_gamification", {
            "user_ref": user_ref
        })
        
        if not gamif or len(gamif) == 0:
            return {
                "status": "not_found",
                "user_ref": user_ref
            }
        
        profile = gamif[0]
        
        return {
            "status": "success",
            "user_ref": user_ref,
            "profile": {
                "pp_total": profile.get("pp_total"),
                "pd_global": profile.get("pd_global"),
                "xp_total": profile.get("xp_total"),
                "nivel_jugador": profile.get("nivel_jugador"),
                "racha_dias": profile.get("racha_dias"),
                "racha_maxima": profile.get("racha_maxima"),  # NUEVO
                "dias_validos_streak": profile.get("dias_validos_streak"),  # NUEVO
                "racha_ultima_fecha": profile.get("racha_ultima_fecha")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/batches")
async def get_batch_stats():
    """
    Estadísticas generales de batches completados
    """
    try:
        batches = roble_client.read_table("pine_batches_completados", {})
        
        if not batches:
            return {
                "status": "no_data",
                "total_batches": 0
            }
        
        # Calcular estadísticas
        total = len(batches)
        by_type = {}
        by_operation = {}
        
        for batch in batches:
            # Por tipo
            batch_type = batch.get("batch_type", "unknown")
            by_type[batch_type] = by_type.get(batch_type, 0) + 1
            
            # Por operación
            operacion = batch.get("operacion", "unknown")
            by_operation[operacion] = by_operation.get(operacion, 0) + 1
        
        return {
            "status": "success",
            "total_batches": total,
            "by_type": by_type,
            "by_operation": by_operation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ENDPOINT DE LIMPIEZA ====================

@router.delete("/cleanup/test-data")
async def cleanup_test_data(confirm: str = ""):
    """
    Limpia datos de prueba (requiere confirmación)
    PRECAUCIÓN: Solo usar en desarrollo
    """
    if confirm != "YES_DELETE_TEST_DATA":
        return {
            "status": "confirmation_required",
            "message": "Add query param ?confirm=YES_DELETE_TEST_DATA to proceed"
        }
    
    try:
        # ADVERTENCIA: Esto eliminaría TODOS los batches
        # En producción, deberías filtrar por algún marcador de test
        
        return {
            "status": "disabled",
            "message": "Cleanup endpoint disabled for safety. Implement with proper test data markers."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
