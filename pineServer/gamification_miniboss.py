"""
Gamification Minibosses - Generación y validación de mini-jefes

Este módulo maneja la generación de batches especiales tipo "mini-jefe"
y la validación de completitud según criterios específicos.
"""

from typing import Dict, List, Tuple
from datetime import datetime
import random
from models import Exercise, ExerciseType, Operator


# ======================================================================================
# DEFINICIONES DE MINI-JEFES
# ======================================================================================

MINIBOSS_SUMA = {
    'operacion': 'suma',
    'nombre': 'Mini-jefe de SUMA',
    'descripcion': 'Desbloquea RESTA',
    'num_ejercicios': 15,
    'tiempo_limite_segundos': 60,
    'acierto_minimo': 0.70,  # 70%
    'permite_reintentos': False,
    'desbloquea': 'resta',
    'condiciones': {
        'operandos_max': 20,
        'operador': '+',
        'tipo': 'arithmetic'
    }
}

MINIBOSS_MULT = {
    'operacion': 'mult',
    'nombre': 'Mini-jefe de MULTIPLICACIÓN',
    'descripcion': 'Permite avanzar en multiplicación',
    'num_ejercicios': 12,
    'tiempo_limite_segundos': 90,
    'acierto_minimo': 0.80,  # 80%
    'permite_reintentos': False,
    'desbloquea': None,  # Ya está desbloqueado, es para práctica
    'condiciones': {
        'tablas_rango': (1, 6),  # tablas del 1 al 6
        'operador': '*',
        'tipo': 'arithmetic'
    }
}

MINIBOSS_DIV = {
    'operacion': 'div',
    'nombre': 'Mini-jefe de DIVISIÓN',
    'descripcion': 'Permite avanzar en división',
    'num_ejercicios': 10,
    'tiempo_limite_segundos': 120,
    'acierto_minimo': 0.75,  # 75%
    'permite_reintentos': False,
    'desbloquea': None,
    'condiciones': {
        'divisiones_exactas': True,
        'operador': '/',
        'tipo': 'arithmetic'
    }
}

# Mapa de mini-jefes
MINIBOSSES = {
    'suma': MINIBOSS_SUMA,
    'mult': MINIBOSS_MULT,
    'div': MINIBOSS_DIV
}


# ======================================================================================
# GENERACIÓN DE BATCHES DE MINI-JEFES
# ======================================================================================

def generar_batch_minijefe_suma() -> List[Exercise]:
    """
    Genera 15 sumas con operandos menores a 20.
    
    Returns:
        Lista de 15 ejercicios de suma
    """
    exercises = []
    
    for i in range(15):
        operand_1 = random.randint(1, 19)
        operand_2 = random.randint(1, 20 - operand_1)  # Asegurar que suma < 20
        
        correct_answer = operand_1 + operand_2
        
        # Generar distractores
        options = [correct_answer]
        while len(options) < 4:
            distractor = correct_answer + random.choice([-3, -2, -1, 1, 2, 3])
            if distractor > 0 and distractor not in options:
                options.append(distractor)
        
        random.shuffle(options)
        
        exercise = Exercise(
            exercise_type=ExerciseType.ARITHMETIC,
            operator=Operator.ADD,
            operand_1=operand_1,
            operand_2=operand_2,
            correct_answer=correct_answer,
            options=options,
            difficulty_level=1.5,
            user_answer=None,
            is_correct=False,
            time_taken_ms=0
        )
        
        exercises.append(exercise)
    
    return exercises


def generar_batch_minijefe_mult() -> List[Exercise]:
    """
    Genera 12 multiplicaciones de tablas 1-6.
    
    Returns:
        Lista de 12 ejercicios de multiplicación
    """
    exercises = []
    
    # Asegurar variedad de tablas
    tablas = list(range(1, 7)) * 2  # [1,2,3,4,5,6,1,2,3,4,5,6]
    random.shuffle(tablas)
    
    for i in range(12):
        operand_1 = tablas[i]
        operand_2 = random.randint(1, 10)
        
        correct_answer = operand_1 * operand_2
        
        # Generar distractores inteligentes
        options = [correct_answer]
        # Distractores: ±tabla, ±1
        posibles_distractores = [
            correct_answer + operand_1,
            correct_answer - operand_1,
            correct_answer + operand_2,
            correct_answer - operand_2,
            correct_answer + 1,
            correct_answer - 1
        ]
        
        for dist in posibles_distractores:
            if dist > 0 and dist not in options and len(options) < 4:
                options.append(dist)
        
        # Completar con aleatorios si es necesario
        while len(options) < 4:
            dist = correct_answer + random.choice([-5, -3, 3, 5])
            if dist > 0 and dist not in options:
                options.append(dist)
        
        random.shuffle(options)
        
        exercise = Exercise(
            exercise_type=ExerciseType.ARITHMETIC,
            operator=Operator.MULTIPLY,
            operand_1=operand_1,
            operand_2=operand_2,
            correct_answer=correct_answer,
            options=options,
            difficulty_level=2.0,
            user_answer=None,
            is_correct=False,
            time_taken_ms=0
        )
        
        exercises.append(exercise)
    
    return exercises


def generar_batch_minijefe_div() -> List[Exercise]:
    """
    Genera 10 divisiones exactas (sin residuo).
    
    Returns:
        Lista de 10 ejercicios de división
    """
    exercises = []
    
    for i in range(10):
        # Generar división exacta: resultado * divisor = dividendo
        resultado = random.randint(2, 12)
        divisor = random.randint(2, 10)
        dividendo = resultado * divisor
        
        correct_answer = resultado
        
        # Generar distractores
        options = [correct_answer]
        posibles_distractores = [
            correct_answer + 1,
            correct_answer - 1,
            correct_answer + 2,
            correct_answer - 2,
            divisor,  # Error común: confundir con el divisor
        ]
        
        for dist in posibles_distractores:
            if dist > 0 and dist not in options and len(options) < 4:
                options.append(dist)
        
        while len(options) < 4:
            dist = random.randint(max(1, correct_answer - 3), correct_answer + 3)
            if dist not in options:
                options.append(dist)
        
        random.shuffle(options)
        
        exercise = Exercise(
            exercise_type=ExerciseType.ARITHMETIC,
            operator=Operator.DIVIDE,
            operand_1=dividendo,
            operand_2=divisor,
            correct_answer=correct_answer,
            options=options,
            difficulty_level=2.5,
            user_answer=None,
            is_correct=False,
            time_taken_ms=0
        )
        
        exercises.append(exercise)
    
    return exercises


def generar_batch_minijefe(operacion: str) -> List[Exercise]:
    """
    Genera un batch de mini-jefe según la operación.
    
    Args:
        operacion: 'suma', 'mult', o 'div'
    
    Returns:
        Lista de ejercicios del mini-jefe
    
    Raises:
        ValueError: Si la operación no es válida
    """
    if operacion == 'suma':
        return generar_batch_minijefe_suma()
    elif operacion == 'mult':
        return generar_batch_minijefe_mult()
    elif operacion == 'div':
        return generar_batch_minijefe_div()
    else:
        raise ValueError(f"Operación de mini-jefe no válida: {operacion}")


# ======================================================================================
# VALIDACIÓN DE COMPLETITUD
# ======================================================================================

def validar_completitud_minijefe(
    operacion: str,
    ejercicios_resultados: List[Dict],
    tiempo_total_segundos: float
) -> Tuple[bool, Dict]:
    """
    Valida si un intento de mini-jefe cumple con los criterios de éxito.
    
    Args:
        operacion: Tipo de mini-jefe ('suma', 'mult', 'div')
        ejercicios_resultados: Lista de resultados con 'is_correct' y 'fue_primer_intento'
        tiempo_total_segundos: Tiempo total empleado
    
    Returns:
        (exito: bool, detalles: Dict)
    """
    if operacion not in MINIBOSSES:
        return False, {"error": f"Mini-jefe {operacion} no existe"}
    
    miniboss_config = MINIBOSSES[operacion]
    
    # Validar número de ejercicios
    num_ejercicios = len(ejercicios_resultados)
    if num_ejercicios != miniboss_config['num_ejercicios']:
        return False, {
            "error": f"Número incorrecto de ejercicios: {num_ejercicios}/{miniboss_config['num_ejercicios']}"
        }
    
    # Contar correctos
    correctos = sum(1 for e in ejercicios_resultados if e.get('is_correct', False))
    porcentaje_acierto = correctos / num_ejercicios if num_ejercicios > 0 else 0
    
    # Verificar porcentaje mínimo
    acierto_requerido = miniboss_config['acierto_minimo']
    cumple_acierto = porcentaje_acierto >= acierto_requerido
    
    # Verificar tiempo
    tiempo_limite = miniboss_config['tiempo_limite_segundos']
    cumple_tiempo = tiempo_total_segundos <= tiempo_limite
    
    # Verificar reintentos (si no se permiten)
    if not miniboss_config['permite_reintentos']:
        # Todos deben ser primer intento
        hubo_reintentos = any(not e.get('fue_primer_intento', True) for e in ejercicios_resultados)
        cumple_reintentos = not hubo_reintentos
    else:
        cumple_reintentos = True
    
    # Determinar éxito
    exito = cumple_acierto and cumple_tiempo and cumple_reintentos
    
    detalles = {
        "nombre": miniboss_config['nombre'],
        "exito": exito,
        "correctos": correctos,
        "total": num_ejercicios,
        "porcentaje_acierto": round(porcentaje_acierto * 100, 1),
        "acierto_requerido": round(acierto_requerido * 100, 1),
        "cumple_acierto": cumple_acierto,
        "tiempo_segundos": round(tiempo_total_segundos, 1),
        "tiempo_limite": tiempo_limite,
        "cumple_tiempo": cumple_tiempo,
        "cumple_reintentos": cumple_reintentos,
        "desbloquea": miniboss_config['desbloquea']
    }
    
    return exito, detalles


# ======================================================================================
# INFORMACIÓN DE MINI-JEFES
# ======================================================================================

def obtener_info_minijefe(operacion: str) -> Dict:
    """
    Obtiene la información de un mini-jefe.
    
    Args:
        operacion: Tipo de mini-jefe
    
    Returns:
        Dict con información del mini-jefe
    """
    if operacion not in MINIBOSSES:
        return {"error": f"Mini-jefe {operacion} no existe"}
    
    config = MINIBOSSES[operacion]
    
    return {
        "operacion": operacion,
        "nombre": config['nombre'],
        "descripcion": config['descripcion'],
        "num_ejercicios": config['num_ejercicios'],
        "tiempo_limite_segundos": config['tiempo_limite_segundos'],
        "acierto_minimo_porcentaje": config['acierto_minimo'] * 100,
        "permite_reintentos": config['permite_reintentos'],
        "desbloquea": config['desbloquea'],
        "condiciones": config['condiciones']
    }


def obtener_todos_minijefes() -> List[Dict]:
    """
    Obtiene información de todos los mini-jefes disponibles.
    
    Returns:
        Lista de info de mini-jefes
    """
    return [obtener_info_minijefe(op) for op in MINIBOSSES.keys()]


def puede_acceder_minijefe(operacion: str, perfil_usuario: Dict) -> Tuple[bool, str]:
    """
    Verifica si un usuario puede acceder a un mini-jefe.
    
    Args:
        operacion: Tipo de mini-jefe
        perfil_usuario: Perfil de gamificación del usuario
    
    Returns:
        (puede_acceder: bool, razon: str)
    """
    if operacion not in MINIBOSSES:
        return False, f"Mini-jefe {operacion} no existe"
    
    # SUMA: Siempre disponible
    if operacion == 'suma':
        return True, "Disponible"
    
    # MULT: Requiere RESTA desbloqueada
    if operacion == 'mult':
        # Buscar operación RESTA en las operaciones del perfil
        operaciones = perfil_usuario.get('operaciones', [])
        resta_op = next((op for op in operaciones if op['operacion'] == 'resta'), None)
        if resta_op and resta_op.get('unlocked'):
            return True, "Disponible"
        return False, "Requiere tener RESTA desbloqueada"
    
    # DIV: Requiere MULT desbloqueada
    if operacion == 'div':
        operaciones = perfil_usuario.get('operaciones', [])
        mult_op = next((op for op in operaciones if op['operacion'] == 'mult'), None)
        if mult_op and mult_op.get('unlocked'):
            return True, "Disponible"
        return False, "Requiere tener MULTIPLICACIÓN desbloqueada"
    
    return False, "Condiciones no cumplidas"
