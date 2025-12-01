"""
Gamification Core - Cálculos puros del sistema de gamificación

Este módulo contiene todas las fórmulas y cálculos del sistema de gamificación
sin dependencias de base de datos. Son funciones puras que se pueden testear fácilmente.
"""

from typing import Dict, Tuple
import math

# ======================================================================================
# CONSTANTES DEL SISTEMA
# ======================================================================================

# Puntos de Práctica (PP)
PP_DIA_MAX = 30  # Límite diario de PP

# Puntos de Dominio (PD)
# Rangos para niveles de dominio por operación
RANGOS_NIVEL_DOMINIO = [
    (0, 19, 1),      # Nivel 1: Básico
    (20, 49, 2),     # Nivel 2: Intermedio
    (50, 89, 3),     # Nivel 3: Avanzado
    (90, 139, 4),    # Nivel 4: Experto
    (140, float('inf'), 5)  # Nivel 5: Maestro
]

# PD por ejercicio
PD_CORRECTO_PRIMER_INTENTO = 2
PD_CORRECTO_REINTENTO = 1
PD_INCORRECTO = 0

# Bonificaciones de PD por batch
PD_BONUS_90_PORCIENTO = 5
PD_BONUS_70_PORCIENTO = 3
PD_BONUS_RACHA_DIARIA = 3

# Desbloqueo de operaciones
DESBLOQUEO_RESTA = {
    'pd_global_min': 30,
    'pd_suma_min': 20,
    'requiere_minijefe': True
}

DESBLOQUEO_MULT = {
    'pd_global_min': 70,
    'pd_resta_min': 20,
    'requiere_minijefe': True
}

DESBLOQUEO_DIV = {
    'pd_global_min': 100,
    'pd_mult_min': 20,
    'requiere_minijefe': True
}

# Desbloqueo de modos de juego
DESBLOQUEO_MIX_SUMA_RESTA = {'nivel_suma_min': 2, 'nivel_resta_min': 2}
DESBLOQUEO_MIX_MULT_DIV = {'nivel_mult_min': 2, 'nivel_div_min': 2}
DESBLOQUEO_SPEED = {'operaciones_nivel_3_min': 2}
DESBLOQUEO_BOSSES = {'operaciones_nivel_4_min': 2}
DESBLOQUEO_ELITE = {'operaciones_nivel_5_min': 1}
DESBLOQUEO_MASTER = {'todas_operaciones_nivel_min': 3}

# XP y Niveles de Jugador
XP_BASE_CORRECTO = 3
XP_MULTIPLICADOR_DIFICULTAD = 0.5
XP_EXPONENTE_NIVEL = 1.5
XP_BASE_NIVEL = 50

# Recompensa de PD por subir de nivel
PD_LEVELUP_MULTIPLICADOR = 20


# ======================================================================================
# FUNCIONES DE CÁLCULO DE PD (Puntos de Dominio)
# ======================================================================================

def calcular_pd_ejercicio(fue_primer_intento: bool, es_correcto: bool) -> int:
    """
    Calcula los PD ganados por un ejercicio individual.
    
    Args:
        fue_primer_intento: True si es el primer intento del ejercicio
        es_correcto: True si la respuesta fue correcta
    
    Returns:
        PD ganados (0, 1, o 2)
    """
    if not es_correcto:
        return PD_INCORRECTO
    
    if fue_primer_intento:
        return PD_CORRECTO_PRIMER_INTENTO
    else:
        return PD_CORRECTO_REINTENTO


def calcular_bonus_batch(porcentaje_acierto: float) -> int:
    """
    Calcula el bonus de PD por rendimiento en el batch.
    
    Args:
        porcentaje_acierto: Porcentaje de aciertos (0.0 a 1.0)
    
    Returns:
        Bonus de PD (0, 3, o 5)
    """
    if porcentaje_acierto >= 0.9:
        return PD_BONUS_90_PORCIENTO
    elif porcentaje_acierto >= 0.7:
        return PD_BONUS_70_PORCIENTO
    else:
        return 0


def calcular_nivel_dominio(pd_operacion: int) -> int:
    """
    Calcula el nivel de dominio (1-5) basado en los PD de una operación.
    
    Args:
        pd_operacion: PD acumulados en la operación
    
    Returns:
        Nivel de dominio (1-5)
    """
    for minimo, maximo, nivel in RANGOS_NIVEL_DOMINIO:
        if minimo <= pd_operacion <= maximo:
            return nivel
    
    # Si no está en ningún rango (no debería pasar), nivel 1
    return 1


# ======================================================================================
# FUNCIONES DE CÁLCULO DE XP Y NIVELES DE JUGADOR
# ======================================================================================

def calcular_xp_batch(correctos: int, dificultad_media: float) -> int:
    """
    Calcula la XP ganada en un batch.
    
    Fórmula: XP = C * (3 + 0.5 * d̄)
    
    Args:
        correctos: Número de ejercicios correctos en el batch
        dificultad_media: Dificultad media del batch (escala 1-5)
    
    Returns:
        XP ganada (entero)
    """
    xp = correctos * (XP_BASE_CORRECTO + XP_MULTIPLICADOR_DIFICULTAD * dificultad_media)
    return int(xp)


def calcular_xp_requerido_nivel(nivel: int) -> int:
    """
    Calcula la XP total requerida para alcanzar un nivel.
    
    Fórmula: XP_requerido(L) = 50 * L^1.5
    
    Args:
        nivel: Nivel objetivo
    
    Returns:
        XP total requerida
    """
    return int(XP_BASE_NIVEL * math.pow(nivel, XP_EXPONENTE_NIVEL))


def calcular_nivel_jugador(xp_total: int) -> int:
    """
    Calcula el nivel de jugador actual basado en XP total.
    
    Args:
        xp_total: XP total acumulada del jugador
    
    Returns:
        Nivel de jugador actual
    """
    nivel = 1
    while xp_total >= calcular_xp_requerido_nivel(nivel + 1):
        nivel += 1
    return nivel


def calcular_pd_levelup(nivel_alcanzado: int) -> int:
    """
    Calcula la recompensa de PD por subir a un nivel.
    
    Fórmula: PD_levelup = 20 * L
    
    Args:
        nivel_alcanzado: Nivel al que se subió
    
    Returns:
        PD de recompensa
    """
    return PD_LEVELUP_MULTIPLICADOR * nivel_alcanzado


def verificar_levelup(xp_anterior: int, xp_nueva: int) -> Tuple[bool, int, int]:
    """
    Verifica si hubo un level up y calcula la recompensa.
    
    Args:
        xp_anterior: XP antes de la actualización
        xp_nueva: XP después de la actualización
    
    Returns:
        (hubo_levelup: bool, nivel_nuevo: int, pd_recompensa: int)
    """
    nivel_anterior = calcular_nivel_jugador(xp_anterior)
    nivel_nuevo = calcular_nivel_jugador(xp_nueva)
    
    if nivel_nuevo > nivel_anterior:
        pd_recompensa = sum(
            calcular_pd_levelup(nivel) 
            for nivel in range(nivel_anterior + 1, nivel_nuevo + 1)
        )
        return True, nivel_nuevo, pd_recompensa
    
    return False, nivel_nuevo, 0


# ======================================================================================
# FUNCIONES DE VALIDACIÓN DE DESBLOQUEOS
# ======================================================================================

def verificar_desbloqueo_resta(pd_global: int, pd_suma: int, minijefe_suma_completado: bool) -> bool:
    """
    Verifica si se cumplen las condiciones para desbloquear RESTA.
    
    Requisitos:
    - PD_global >= 30
    - PD_suma >= 20 (Nivel 2)
    - Mini-jefe de SUMA completado
    """
    return (
        pd_global >= DESBLOQUEO_RESTA['pd_global_min'] and
        pd_suma >= DESBLOQUEO_RESTA['pd_suma_min'] and
        minijefe_suma_completado
    )


def verificar_desbloqueo_mult(pd_global: int, pd_resta: int, minijefe_mult_completado: bool) -> bool:
    """
    Verifica si se cumplen las condiciones para desbloquear MULTIPLICACIÓN.
    
    Requisitos:
    - PD_global >= 70
    - PD_resta >= 20 (Nivel 2)
    - Mini-jefe de MULTIPLICACIÓN completado
    """
    return (
        pd_global >= DESBLOQUEO_MULT['pd_global_min'] and
        pd_resta >= DESBLOQUEO_MULT['pd_resta_min'] and
        minijefe_mult_completado
    )


def verificar_desbloqueo_div(pd_global: int, pd_mult: int, minijefe_div_completado: bool) -> bool:
    """
    Verifica si se cumplen las condiciones para desbloquear DIVISIÓN.
    
    Requisitos:
    - PD_global >= 100
    - PD_mult >= 20 (Nivel 2)
    - Mini-jefe de DIVISIÓN completado
    """
    return (
        pd_global >= DESBLOQUEO_DIV['pd_global_min'] and
        pd_mult >= DESBLOQUEO_DIV['pd_mult_min'] and
        minijefe_div_completado
    )


def verificar_desbloqueos_modos(
    nivel_suma: int,
    nivel_resta: int,
    nivel_mult: int,
    nivel_div: int
) -> Dict[str, bool]:
    """
    Verifica qué modos de juego están desbloqueados.
    
    Args:
        nivel_suma, nivel_resta, nivel_mult, nivel_div: Niveles de dominio por operación
    
    Returns:
        Diccionario con flags de desbloqueo para cada modo
    """
    # Contar operaciones por nivel
    niveles = [nivel_suma, nivel_resta, nivel_mult, nivel_div]
    ops_nivel_3 = sum(1 for n in niveles if n >= 3)
    ops_nivel_4 = sum(1 for n in niveles if n >= 4)
    ops_nivel_5 = sum(1 for n in niveles if n >= 5)
    
    return {
        'mix_suma_resta': nivel_suma >= 2 and nivel_resta >= 2,
        'mix_mult_div': nivel_mult >= 2 and nivel_div >= 2,
        'speed': ops_nivel_3 >= 2,
        'bosses': ops_nivel_4 >= 2,
        'elite': ops_nivel_5 >= 1,
        'master': all(n >= 3 for n in niveles)
    }


# ======================================================================================
# FUNCIONES DE SCORE SEMANAL
# ======================================================================================

def calcular_score_semanal(pp_semana: int, pd_semana: int) -> float:
    """
    Calcula el score semanal para el leaderboard.
    
    Fórmula: Score_semanal = (PP_semana * 0.4) + (PD_semana * 0.6)
    
    Args:
        pp_semana: PP ganados en la semana
        pd_semana: PD ganados en la semana
    
    Returns:
        Score semanal
    """
    return (pp_semana * 0.4) + (pd_semana * 0.6)


# ======================================================================================
# FUNCIONES AUXILIARES
# ======================================================================================

def debe_repetirse_item(fue_primer_intento: bool, es_correcto_final: bool) -> bool:
    """
    Determina si un ítem debe añadirse a la cola de repetición.
    
    Según las reglas:
    - Si falla en el primer intento (independiente del reintento) → debe repetirse
    
    Args:
        fue_primer_intento: True si acertó en el primer intento
        es_correcto_final: True si el resultado final fue correcto
    
    Returns:
        True si debe repetirse
    """
    # Si NO fue primer intento (es decir, falló al menos una vez), debe repetirse
    return not fue_primer_intento
