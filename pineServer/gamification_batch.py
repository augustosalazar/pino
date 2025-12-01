"""
Gamification Batch - Procesamiento de batches de ejercicios

Este módulo maneja el procesamiento completo de un batch de ejercicios,
incluyendo cálculos de recompensas, bonificaciones, y gestión de items pendientes.
"""

from typing import Dict, List
from datetime import datetime, date
import gamification_core as gc
import gamification_profile as gp
import gamification_unlocks as gu
from roble_client import roble_client


# ======================================================================================
# TIPO DE DATOS PARA RESULTADOS DE ITEMS
# ======================================================================================

"""
Formato esperado de resultado de un ítem:

{
    'exercise_id': str,  # ID del ejercicio en pine_exercises
    'fue_primer_intento': bool,  # True si acertó en primer intento
    'es_correcto_final': bool,  # True si el resultado final fue correcto
    'operacion': str,  # 'suma', 'resta', 'mult', 'div'
    'dificultad': float  # Nivel de dificultad del ejercicio
}
"""


# ======================================================================================
# PROCESAMIENTO DE BATCH COMPLETO
# ======================================================================================

async def procesar_batch_completo(
    user_ref: str,
    resultados_items: List[Dict],
    operacion_principal: str,
    dificultad_media: float = None
) -> Dict:
    """
    Procesa un batch completo de ejercicios y actualiza todas las métricas.
    
    Args:
        user_ref: Referencia del usuario
        resultados_items: Lista de resultados de ejercicios
        operacion_principal: Operación principal del batch
        dificultad_media: Dificultad media del batch (se calcula si no se proporciona)
    
    Returns:
        Dict con todo lo que se ganó y los cambios realizados
    """
    if not resultados_items:
        return {
            'error': 'No hay items para procesar'
        }
    
    # === 1. CÁLCULOS INICIALES ===
    
    total_items = len(resultados_items)
    correctos = sum(1 for item in resultados_items if item['es_correcto_final'])
    porcentaje_acierto = correctos / total_items if total_items > 0 else 0
    
    # Calcular dificultad media si no se proporcionó
    if dificultad_media is None:
        dificultad_media = sum(item.get('dificultad', 1.0) for item in resultados_items) / total_items
    
    # === 2. CALCULAR RECOMPENSAS ===
    
    # PP - 1 por cada item mostrado (límite diario se maneja en actualizar_pp)
    pp_ganados = total_items
    
    # PD por items
    pd_items_total = 0
    pd_items_por_operacion = {}
    
    for item in resultados_items:
        pd_item = gc.calcular_pd_ejercicio(
            item['fue_primer_intento'],
            item['es_correcto_final']
        )
        pd_items_total += pd_item
        
        # Acumular por operación
        op = item.get('operacion', operacion_principal)
        pd_items_por_operacion[op] = pd_items_por_operacion.get(op, 0) + pd_item
    
    # Bonus por porcentaje de acierto
    bonus_batch = gc.calcular_bonus_batch(porcentaje_acierto)
    
    # XP
    xp_ganada = gc.calcular_xp_batch(correctos, dificultad_media)
    
    # === 3. GESTIONAR RACHA DIARIA ===
    
    racha_info = await verificar_y_actualizar_racha(user_ref)
    bonus_racha = gc.PD_BONUS_RACHA_DIARIA if racha_info['bonus_aplicado'] else 0
    
    # === 4. ACTUALIZAR BASE DE DATOS ===
    
    # Actualizar PP
    await gp.actualizar_pp(user_ref, pp_ganados)
    
    # Actualizar PD (global, semanal, y por operación)
    pd_global_total = pd_items_total + bonus_batch + bonus_racha
    pd_operacion_total = pd_items_por_operacion.get(operacion_principal, 0)
    
    perfil, operacion_obj = await gp.actualizar_pd(
        user_ref,
        pd_global_total,
        pd_operacion_total,
        operacion_principal
    )
    
    # Actualizar XP y verificar level up
    perfil, hubo_levelup, pd_levelup = await gp.actualizar_xp(user_ref, xp_ganada)
    
    # Si hubo level up, el PD ya fue sumado en actualizar_xp
    # Solo necesitamos registrarlo en la respuesta
    
    # Actualizar estadísticas de la operación
    await gp.incrementar_estadisticas_operacion(
        user_ref,
        operacion_principal,
        total_items,
        correctos
    )
    
    # === 5. GESTIONAR ITEMS PENDIENTES ===
    
    items_para_repetir = [
        item for item in resultados_items
        if gc.debe_repetirse_item(item['fue_primer_intento'], item['es_correcto_final'])
    ]
    
    items_pendientes_info = await gestionar_items_pendientes(
        user_ref,
        items_para_repetir,
        operacion_principal
    )
    
    # === 6. VERIFICAR DESBLOQUEOS ===
    
    desbloqueos_operaciones = await gu.verificar_y_desbloquear_operaciones(user_ref)
    desbloqueos_modos = await gu.verificar_y_actualizar_modos(user_ref)
    
    # === 7. CONSTRUIR RESPUESTA ===
    
    return {
        'resumen': {
            'total_items': total_items,
            'correctos': correctos,
            'porcentaje_acierto': porcentaje_acierto,
            'dificultad_media': dificultad_media
        },
        'recompensas': {
            'pp_ganados': pp_ganados,
            'pd': {
                'por_items': pd_items_total,
                'bonus_batch': bonus_batch,
                'bonus_racha': bonus_racha,
                'bonus_levelup': pd_levelup,
                'total_pd_global': pd_global_total + pd_levelup
            },
            'xp_ganada': xp_ganada
        },
        'progreso': {
            'nivel_jugador': perfil['nivel_jugador'],
            'hubo_levelup': hubo_levelup,
            'nivel_dominio': operacion_obj['nivel_dominio'],
            'pd_global': perfil['pd_global'],
            'pd_operacion': operacion_obj['pd_operacion'],
            'xp_total': perfil['xp_total'],
            'racha_dias': perfil['racha_dias']
        },
        'items_pendientes': items_pendientes_info,
        'desbloqueos': {
            'operaciones': desbloqueos_operaciones,
            'modos': desbloqueos_modos,
            'hubo_desbloqueos': any(desbloqueos_operaciones.values()) or any(desbloqueos_modos.values())
        }
    }


# ======================================================================================
# GESTIÓN DE ITEMS PENDIENTES
# ======================================================================================

async def gestionar_items_pendientes(user_ref: str, items_fallados: List[Dict], operacion: str) -> Dict:
    """
    Gestiona los items que deben repetirse en el siguiente batch.
    
    Args:
        user_ref: Referencia del usuario
        items_fallados: Lista de items que fallaron (al menos una vez)
        operacion: Operación de los items
    
    Returns:
        Info sobre items pendientes
    """
    if not items_fallados:
        return {
            'total': 0,
            'nuevos': 0,
            'mensaje': 'No hay items pendientes'
        }
    
    items_agregados = 0
    
    for item in items_fallados:
        # Verificar si ya existe en pending_items
        existentes = roble_client.read_table('pine_pending_items', {
            'user_ref': user_ref,
            'exercise_ref': item['exercise_id']
        })
        
        if existentes:
            # Ya existe, incrementar intentos fallidos
            pending_item = existentes[0]
            updates = {
                'intentos_fallidos': pending_item['intentos_fallidos'] + 1,
                'fecha_ultimo_fallo': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            roble_client.update_record('pine_pending_items', pending_item['_id'], updates)
        else:
            # Nuevo item pendiente
            nuevo_pending = {
                'user_ref': user_ref,
                'exercise_ref': item['exercise_id'],
                'operacion': item.get('operacion', operacion),
                'dificultad': int(item.get('dificultad', 1)),
                'intentos_fallidos': 1,
                'fecha_primer_fallo': datetime.now().isoformat(),
                'fecha_ultimo_fallo': datetime.now().isoformat(),
                'mostrado_nuevamente': False,
                'completado': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            roble_client.insert_records('pine_pending_items', [nuevo_pending])
            items_agregados += 1
    
    return {
        'total': len(items_fallados),
        'nuevos': items_agregados,
        'mensaje': f'Se agregaron {items_agregados} items nuevos a la lista de pendientes'
    }


async def obtener_items_pendientes(user_ref: str, operacion: str, limite: int = 3) -> List[Dict]:
    """
    Obtiene items pendientes para incluir en el próximo batch.
    
    Args:
        user_ref: Referencia del usuario
        operacion: Operación para la que se solicitan items
        limite: Número máximo de items a devolver
    
    Returns:
        Lista de items pendientes
    """
    items_pendientes = roble_client.read_table('pine_pending_items', {
        'user_ref': user_ref,
        'operacion': operacion,
        'completado': False
    })
    
    # Ordenar por fecha del primer fallo (más antiguos primero)
    items_ordenados = sorted(
        items_pendientes,
        key=lambda x: x['fecha_primer_fallo']
    )
    
    return items_ordenados[:limite]


async def marcar_item_pendiente_completado(user_ref: str, exercise_ref: str) -> bool:
    """
    Marca un item pendiente como completado (cuando se acierta en primer intento).
    
    Args:
        user_ref: Referencia del usuario
        exercise_ref: Referencia del ejercicio
    
    Returns:
        True si se marcó exitosamente
    """
    items = roble_client.read_table('pine_pending_items', {
        'user_ref': user_ref,
        'exercise_ref': exercise_ref
    })
    
    if not items:
        return False
    
    pending_item = items[0]
    updates = {
        'completado': True,
        'fecha_completado': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    roble_client.update_record('pine_pending_items', pending_item['_id'], updates)
    return True


# ======================================================================================
# GESTIÓN DE RACHA DIARIA
# ======================================================================================

async def verificar_y_actualizar_racha(user_ref: str) -> Dict:
    """
    Verifica y actualiza la racha diaria del usuario.
    Aplica bonus de PD si corresponde (primer batch del día).
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Dict con info de la racha y si se aplicó bonus
    """
    perfil = await gp.obtener_perfil_gamificacion(user_ref)
    
    if not perfil:
        return {'racha_actual': 0, 'bonus_aplicado': False}
    
    # Verificar si ya jugó hoy
    # Nota: En producción, necesitarás almacenar "ultimo_dia_jugado" en el perfil
    # Por ahora, asumimos que si pp_dia > 0, ya jugó hoy
    
    ya_jugo_hoy = perfil['pp_dia'] > 0
    
    if not ya_jugo_hoy:
        # Primer batch del día
        # Incrementar racha
        await gp.actualizar_racha(user_ref, incrementar=True)
        
        # El bonus de racha se incluye en el procesamiento del batch
        return {
            'racha_actual': perfil['racha_dias'] + 1,
            'bonus_aplicado': True,
            'es_primer_batch_del_dia': True
        }
    else:
        # Ya jugó hoy
        return {
            'racha_actual': perfil['racha_dias'],
            'bonus_aplicado': False,
            'es_primer_batch_del_dia': False
        }


async def resetear_racha_si_necesario(user_ref: str) -> bool:
    """
    Resetea la racha si el usuario no jugó ayer.
    Esta función debería llamarse periódicamente (ej. en un cron job diario).
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        True si se reseteó la racha
    """
    # Nota: En producción, necesitarás verificar la fecha del último batch
    # y comparar con la fecha actual
    
    # Por ahora, esta es una función placeholder
    # La implementación real requeriría almacenar "ultimo_batch_fecha" en el perfil
    
    return False


# ======================================================================================
# ESTADÍSTICAS Y REPORTES
# ======================================================================================

async def obtener_estadisticas_batch(user_ref: str) -> Dict:
    """
    Obtiene estadísticas generales del usuario para mostrar después de un batch.
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Dict con estadísticas completas
    """
    perfil_completo = await gp.obtener_perfil_completo(user_ref)
    perfil = perfil_completo['perfil']
    operaciones = perfil_completo['operaciones']
    
    # Calcular operación más fuerte y más débil
    ops_desbloqueadas = [op for op in operaciones if op['unlocked']]
    
    if ops_desbloqueadas:
        op_mas_fuerte = max(ops_desbloqueadas, key=lambda x: x['pd_operacion'])
        op_mas_debil = min(ops_desbloqueadas, key=lambda x: x['pd_operacion'])
    else:
        op_mas_fuerte = None
        op_mas_debil = None
    
    return {
        'perfil': perfil,
        'operaciones': operaciones,
        'operacion_mas_fuerte': op_mas_fuerte['operacion'] if op_mas_fuerte else None,
        'operacion_mas_debil': op_mas_debil['operacion'] if op_mas_debil else None,
        'total_operaciones_desbloqueadas': len(ops_desbloqueadas)
    }
