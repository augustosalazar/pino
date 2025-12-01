"""
Gamification Unlocks - Gestión de desbloqueos de operaciones y modos

Este módulo maneja la lógica de desbloqueos de operaciones y modos de juego.
"""

from typing import Dict, List
from datetime import datetime
import gamification_core as gc
import gamification_profile as gp
from roble_client import roble_client


# ======================================================================================
# VERIFICACIÓN DE DESBLOQUEOS DE OPERACIONES
# ======================================================================================

async def verificar_y_desbloquear_operaciones(user_ref: str) -> Dict[str, bool]:
    """
    Verifica y desbloquea operaciones automáticamente según el progreso del usuario.
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Dict con flags de qué se desbloqueó en esta llamada
    """
    perfil_completo = await gp.obtener_perfil_completo(user_ref)
    perfil = perfil_completo['perfil']
    operaciones = {op['operacion']: op for op in perfil_completo['operaciones']}
    
    desbloqueados = {
        'resta': False,
        'mult': False,
        'div': False
    }
    
    # Verificar RESTA
    if not operaciones['resta']['unlocked']:
        puede_desbloquear = gc.verificar_desbloqueo_resta(
            perfil['pd_global'],
            operaciones['suma']['pd_operacion'],
            operaciones['suma']['miniboss_completed']
        )
        
        if puede_desbloquear:
            await desbloquear_operacion(user_ref, 'resta')
            desbloqueados['resta'] = True
    
    # Verificar MULT
    if not operaciones['mult']['unlocked']:
        puede_desbloquear = gc.verificar_desbloqueo_mult(
            perfil['pd_global'],
            operaciones['resta']['pd_operacion'],
            operaciones['mult']['miniboss_completed']
        )
        
        if puede_desbloquear:
            await desbloquear_operacion(user_ref, 'mult')
            desbloqueados['mult'] = True
    
    # Verificar DIV
    if not operaciones['div']['unlocked']:
        puede_desbloquear = gc.verificar_desbloqueo_div(
            perfil['pd_global'],
            operaciones['mult']['pd_operacion'],
            operaciones['div']['miniboss_completed']
        )
        
        if puede_desbloquear:
            await desbloquear_operacion(user_ref, 'div')
            desbloqueados['div'] = True
    
    return desbloqueados


async def desbloquear_operacion(user_ref: str, operacion: str) -> Dict:
    """
    Desbloquea una operación para un usuario.
    
    Args:
        user_ref: Referencia del usuario
        operacion: Operación a desbloquear ('suma', 'resta', 'mult', 'div')
    
    Returns:
        Operación actualizada
    """
    operacion_obj = await gp.obtener_operacion(user_ref, operacion)
    
    if not operacion_obj:
        raise Exception(f"Operación {operacion} no encontrada")
    
    if operacion_obj['unlocked']:
        return operacion_obj  # Ya estaba desbloqueada
    
    updates = {
        'unlocked': True,
        'nivel_dominio': 1,  # Al desbloquear, empieza en nivel 1
        'updated_at': datetime.now().isoformat()
    }
    
    roble_client.update_record('pine_user_operations', operacion_obj['_id'], updates)
    
    return await gp.obtener_operacion(user_ref, operacion)


async def marcar_minijefe_completado(user_ref: str, operacion: str) -> Dict:
    """
    Marca un mini-jefe como completado.
    
    Args:
        user_ref: Referencia del usuario
        operacion: Operación del mini-jefe ('suma', 'mult', 'div')
    
    Returns:
        Operación actualizada
    """
    operacion_obj = await gp.obtener_operacion(user_ref, operacion)
    
    if not operacion_obj:
        raise Exception(f"Operación {operacion} no encontrada")
    
    updates = {
        'miniboss_completed': True,
        'updated_at': datetime.now().isoformat()
    }
    
    roble_client.update_record('pine_user_operations', operacion_obj['_id'], updates)
    
    return await gp.obtener_operacion(user_ref, operacion)


async def registrar_intento_minijefe(user_ref: str, operacion: str) -> Dict:
    """
    Registra un intento de mini-jefe.
    
    Args:
        user_ref: Referencia del usuario
        operacion: Operación del mini-jefe
    
    Returns:
        Operación actualizada
    """
    operacion_obj = await gp.obtener_operacion(user_ref, operacion)
    
    if not operacion_obj:
        raise Exception(f"Operación {operacion} no encontrada")
    
    updates = {
        'miniboss_attempts': operacion_obj['miniboss_attempts'] + 1,
        'miniboss_last_attempt': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    roble_client.update_record('pine_user_operations', operacion_obj['_id'], updates)
    
    return await gp.obtener_operacion(user_ref, operacion)


# ======================================================================================
# VERIFICACIÓN DE DESBLOQUEOS DE MODOS
# ======================================================================================

async def verificar_y_actualizar_modos(user_ref: str) -> Dict[str, bool]:
    """
    Verifica y actualiza los flags de modos desbloqueados.
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Dict con modos actualmente desbloqueados
    """
    perfil_completo = await gp.obtener_perfil_completo(user_ref)
    operaciones = {op['operacion']: op for op in perfil_completo['operaciones']}
    
    # Obtener niveles de dominio
    nivel_suma = operaciones['suma']['nivel_dominio']
    nivel_resta = operaciones['resta']['nivel_dominio']
    nivel_mult = operaciones['mult']['nivel_dominio']
    nivel_div = operaciones['div']['nivel_dominio']
    
    # Calcular qué modos están desbloqueados
    modos_desbloqueados = gc.verificar_desbloqueos_modos(
        nivel_suma, nivel_resta, nivel_mult, nivel_div
    )
    
    # Actualizar perfil con los modos
    perfil = perfil_completo['perfil']
    updates = {
        'unlocked_mix_suma_resta': modos_desbloqueados['mix_suma_resta'],
        'unlocked_mix_mult_div': modos_desbloqueados['mix_mult_div'],
        'unlocked_speed': modos_desbloqueados['speed'],
        'unlocked_bosses': modos_desbloqueados['bosses'],
        'unlocked_elite': modos_desbloqueados['elite'],
        'unlocked_master': modos_desbloqueados['master'],
        'updated_at': datetime.now().isoformat()
    }
    
    roble_client.update_record('pine_user_gamification', perfil['_id'], updates)
    
    return modos_desbloqueados


async def obtener_modos_disponibles(user_ref: str) -> Dict:
    """
    Obtiene los modos de juego disponibles para un usuario.
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Dict con información de modos disponibles
    """
    await verificar_y_actualizar_modos(user_ref)
    
    perfil = await gp.obtener_perfil_gamificacion(user_ref)
    
    return {
        'mix_suma_resta': perfil['unlocked_mix_suma_resta'],
        'mix_mult_div': perfil['unlocked_mix_mult_div'],
        'speed': perfil['unlocked_speed'],
        'bosses': perfil['unlocked_bosses'],
        'elite': perfil['unlocked_elite'],
        'master': perfil['unlocked_master']
    }


# ======================================================================================
# VERIFICACIÓN DE OPERACIONES DISPONIBLES
# ======================================================================================

async def obtener_operaciones_disponibles(user_ref: str) -> List[str]:
    """
    Obtiene la lista de operaciones desbloqueadas para un usuario.
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Lista de nombres de operaciones desbloqueadas
    """
    operaciones = await gp.obtener_operaciones_usuario(user_ref)
    
    return [
        op['operacion'] 
        for op in operaciones 
        if op['unlocked']
    ]


async def puede_realizar_operacion(user_ref: str, operacion: str) -> bool:
    """
    Verifica si un usuario puede realizar una operación específica.
    
    Args:
        user_ref: Referencia del usuario
        operacion: Operación a verificar
    
    Returns:
        True si la operación está desbloqueada
    """
    operacion_obj = await gp.obtener_operacion(user_ref, operacion)
    
    if not operacion_obj:
        return False
    
    return operacion_obj['unlocked']


# ======================================================================================
# INFORMACIÓN DE PROGRESO DE DESBLOQUEOS
# ======================================================================================

async def obtener_progreso_desbloqueos(user_ref: str) -> Dict:
    """
    Obtiene información detallada del progreso hacia desbloqueos.
    
    Args:
        user_ref: Referencia del usuario
    
    Returns:
        Dict con progreso de cada desbloqueo
    """
    perfil_completo = await gp.obtener_perfil_completo(user_ref)
    perfil = perfil_completo['perfil']
    operaciones = {op['operacion']: op for op in perfil_completo['operaciones']}
    
    progreso = {}
    
    # Progreso para RESTA
    if not operaciones['resta']['unlocked']:
        progreso['resta'] = {
            'desbloqueada': False,
            'requisitos': {
                'pd_global': {
                    'actual': perfil['pd_global'],
                    'requerido': gc.DESBLOQUEO_RESTA['pd_global_min'],
                    'cumplido': perfil['pd_global'] >= gc.DESBLOQUEO_RESTA['pd_global_min']
                },
                'pd_suma': {
                    'actual': operaciones['suma']['pd_operacion'],
                    'requerido': gc.DESBLOQUEO_RESTA['pd_suma_min'],
                    'cumplido': operaciones['suma']['pd_operacion'] >= gc.DESBLOQUEO_RESTA['pd_suma_min']
                },
                'minijefe_suma': {
                    'completado': operaciones['suma']['miniboss_completed']
                }
            }
        }
    else:
        progreso['resta'] = {'desbloqueada': True}
    
    # Progreso para MULT
    if not operaciones['mult']['unlocked']:
        progreso['mult'] = {
            'desbloqueada': False,
            'requisitos': {
                'pd_global': {
                    'actual': perfil['pd_global'],
                    'requerido': gc.DESBLOQUEO_MULT['pd_global_min'],
                    'cumplido': perfil['pd_global'] >= gc.DESBLOQUEO_MULT['pd_global_min']
                },
                'pd_resta': {
                    'actual': operaciones['resta']['pd_operacion'],
                    'requerido': gc.DESBLOQUEO_MULT['pd_resta_min'],
                    'cumplido': operaciones['resta']['pd_operacion'] >= gc.DESBLOQUEO_MULT['pd_resta_min']
                },
                'minijefe_mult': {
                    'completado': operaciones['mult']['miniboss_completed']
                }
            }
        }
    else:
        progreso['mult'] = {'desbloqueada': True}
    
    # Progreso para DIV
    if not operaciones['div']['unlocked']:
        progreso['div'] = {
            'desbloqueada': False,
            'requisitos': {
                'pd_global': {
                    'actual': perfil['pd_global'],
                    'requerido': gc.DESBLOQUEO_DIV['pd_global_min'],
                    'cumplido': perfil['pd_global'] >= gc.DESBLOQUEO_DIV['pd_global_min']
                },
                'pd_mult': {
                    'actual': operaciones['mult']['pd_operacion'],
                    'requerido': gc.DESBLOQUEO_DIV['pd_mult_min'],
                    'cumplido': operaciones['mult']['pd_operacion'] >= gc.DESBLOQUEO_DIV['pd_mult_min']
                },
                'minijefe_div': {
                    'completado': operaciones['div']['miniboss_completed']
                }
            }
        }
    else:
        progreso['div'] = {'desbloqueada': True}
    
    return progreso
