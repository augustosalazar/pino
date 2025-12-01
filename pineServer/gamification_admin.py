"""
Gamification Admin Tasks - Scripts de mantenimiento

Este módulo contiene tareas administrativas para el sistema de gamificación:
- Reset diario de PP
- Reset semanal de PP/PD
- Verificación de rachas rotas

Estos scripts deben ejecutarse mediante cron jobs o tareas programadas.
"""

from typing import List, Dict
from datetime import datetime, timedelta
from roble_client import roble_client
import gamification_profile as gp


# ======================================================================================
# RESET DIARIO
# ======================================================================================

async def reset_pp_dia_todos_usuarios() -> Dict:
    """
    Reset diario de PP para todos los usuarios.
    
    Esta tarea debe ejecutarse DIARIAMENTE a medianoche.
    
    Returns:
        Dict con estadísticas del reset
    """
    print(f"[ADMIN] Starting daily PP reset at {datetime.now()}")
    
    # Get all gamification profiles
    profiles = roble_client.read_table("pine_user_gamification", {})
    
    total_users = len(profiles)
    reset_count = 0
    errors = []
    
    for profile in profiles:
        user_ref = profile.get('user_ref')
        try:
            await gp.resetear_pp_dia(user_ref)
            reset_count += 1
        except Exception as e:
            errors.append({
                'user_ref': user_ref,
                'error': str(e)
            })
            print(f"[ERROR] Failed to reset PP for user {user_ref}: {e}")
    
    result = {
        'task': 'reset_pp_dia',
        'timestamp': datetime.now().isoformat(),
        'total_users': total_users,
        'reset_count': reset_count,
        'errors_count': len(errors),
        'errors': errors[:10]  # Solo primeros 10 errores
    }
    
    print(f"[ADMIN] Daily PP reset complete: {reset_count}/{total_users} users")
    
    return result


# ======================================================================================
# RESET SEMANAL
# ======================================================================================

async def reset_semana_todos_usuarios() -> Dict:
    """
    Reset semanal de PP_semana y PD_semana para todos los usuarios.
    
    Esta tarea debe ejecutarse SEMANALMENTE (lunes a medianoche).
    
    Returns:
        Dict con estadísticas del reset
    """
    print(f"[ADMIN] Starting weekly reset at {datetime.now()}")
    
    # Get all gamification profiles
    profiles = roble_client.read_table("pine_user_gamification", {})
    
    total_users = len(profiles)
    reset_count = 0
    errors = []
    
    for profile in profiles:
        user_ref = profile.get('user_ref')
        try:
            await gp.resetear_semana(user_ref)
            reset_count += 1
        except Exception as e:
            errors.append({
                'user_ref': user_ref,
                'error': str(e)
            })
            print(f"[ERROR] Failed to reset week for user {user_ref}: {e}")
    
    result = {
        'task': 'reset_semana',
        'timestamp': datetime.now().isoformat(),
        'total_users': total_users,
        'reset_count': reset_count,
        'errors_count': len(errors),
        'errors': errors[:10]
    }
    
    print(f"[ADMIN] Weekly reset complete: {reset_count}/{total_users} users")
    
    return result


# ======================================================================================
# VERIFICACIÓN DE RACHAS
# ======================================================================================

async def verificar_rachas_rotas() -> Dict:
    """
    Verifica y resetea rachas de usuarios que no jugaron ayer.
    
    Esta tarea debe ejecutarse DIARIAMENTE (preferiblemente después del reset de PP).
    
    Lógica:
    - Si un usuario tiene racha_dias > 0 pero pp_dia == 0 (no jugó hoy)
    - Y ya pasó suficiente tiempo desde el último reset
    - Entonces su racha se rompe → racha_dias = 0
    
    Returns:
        Dict con estadísticas de rachas verificadas
    """
    print(f"[ADMIN] Starting streak verification at {datetime.now()}")
    
    # Get all gamification profiles with active streaks
    profiles = roble_client.read_table("pine_user_gamification", {})
    
    total_users = len(profiles)
    broken_streaks = 0
    active_streaks = 0
    errors = []
    
    for profile in profiles:
        user_ref = profile.get('user_ref')
        racha_dias = profile.get('racha_dias', 0)
        pp_dia = profile.get('pp_dia', 0)
        
        # Skip users without active streaks
        if racha_dias == 0:
            continue
        
        # If user has streak but didn't play today (pp_dia == 0)
        # This means they haven't played since the daily reset
        if pp_dia == 0:
            try:
                # Reset streak
                await gp.actualizar_racha(user_ref, incrementar=False)
                broken_streaks += 1
                print(f"[INFO] Broke streak for user {user_ref} (was {racha_dias} days)")
            except Exception as e:
                errors.append({
                    'user_ref': user_ref,
                    'error': str(e)
                })
                print(f"[ERROR] Failed to reset streak for user {user_ref}: {e}")
        else:
            # User still has active streak
            active_streaks += 1
    
    result = {
        'task': 'verificar_rachas',
        'timestamp': datetime.now().isoformat(),
        'total_users': total_users,
        'broken_streaks': broken_streaks,
        'active_streaks': active_streaks,
        'errors_count': len(errors),
        'errors': errors[:10]
    }
    
    print(f"[ADMIN] Streak verification complete: {broken_streaks} broken, {active_streaks} active")
    
    return result


# ======================================================================================
# TAREA COMBINADA DIARIA
# ======================================================================================

async def tarea_diaria_completa() -> Dict:
    """
    Ejecuta todas las tareas diarias en orden.
    
    Orden:
    1. Reset de PP diario
    2. Verificación de rachas rotas
    
    Esta función debe ser llamada por un cron job diario a medianoche.
    
    Returns:
        Dict con resultados de todas las tareas
    """
    print(f"[ADMIN] ========== STARTING DAILY TASKS ==========")
    
    # Task 1: Reset PP
    reset_pp_result = await reset_pp_dia_todos_usuarios()
    
    # Task 2: Verify streaks
    rachas_result = await verificar_rachas_rotas()
    
    result = {
        'task_type': 'daily_complete',
        'timestamp': datetime.now().isoformat(),
        'reset_pp': reset_pp_result,
        'verify_streaks': rachas_result
    }
    
    print(f"[ADMIN] ========== DAILY TASKS COMPLETE ==========")
    
    return result


# ======================================================================================
# UTILIDADES DE INFORMACIÓN
# ======================================================================================

def obtener_info_tareas() -> Dict:
    """
    Retorna información sobre las tareas programadas.
    
    Returns:
        Dict con info de cada tarea
    """
    return {
        'tareas_diarias': {
            'reset_pp_dia': {
                'descripcion': 'Resetea pp_dia a 0 para todos los usuarios',
                'frecuencia': 'Diaria',
                'hora_recomendada': '00:00 (medianoche)',
                'funcion': 'reset_pp_dia_todos_usuarios()'
            },
            'verificar_rachas': {
                'descripcion': 'Verifica y rompe rachas de usuarios inactivos',
                'frecuencia': 'Diaria',
                'hora_recomendada': '00:05 (después del reset PP)',
                'funcion': 'verificar_rachas_rotas()'
            },
            'tarea_completa': {
                'descripcion': 'Ejecuta reset_pp + verificar_rachas',
                'frecuencia': 'Diaria',
                'hora_recomendada': '00:00 (medianoche)',
                'funcion': 'tarea_diaria_completa()'
            }
        },
        'tareas_semanales': {
            'reset_semana': {
                'descripcion': 'Resetea pp_semana y pd_semana a 0',
                'frecuencia': 'Semanal',
                'dia_recomendado': 'Lunes',
                'hora_recomendada': '00:00 (medianoche)',
                'funcion': 'reset_semana_todos_usuarios()'
            }
        },
        'nota': 'Use cron jobs o Windows Task Scheduler para automatizar'
    }


# ======================================================================================
# SCRIPTS DE LÍNEA DE COMANDOS
# ======================================================================================

async def main():
    """
    Función principal para ejecutar desde línea de comandos.
    
    Uso:
        python gamification_admin.py
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python gamification_admin.py <tarea>")
        print("\nTareas disponibles:")
        print("  daily       - Ejecuta tareas diarias (reset PP + rachas)")
        print("  weekly      - Ejecuta reset semanal")
        print("  reset-pp    - Solo reset PP diario")
        print("  check-streaks - Solo verifica rachas")
        print("  info        - Muestra info de tareas")
        return
    
    tarea = sys.argv[1].lower()
    
    if tarea == 'daily':
        result = await tarea_diaria_completa()
        print(f"\nResultado: {result}")
    
    elif tarea == 'weekly':
        result = await reset_semana_todos_usuarios()
        print(f"\nResultado: {result}")
    
    elif tarea == 'reset-pp':
        result = await reset_pp_dia_todos_usuarios()
        print(f"\nResultado: {result}")
    
    elif tarea == 'check-streaks':
        result = await verificar_rachas_rotas()
        print(f"\nResultado: {result}")
    
    elif tarea == 'info':
        info = obtener_info_tareas()
        import json
        print(json.dumps(info, indent=2))
    
    else:
        print(f"Tarea desconocida: {tarea}")
        print("Use 'python gamification_admin.py' sin argumentos para ver ayuda")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
