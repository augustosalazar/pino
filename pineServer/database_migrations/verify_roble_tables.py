#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar todas las tablas de la base de datos Roble
Usando la API de Roble (no conexión directa PostgreSQL)
Incluye prueba de escritura y lectura con campos viejos + nuevos
"""

import os
import sys
import json
import requests
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Intentar cargar dotenv
try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv no esta instalado")
    print("Instala con: pip install python-dotenv")
    sys.exit(1)

# Cargar variables de entorno desde el directorio padre (pineServer/.env)
current_dir = Path(__file__).parent
env_path = current_dir.parent / '.env'
load_dotenv(dotenv_path=env_path)

class RobleVerifier:
    def __init__(self):
        self.project_id = os.getenv("ROBLE_PROJECT_ID")
        self.base_url = os.getenv("ROBLE_BASE_URL", "https://roble-api.openlab.uninorte.edu.co")
        self.admin_email = os.getenv("ADMIN_EMAIL")
        self.admin_password = os.getenv("ADMIN_PASSWORD")
        
        if not all([self.project_id, self.admin_email, self.admin_password]):
            print("[ERROR] Faltan variables de entorno en .env")
            sys.exit(1)
        
        self.auth_url = f"{self.base_url}/auth/{self.project_id}".rstrip('/')
        self.db_url = f"{self.base_url}/database/{self.project_id}"
        self.session = requests.Session()
        self.access_token: Optional[str] = None

    def login(self):
        """Autenticarse con Roble"""
        print("[*] Autenticando...")
        url = f"{self.auth_url}/login"
        try:
            response = self.session.post(url, json={
                "email": self.admin_email,
                "password": self.admin_password
            })
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("accessToken")
            self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
            print("[OK] Autenticado exitosamente")
        except Exception as e:
            print(f"[ERROR] Fallo la autenticacion: {e}")
            sys.exit(1)

    def check_table_exists(self, table_name: str) -> Dict[str, Any]:
        """Verifica si una tabla existe intentando leerla"""
        url = f"{self.db_url}/read"
        params = {"tableName": table_name}
        
        try:
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return {
                        "exists": True, 
                        "count": len(data),
                        "sample": data[0] if data else None
                    }
                return {"exists": False, "error": "Formato inesperado"}
            elif response.status_code == 404:
                return {"exists": False, "error": "404 Not Found"}
            elif response.status_code == 400:
                return {"exists": False, "error": response.text}
            else:
                return {"exists": False, "error": f"Status {response.status_code}"}
                
        except Exception as e:
            return {"exists": False, "error": str(e)}

    def insert_record(self, table_name: str, record: Dict) -> Dict:
        """Inserta un registro"""
        url = f"{self.db_url}/insert"
        payload = {
            "tableName": table_name,
            "records": [record]
        }
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def delete_record(self, table_name: str, record_id: str) -> bool:
        """Elimina un registro por _id"""
        url = f"{self.db_url}/delete"
        payload = {
            "tableName": table_name,
            "idColumn": "_id",
            "idValue": record_id
        }
        response = self.session.delete(url, json=payload)
        return response.status_code == 200

    def test_write_read(self, table_name: str, sample_data: Dict) -> bool:
        """Prueba escritura y lectura completa"""
        print(f"\nProbando escritura/lectura en {table_name}...")
        
        try:
            # 1. Insertar
            print("  [>] Insertando registro de prueba...")
            result = self.insert_record(table_name, sample_data)
            
            # Debug: imprimir respuesta completa si falla o si no hay IDs
            if not result.get("inserted") or not result.get("insertedIds"):
                print(f"  [DEBUG] Respuesta de inserción: {json.dumps(result, indent=2)}")
            
            if not result.get("inserted"):
                print(f"  [X] Falló inserción")
                return False
                
            # Intentar obtener ID de insertedIds o del objeto insertado
            inserted_ids = result.get("insertedIds", [])
            if inserted_ids:
                record_id = inserted_ids[0]
            elif result.get("inserted") and "_id" in result["inserted"][0]:
                record_id = result["inserted"][0]["_id"]
            else:
                print("  [X] No se devolvió ID insertado")
                return False
                
            print(f"  [OK] Insertado con ID: {record_id}")
            
            # 2. Leer y verificar campos
            print("  [>] Leyendo registro...")
            url = f"{self.db_url}/read"
            params = {"tableName": table_name, "_id": record_id}
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                print(f"  [X] Falló lectura: {response.status_code}")
                return False
                
            records = response.json()
            if not records:
                print("  [X] Registro no encontrado")
                return False
                
            read_record = records[0]
            
            # Verificar que todos los campos enviados están presentes
            missing_fields = []
            for key in sample_data.keys():
                if key not in read_record:
                    missing_fields.append(key)
            
            if missing_fields:
                print(f"  [X] Faltan campos en lectura: {', '.join(missing_fields)}")
                # Limpiar
                self.delete_record(table_name, record_id)
                return False
            
            print(f"  [OK] Todos los campos ({len(sample_data)}) verificados correctamente")
            
            # 3. Limpiar
            print("  [>] Limpiando registro de prueba...")
            self.delete_record(table_name, record_id)
            print("  [OK] Limpieza completada")
            
            return True
            
        except Exception as e:
            print(f"  [X] Excepción: {e}")
            return False

def main():
    print("=" * 80)
    print("  VERIFICACION INTEGRAL DE TABLAS ROBLE")
    print("  (Existencia + Escritura/Lectura de Campos Viejos y Nuevos)")
    print("=" * 80)
    print()

    verifier = RobleVerifier()
    verifier.login()
    print()

    # Definición de datos de prueba con campos VIEJOS + NUEVOS
    test_data = {
        # Tabla existente extendida
        'pine_exercise_sessions': {
            # Campos Viejos (PineServer original)
            'user_ref': '123', # Probando con string numérico
            'started_at': datetime.now().isoformat(),
            'completed_at': datetime.now().isoformat(),
            'total_exercises': 10,
            'correct_answers': 8,
            'avg_difficulty': 2,
            'total_time_ms': 120000,
            'score_earned': 80,
            'model_ref': 'default_model',
            
            # Campos Nuevos (Migración 002)
            'pp_ganados': 0,
            'pd_ganados': 0,
            'xp_ganados': 0,
            'bonus_batch_pd': 0,
            'bonus_racha_pd': 0,
            'bonus_levelup_pd': 0,
            'session_type': 'normal',
            'total_items': 10,
            'items_correctos_primer_intento': 0,
            'items_correctos_reintento': 0,
            'items_fallados': 0,
            'tiempo_promedio_segundos': 0,
            'miniboss_exito': False,
            'miniboss_tiempo_total': 0,
            'miniboss_aciertos': 0,
            'miniboss_reintentos': 0
        },
        
        # Tabla existente extendida
        'pine_exercises': {
            # Campos Viejos
            'session_ref': 'TEST_SESSION_REF',
            'user_ref': 'TEST_USER_VERIFY',
            'exercise_type': 1,  # Cambiado a int (smallint esperado)
            'operator': '+',
            'operand_1': 5,
            'operand_2': 3,
            'correct_answer': 8,
            'user_answer': 8,
            'options': json.dumps([8, 9, 7, 6]), # Stringify JSON
            'difficulty_level': 1, # Cambiado a int
            'is_correct': True,
            'time_taken_ms': 5000,
            'presented_at': datetime.now().isoformat(),
            'answered_at': datetime.now().isoformat(),
            
            # Campos Nuevos (Migración 003)
            'fue_primer_intento': True,
            'requirio_reintento': False,
            'reintento_exitoso': None,
            'pp_ganados': 1,
            'pd_ganados': 1,
            'operacion': 'suma',
            'debe_repetirse': False,
            'repeticion_programada': False
        },
        
        # Tabla Nueva (Migración 001)
        'pine_user_gamification': {
            'user_ref': 'TEST_USER_VERIFY',
            'pp_total': 0,
            'pp_dia': 0,
            'pp_semana': 0,
            'pp_dia_max': 0,
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
        },
        
        # Tabla Nueva (Migración 001)
        'pine_user_operations': {
            'user_ref': 'TEST_USER_VERIFY',
            'operacion': 'suma',
            'pd_operacion': 50,
            'nivel_dominio': 2,
            'unlocked': True,
            'miniboss_completed': False,
            'miniboss_attempts': 0,
            'total_ejercicios': 20,
            'total_correctos': 18,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        
        # Tabla Nueva (Migración 004)
        'pine_pending_items': {
            'user_ref': 'TEST_USER_VERIFY',
            'exercise_ref': 'TEST_EXERCISE_REF',
            'operacion': 'suma',
            'dificultad': 1, # Cambiado a int
            'intentos_fallidos': 1,
            'fecha_primer_fallo': datetime.now().isoformat(),
            'fecha_ultimo_fallo': datetime.now().isoformat(),
            'mostrado_nuevamente': False,
            'completado': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    }

    # Ejecutar pruebas
    success_count = 0
    total_tests = len(test_data)
    
    for table, data in test_data.items():
        # Primero verificar existencia
        exists_info = verifier.check_table_exists(table)
        status = "[EXISTE]" if exists_info["exists"] else "[NO EXISTE]"
        print(f"\nTabla: {table} {status}")
        
        if exists_info["exists"]:
            # Probar escritura/lectura
            if verifier.test_write_read(table, data):
                success_count += 1
        else:
            print(f"  [SKIP] No se puede probar escritura porque la tabla no existe")

    print("\n" + "=" * 80)
    print("RESUMEN FINAL DE PRUEBAS:")
    print(f"  Total tablas probadas: {total_tests}")
    print(f"  Exitosas: {success_count}")
    print(f"  Fallidas: {total_tests - success_count}")
    print("=" * 80)

if __name__ == "__main__":
    main()
