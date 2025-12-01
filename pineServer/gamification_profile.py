"""
Gamification Profile - Gestión de perfiles de gamificación de usuarios

Este módulo maneja todas las operaciones de base de datos relacionadas con
el perfil de gamificación de los usuarios.
"""

from typing import Dict, List, Optional
from datetime import datetime
from roble_client import roble_client
import gamification_core as gc


# ======================================================================================
# INICIALIZACIÓN DE PERFIL
# ======================================================================================

async def crear_perfil_gamificacion(user_ref: str) -> Dict:
    """
    Crea el perfil de gamificación inicial para un usuario.
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Perfil creado
    """
    perfil = {
        'user_ref': user_ref,
        'pp_total': 0,
        'pp_dia': 0,
        'pp_semana': 0,
        'pp_dia_max': gc.PP_DIA_MAX,
        'pd_global': 0,
        'pd_semana': 0,
        'xp_total': 0,
        'nivel_jugador': 1,
        'racha_dias': 0,
        'unlocked_mix_suma_resta': False,
        'unlocked_mix_mult_div': False,
        'unlocked_speed': False,
        'unlocked_bosses': False,
        'unlocked_elite': False,
        'unlocked_master': False,
        'semana_inicio': datetime.now().isoformat(),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    result = roble_client.insert_records('pine_user_gamification', [perfil])
    
    if result.get('inserted'):
        # Retornar el registro insertado si está disponible
        if result['inserted']:
            return result['inserted'][0]
        return perfil
    else:
        raise Exception(f"Error creando perfil de gamificación: {result}")


async def inicializar_operaciones(user_ref: str) -> List[Dict]:
    """
    Inicializa las 4 operaciones para un usuario.
    SUMA empieza desbloqueada, las demás bloqueadas.
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Lista de operaciones creadas
    """
    operaciones = []
    
    for op in ['suma', 'resta', 'mult', 'div']:
        operacion = {
            'user_ref': user_ref,
            'operacion': op,
            'pd_operacion': 0,
            'nivel_dominio': 1 if op == 'suma' else 0,  # SUMA nivel 1, otras 0
            'unlocked': op == 'suma',  # Solo SUMA desbloqueada
            'miniboss_completed': False,
            'miniboss_attempts': 0,
            'total_ejercicios': 0,
            'total_correctos': 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        operaciones.append(operacion)
    
    result = roble_client.insert_records('pine_user_operations', operaciones)
    
    if result.get('inserted'):
        return result['inserted']
    else:
        raise Exception(f"Error inicializando operaciones: {result}")


async def inicializar_perfil_completo(user_ref: str) -> Dict:
    """
    Inicializa el perfil completo de gamificación (perfil + operaciones).
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Perfil completo con operaciones
    """
    perfil = await crear_perfil_gamificacion(user_ref)
    operaciones = await inicializar_operaciones(user_ref)
    
    return {
        'perfil': perfil,
        'operaciones': operaciones
    }


# ======================================================================================
# OBTENCIÓN DE DATOS
# ======================================================================================

async def obtener_perfil_gamificacion(user_ref: str) -> Optional[Dict]:
    """
    Obtiene el perfil de gamificación de un usuario.
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Perfil de gamificación o None si no existe
    """
    registros = roble_client.read_table('pine_user_gamification', {'user_ref': user_ref})
    
    if registros:
        return registros[0]
    return None


async def obtener_operaciones_usuario(user_ref: str) -> List[Dict]:
    """
    Obtiene todas las operaciones de un usuario.
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Lista de operaciones
    """
    return roble_client.read_table('pine_user_operations', {'user_ref': user_ref})


async def obtener_operacion(user_ref: str, operacion: str) -> Optional[Dict]:
    """
    Obtiene una operación específica de un usuario.
    
    Args:
        user_ref: Referencia del usuario
        operacion: Nombre de la operación ('suma', 'resta', 'mult', 'div')
    
    Returns:
        Operación o None si no existe
    """
    registros = roble_client.read_table('pine_user_operations', {
        'user_ref': user_ref,
        'operacion': operacion
    })
    
    if registros:
        return registros[0]
    return None


async def obtener_perfil_completo(user_ref: str) -> Dict:
    """
    Obtiene el perfil completo de gamificación con todas las operaciones.
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Dict con 'perfil' y 'operaciones'
    """
    perfil = await obtener_perfil_gamificacion(user_ref)
    operaciones = await obtener_operaciones_usuario(user_ref)
    
    # Si no existe perfil, inicializarlo
    if not perfil:
        return await inicializar_perfil_completo(user_ref)
    
    # Si no existen operaciones, inicializarlas
    if not operaciones or len(operaciones) < 4:
        operaciones = await inicializar_operaciones(user_ref)
    
    # Enriquecer operaciones con niveles calculados
    operaciones_enriquecidas = []
    for op in operaciones:
        op_enriquecida = op.copy()
        op_enriquecida['nivel_dominio'] = gc.calcular_nivel_dominio(op['pd_operacion'])
        operaciones_enriquecidas.append(op_enriquecida)
    
    return {
        'perfil': perfil,
        'operaciones': operaciones_enriquecidas
    }


# ======================================================================================
# ACTUALIZACIÓN DE DATOS
# ======================================================================================

async def actualizar_pp(user_ref: str, pp_delta: int, actualizar_dia: bool = True, actualizar_semana: bool = True) -> Dict:
    """
    Actualiza los PP del usuario.
    
    Args:
        user_ref: Referencia del usuario
        pp_delta: Cantidad de PP a sumar (puede ser negativo)
        actualizar_dia: Si True, actualiza pp_dia
        actualizar_semana: Si True, actualiza pp_semana
    
    Returns:
        Perfil actualizado
    """
    perfil = await obtener_perfil_gamificacion(user_ref)
    
    if not perfil:
        raise Exception(f"Perfil no encontrado para user_ref: {user_ref}")
    
    updates = {
        'pp_total': perfil['pp_total'] + pp_delta,
        'updated_at': datetime.now().isoformat()
    }
    
    if actualizar_dia:
        # Respetar límite diario
        nuevo_pp_dia = min(perfil['pp_dia'] + pp_delta, gc.PP_DIA_MAX)
        updates['pp_dia'] = nuevo_pp_dia
    
    if actualizar_semana:
        updates['pp_semana'] = perfil['pp_semana'] + pp_delta
    
    roble_client.update_record('pine_user_gamification', perfil['_id'], updates)
    
    # Retornar perfil actualizado
    return await obtener_perfil_gamificacion(user_ref)


async def actualizar_pd(user_ref: str, pd_global_delta: int, pd_operacion_delta: int, operacion: str) -> tuple[Dict, Dict]:
    """
    Actualiza los PD globales y de una operación específica.
    
    Args:
        user_ref: Referencia del usuario
        pd_global_delta: PD a sumar al global
        pd_operacion_delta: PD a sumar a la operación
        operacion: Operación a actualizar
    
    Returns:
        (perfil_actualizado, operacion_actualizada)
    """
    # Actualizar PD global
    perfil = await obtener_perfil_gamificacion(user_ref)
    
    if not perfil:
        raise Exception(f"Perfil no encontrado para user_ref: {user_ref}")
    
    perfil_updates = {
        'pd_global': perfil['pd_global'] + pd_global_delta,
        'pd_semana': perfil['pd_semana'] + pd_global_delta,
        'updated_at': datetime.now().isoformat()
    }
    
    roble_client.update_record('pine_user_gamification', perfil['_id'], perfil_updates)
    
    # Actualizar PD de operación
    operacion_obj = await obtener_operacion(user_ref, operacion)
    
    if not operacion_obj:
        raise Exception(f"Operación {operacion} no encontrada para user_ref: {user_ref}")
    
    nuevo_pd_operacion = operacion_obj['pd_operacion'] + pd_operacion_delta
    nuevo_nivel_dominio = gc.calcular_nivel_dominio(nuevo_pd_operacion)
    
    operacion_updates = {
        'pd_operacion': nuevo_pd_operacion,
        'nivel_dominio': nuevo_nivel_dominio,
        'updated_at': datetime.now().isoformat()
    }
    
    roble_client.update_record('pine_user_operations', operacion_obj['_id'], operacion_updates)
    
    # Retornar datos actualizados
    perfil_nuevo = await obtener_perfil_gamificacion(user_ref)
    operacion_nueva = await obtener_operacion(user_ref, operacion)
    
    return perfil_nuevo, operacion_nueva


async def actualizar_xp(user_ref: str, xp_delta: int) -> tuple[Dict, bool, int]:
    """
    Actualiza la XP del usuario y verifica level up.
    
    Args:
        user_ref: Referencia del usuario
        xp_delta: XP a sumar
    
    Returns:
        (perfil_actualizado, hubo_levelup: bool, pd_recompensa: int)
    """
    perfil = await obtener_perfil_gamificacion(user_ref)
    
    if not perfil:
        raise Exception(f"Perfil no encontrado para user_ref: {user_ref}")
    
    xp_anterior = perfil['xp_total']
    xp_nueva = xp_anterior + xp_delta
    
    # Verificar level up
    hubo_levelup, nivel_nuevo, pd_recompensa = gc.verificar_levelup(xp_anterior, xp_nueva)
    
    updates = {
        'xp_total': xp_nueva,
        'nivel_jugador': nivel_nuevo,
        'updated_at': datetime.now().isoformat()
    }
    
    # Si hubo level up, sumar PD de recompensa
    if hubo_levelup and pd_recompensa > 0:
        updates['pd_global'] = perfil['pd_global'] + pd_recompensa
        updates['pd_semana'] = perfil['pd_semana'] + pd_recompensa
    
    roble_client.update_record('pine_user_gamification', perfil['_id'], updates)
    
    perfil_nuevo = await obtener_perfil_gamificacion(user_ref)
    
    return perfil_nuevo, hubo_levelup, pd_recompensa


async def actualizar_racha(user_ref: str, incrementar: bool = True) -> Dict:
    """
    Actualiza la racha diaria del usuario.
    
    Args:
        user_ref: Referencia del usuario
        incrementar: Si True, incrementa la racha. Si False, la resetea a 0.
    
    Returns:
        Perfil actualizado
    """
    perfil = await obtener_perfil_gamificacion(user_ref)
    
    if not perfil:
        raise Exception(f"Perfil no encontrado para user_ref: {user_ref}")
    
    if incrementar:
        updates = {
            'racha_dias': perfil['racha_dias'] + 1,
            'updated_at': datetime.now().isoformat()
        }
    else:
        updates = {
            'racha_dias': 0,
            'updated_at': datetime.now().isoformat()
        }
    
    roble_client.update_record('pine_user_gamification', perfil['_id'], updates)
    
    return await obtener_perfil_gamificacion(user_ref)


async def incrementar_estadisticas_operacion(user_ref: str, operacion: str, total_ejercicios: int, correctos: int) -> Dict:
    """
    Incrementa las estadísticas de una operación.
    
    Args:
        user_ref: Referencia del usuario
        operacion: Operación a actualizar
        total_ejercicios: Número de ejercicios a sumar
        correctos: Número de correctos a sumar
    
    Returns:
        Operación actualizada
    """
    operacion_obj = await obtener_operacion(user_ref, operacion)
    
    if not operacion_obj:
        raise Exception(f"Operación {operacion} no encontrada para user_ref: {user_ref}")
    
    updates = {
        'total_ejercicios': operacion_obj['total_ejercicios'] + total_ejercicios,
        'total_correctos': operacion_obj['total_correctos'] + correctos,
        'updated_at': datetime.now().isoformat()
    }
    
    roble_client.update_record('pine_user_operations', operacion_obj['_id'], updates)
    
    return await obtener_operacion(user_ref, operacion)


# ======================================================================================
# RESETEOS
# ======================================================================================

async def resetear_pp_dia(user_ref: str) -> Dict:
    """
    Resetea los PP del día a 0.
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Perfil actualizado
    """
    perfil = await obtener_perfil_gamificacion(user_ref)
    
    if not perfil:
        return None
    
    updates = {
        'pp_dia': 0,
        'updated_at': datetime.now().isoformat()
    }
    
    roble_client.update_record('pine_user_gamification', perfil['_id'], updates)
    
    return await obtener_perfil_gamificacion(user_ref)


async def resetear_semana(user_ref: str) -> Dict:
    """
    Resetea los contadores semanales (PP y PD de la semana).
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Perfil actualizado
    """
    perfil = await obtener_perfil_gamificacion(user_ref)
    
    if not perfil:
        return None
    
    updates = {
        'pp_semana': 0,
        'pd_semana': 0,
        'semana_inicio': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    roble_client.update_record('pine_user_gamification', perfil['_id'], updates)
    
    return await obtener_perfil_gamificacion(user_ref)
