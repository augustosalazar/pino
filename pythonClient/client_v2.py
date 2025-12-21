"""
Cliente Interactivo de Prueba para Gamificación V2 (Consola)

Este script permite probar el flujo completo del nuevo motor de gamificación
desde la terminal, simulando la experiencia que tendrá el usuario en la app React Native.

Uso:
    Asegúrate de que el servidor esté corriendo con V2 habilitado:
    > set USE_GAMIFICATION_V2=true && python pineServer/main.py (o run_v2_tests.bat)
    
    Luego ejecuta este cliente:
    > python client_v2.py
"""

import requests
import time
import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Configuración
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# Colores para la consola
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Habilitar colores en Windows
if os.name == 'nt':
    os.system('color')

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f" {text}")
    print(f"{'='*60}{Colors.ENDC}")

def ensure_user(user_ref: str):
    """Asegura que el usuario exista y obtiene su perfil"""
    url = f"{BASE_URL}/api/users/ensure"
    payload = {
        "user_ref": user_ref,
        "email": f"{user_ref}@example.com",
        "username": user_ref
    }
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"{Colors.FAIL}Error creating/fetching user: {e}{Colors.ENDC}")
        return None

def start_session(user_ref: str, num_exercises: int = 10, batch_type: str = "regular"):
    """Inicia una nueva sesión de práctica
    
    Args:
        user_ref: Referencia del usuario
        num_exercises: Número de ejercicios en la sesión
        batch_type: Tipo de sesión ('regular', 'miniboss', o 'endless')
    """
    url = f"{BASE_URL}/api/sessions/start"
    payload = {
        "user_ref": user_ref,
        "num_exercises": num_exercises,
        "batch_type": batch_type
    }
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"{Colors.FAIL}Error starting session: {e}{Colors.ENDC}")
        if response.text:
            print(f"Server response: {response.text}")
        return None

def present_exercise(exercise: Dict, index: int, total: int) -> Dict:
    """Muestra un ejercicio y captura la respuesta"""
    op_map = {'ADDITION': '+', 'SUBTRACTION': '-', 'MULTIPLICATION': '*', 'DIVISION': '/'}
    # Support both legacy Enum strings and new V2 shorthand
    op_v2_map = {'suma': '+', 'resta': '-', 'mult': '*', 'div': '/'}
    
    op_symbol = op_map.get(exercise.get('operator'), exercise.get('operator'))
    if not op_symbol and 'operacion' in exercise: # V2 raw format fallback
        op_symbol = op_v2_map.get(exercise['operacion'], '?')
        
    problem_str = f"{exercise['operand_1']} {op_symbol or '?'} {exercise['operand_2']}"
    
    print(f"\n{Colors.CYAN}[{index}/{total}] {Colors.BOLD}{problem_str} = ?{Colors.ENDC}")
    
    # Manejar opciones si es multiple choice
    options = exercise.get('options')
    if options:
        print(f"Opciones: {options}")
    
    start_time = time.time()
    
    while True:
        try:
            user_input = input(f"{Colors.BLUE}Tu respuesta: {Colors.ENDC}")
            user_answer = float(user_input)
            break
        except ValueError:
            print("Por favor ingresa un número válido.")
    
    end_time = time.time()
    time_ms = int((end_time - start_time) * 1000)
    
    # Check correctness
    correct_answer = exercise.get('correct_answer')
    if correct_answer is None: correct_answer = exercise.get('respuesta_correcta')
    
    # Verificación laxa para flotantes
    is_correct = abs(user_answer - float(correct_answer)) < 0.01
    
    if is_correct:
        print(f"{Colors.GREEN}✓ ¡Correcto!{Colors.ENDC} ({time_ms/1000:.1f}s)")
    else:
        print(f"{Colors.FAIL}✗ Incorrecto. Era {correct_answer}{Colors.ENDC}")
        
    # Enriquecer objeto ejercicio con resultados
    exercise['user_answer'] = user_answer
    exercise['is_correct'] = is_correct
    exercise['time_taken_ms'] = time_ms
    
    # Asegurar campos requeridos por el backend complete_session
    if 'exercise_type' not in exercise:
        exercise['exercise_type'] = 'multiple_choice' if options else 'free_text'
        
    return exercise

def complete_session(session_id: str, resolved_exercises: List[Dict]):
    """Envía los resultados al servidor"""
    url = f"{BASE_URL}/api/sessions/{session_id}/complete"
    payload = {
        "exercises": resolved_exercises
    }
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"{Colors.FAIL}Error completing session: {e}{Colors.ENDC}")
        if response.text:
            print(f"Server response: {response.text}")
        return None

def main():
    print_header("CLIENTE DE PRUEBA GAMIFICACIÓN V2")
    
    # 1. Login
    user_ref = input("Ingresa tu ID de usuario (ej: test_user): ").strip()
    if not user_ref: user_ref = "test_user"
    
    print(f"\nConectando como: {user_ref}...")
    user_data = ensure_user(user_ref)
    
    if not user_data:
        return
        
    # Mostrar estado actual de gamificación si existe
    if 'gamification' in user_data:
        gamif = user_data['gamification']['perfil']
        print(gamif)
        print(f"{Colors.CYAN}Estado Actual:{Colors.ENDC}")
        print(f" - Nivel: {gamif.get('nivel_jugador', 1)}")
        print(f" - XP: {gamif.get('xp_total', 0)}")
        print(f" - Racha: {gamif.get('racha_dias', 0)} días")
        print(f" - PP Disponibles: {gamif.get('pp_total', 0)}")
    
    # 2. Select Game Mode
    print(f"\n{Colors.BOLD}Selecciona modo de juego:{Colors.ENDC}")
    print("1. Modo Regular (Práctica normal)")
    print("2. Modo Miniboss (Desafío especial)")
    print("3. Modo Endless (¡Practica hasta fallar!)")
    
    mode_choice = input(f"\n{Colors.BLUE}Selección (1-3, default=1): {Colors.ENDC}").strip()
    
    batch_type_map = {
        "1": "regular",
        "2": "miniboss",
        "3": "endless"
    }
    batch_type = batch_type_map.get(mode_choice, "regular")
    mode_names = {
        "regular": "Regular",
        "miniboss": "Miniboss",
        "endless": "Endless"
    }
    
    # 3. Start Session
    input(f"\n{Colors.BOLD}Modo: {mode_names[batch_type]}{Colors.ENDC}")
    input(f"Presiona ENTER para solicitar un batch de ejercicios...")
    
    # For endless mode, we generate batches dynamically
    num_exercises = 5 if batch_type == "endless" else 10
    session_data = start_session(user_ref, num_exercises, batch_type)
    
    if not session_data:
        return
        
    session_id = session_data['session_id']
    exercises = session_data['exercises']
    
    # Detectar modo
    profile = session_data.get('user_profile', {})
    is_miniboss = profile.get('is_miniboss')
    
    print(f"\n{Colors.GREEN}¡Sesión Iniciada!{Colors.ENDC}")
    print(f"ID: {session_id}")
    print(f"Ejercicios: {len(exercises)}")
    
    if batch_type == "endless":
        print(f"{Colors.WARNING}🎯 MODO ENDLESS ACTIVADO 🎯{Colors.ENDC}")
        print("¡Responde correctamente para continuar!")
        print("Se generarán ejercicios hasta que cometas un error...")
    elif is_miniboss:
        print(f"{Colors.WARNING}⚠️  MODO MINIBOSS ACTIVADO ⚠️{Colors.ENDC}")
        print("¡Este batch es crucial para subir de nivel!")
        
    # 4. Interactive Loop
    resolved_exercises = []
    endless_streak = 0
    
    for i, ex in enumerate(exercises):
        resolved = present_exercise(ex, i+1, len(exercises))
        resolved_exercises.append(resolved)
        
        # In endless mode, track streak and potentially continue
        if batch_type == "endless":
            if resolved.get('is_correct'):
                endless_streak += 1
                print(f"{Colors.GREEN}¡Racha: {endless_streak}! {Colors.ENDC}")
                # Request next exercise if there's more to do
                if i == len(exercises) - 1:
                    # Ask if user wants to continue
                    continue_choice = input(f"\n{Colors.BLUE}¿Deseas continuar? (s/n): {Colors.ENDC}").strip().lower()
                    if continue_choice == 's':
                        print("Obteniendo siguiente ejercicio...")
                        # In a real implementation, you'd request the next exercise
                        # For now, we'll just complete the session
                        pass
            else:
                print(f"{Colors.FAIL}¡Racha rota! Final: {endless_streak} ejercicios correctos.{Colors.ENDC}")
                break
        
    # 5. Complete Session
    print(f"\nEnviando resultados...")
    result_data = complete_session(session_id, resolved_exercises)
    
    if not result_data:
        print(f"{Colors.FAIL}El servidor no valoro la sesión.{Colors.ENDC}")
        return
        
    # 6. Show Results
    print_header("RESUMEN DE SESIÓN")
    
    score = result_data.get('score_earned', 0)
    correct = result_data.get('correct_answers', 0)
    total = result_data.get('total_exercises', 0)
    
    print(f"Aciertos: {correct}/{total}")
    print(f"Puntuación Base: {Colors.BOLD}{score}{Colors.ENDC}")
    
    # Show endless mode specific info
    if batch_type == "endless":
        endless_info = result_data.get('endless_info', {})
        streak = endless_info.get('streak', 0)
        best_streak = endless_info.get('best_streak', 0)
        print(f"\n{Colors.CYAN}📊 Estadísticas Endless:{Colors.ENDC}")
        print(f" - Racha Actual: {streak}")
        print(f" - Mejor Racha (este mes): {best_streak}")
    
    # Mostrar Gamificación V2 info
    if 'gamification' in result_data:
        g = result_data['gamification']
        rewards = g.get('recompensas', {})
        
        print(f"\n{Colors.WARNING}🏆 RECOMPENSAS V2 🏆{Colors.ENDC}")
        print(f" + {rewards.get('xp_ganada', 0)} XP")
        print(f" + {rewards.get('pp_ganados', 0)} Puntos de Práctica")
        print(f" + {rewards.get('pd', {}).get('total_pd_global', 0)} Puntos de Dominio")
        
        if g.get('level_up'):
             print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ¡HAS SUBIDO DE NIVEL DE DOMINIO! 🎉{Colors.ENDC}")
             
    # Mostrar ajustes de dificultad
    diff_adj = result_data.get('difficulty_adjustments', {})
    if diff_adj:
        print(f"\n{Colors.BLUE}Ajustes de Dificultad:{Colors.ENDC}")
        for op, adj in diff_adj.items():
            print(f" - {op}: {adj.get('old', '?')} -> {adj.get('new', '?')}")

    print("\n¡Prueba finalizada!")

if __name__ == "__main__":
    main()
