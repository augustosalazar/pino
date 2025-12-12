"""
Gamification V2 - Initialization Module
Populates configuration tables on server startup if empty
"""

from datetime_utils import now_colombia, now_colombia_iso
from roble_client import roble_client
from datetime import datetime
import json  # ← Added


def initialize_system_config():
    """
    Initialize pine_configuracion_sistema with default values
    """
    print("[INIT] Checking pine_configuracion_sistema...")
    
    try:
        # Check if table has data
        existing = roble_client.read_table("pine_configuracion_sistema", {})
        
        if existing and len(existing) > 0:
            print(f"[INIT] ✅ pine_configuracion_sistema already has {len(existing)} records")
            return True
        
        print("[INIT] 📝 Populating pine_configuracion_sistema with default values...")
        
        # Default system configurations
        # NOTE: config_value must be JSON string for JSONB field
        # NOTE: Roble generates _id automatically, config_key is just a regular TEXT field
        configs = [
            {
                "config_key": "scoring.base_multiplier",
                "config_value": json.dumps({"value": 5, "type": "integer"}),
                "description": "Multiplicador base: C × (value + d̄)",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "scoring.participation_bonus",
                "config_value": json.dumps({"value": 10, "type": "integer"}),
                "description": "Bonus por completar batch",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "scoring.error_penalty",
                "config_value": json.dumps({"value": 2, "type": "integer"}),
                "description": "Penalización por error",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "streak.min_correct",
                "config_value": json.dumps({"value": 4, "type": "integer"}),
                "description": "Mínimo de aciertos para contar streak",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "streak.base_score",
                "config_value": json.dumps({"value": 5, "type": "integer"}),
                "description": "Puntos base de streak",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "streak.daily_multiplier",
                "config_value": json.dumps({"value": 3, "type": "integer"}),
                "description": "Multiplicador por día",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "streak.max_days",
                "config_value": json.dumps({"value": 30, "type": "integer"}),
                "description": "Días máximos de streak",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "practice_points.chest_interval",
                "config_value": json.dumps({"value": 100, "type": "integer"}),
                "description": "PP para abrir cofre",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "miniboss.min_batches_after_fail",
                "config_value": json.dumps({"value": 3, "type": "integer"}),
                "description": "Batches mínimos tras fallo",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "miniboss.min_correct_rate",
                "config_value": json.dumps({"value": 0.8, "type": "float"}),
                "description": "Tasa de aciertos mínima (80%)",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "miniboss.nivel_invisible_threshold",
                "config_value": json.dumps({"value": 0.5, "type": "float"}),
                "description": "Diferencia mínima de nivel",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "batch.size",
                "config_value": json.dumps({"value": 10, "type": "integer"}),
                "description": "Ejercicios por batch",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "batch.distribution_easy",
                "config_value": json.dumps({"value": 2, "type": "integer"}),
                "description": "Ejercicios fáciles",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "batch.distribution_central",
                "config_value": json.dumps({"value": 6, "type": "integer"}),
                "description": "Ejercicios centrales",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "config_key": "batch.distribution_hard",
                "config_value": json.dumps({"value": 2, "type": "integer"}),
                "description": "Ejercicios difíciles",
                "version": 1,
                "activa": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]
        
        # Insert all configs
        result = roble_client.insert_records("pine_configuracion_sistema", configs)
        
        if result and result.get("inserted"):
            count = len(result["inserted"])
            print(f"[INIT] ✅ Inserted {count} system configurations")
            return True
        else:
            # Check if it was skipped
            skipped = result.get("skipped", [])
            if skipped:
                print(f"[INIT] ⚠️  Warning: {len(skipped)} configs were skipped")
                for skip in skipped[:3]:  # Show first 3
                    print(f"       Reason: {skip.get('reason')}")
            return False
            
    except Exception as e:
        print(f"[INIT] ❌ Error initializing system config: {e}")
        import traceback
        traceback.print_exc()
        return False


def initialize_difficulty_config():
    """
    Initialize pine_configuracion_dificultad with default values
    """
    print("[INIT] Checking pine_configuracion_dificultad...")
    
    try:
        # Check if table has data
        existing = roble_client.read_table("pine_configuracion_dificultad", {})
        
        if existing and len(existing) > 0:
            print(f"[INIT] ✅ pine_configuracion_dificultad already has {len(existing)} records")
            return True
        
        print("[INIT] 📝 Populating pine_configuracion_dificultad with default values...")
        
        # Default difficulty configurations (4 operations × 5 levels = 20 configs)
        configs = [
            # SUMA
            {
                "operacion": "suma", "nivel": 1,
                "min_operando_1": 0, "max_operando_1": 10,
                "min_operando_2": 0, "max_operando_2": 10,
                "max_resultado": 20,
                "tipo_respuesta": "multiple_choice", "num_opciones": 4,
                "max_tiempo_segundos": 30, "dificultad_score": 1.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "suma", "nivel": 2,
                "min_operando_1": 10, "max_operando_1": 50,
                "min_operando_2": 10, "max_operando_2": 50,
                "max_resultado": 100,
                "tipo_respuesta": "multiple_choice", "num_opciones": 4,
                "max_tiempo_segundos": 45, "dificultad_score": 2.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "suma", "nivel": 3,
                "min_operando_1": 50, "max_operando_1": 200,
                "min_operando_2": 50, "max_operando_2": 200,
                "max_resultado": 400,
                "tipo_respuesta": "multiple_choice", "num_opciones": 4,
                "max_tiempo_segundos": 60, "dificultad_score": 3.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "suma", "nivel": 4,
                "min_operando_1": 100, "max_operando_1": 500,
                "min_operando_2": 100, "max_operando_2": 500,
                "max_resultado": 1000,
                "tipo_respuesta": "abierta", "num_opciones": None,
                "max_tiempo_segundos": 75, "dificultad_score": 4.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "suma", "nivel": 5,
                "min_operando_1": 500, "max_operando_1": 2000,
                "min_operando_2": 500, "max_operando_2": 2000,
                "max_resultado": 4000,
                "tipo_respuesta": "abierta", "num_opciones": None,
                "max_tiempo_segundos": 90, "dificultad_score": 5.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            
            # RESTA
            {
                "operacion": "resta", "nivel": 1,
                "min_operando_1": 0, "max_operando_1": 10,
                "min_operando_2": 0, "max_operando_2": 10,
                "max_resultado": 10,
                "tipo_respuesta": "multiple_choice", "num_opciones": 4,
                "max_tiempo_segundos": 30, "dificultad_score": 1.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "resta", "nivel": 2,
                "min_operando_1": 10, "max_operando_1": 50,
                "min_operando_2": 10, "max_operando_2": 50,
                "max_resultado": 50,
                "tipo_respuesta": "multiple_choice", "num_opciones": 4,
                "max_tiempo_segundos": 45, "dificultad_score": 2.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "resta", "nivel": 3,
                "min_operando_1": 50, "max_operando_1": 200,
                "min_operando_2": 50, "max_operando_2": 200,
                "max_resultado": 200,
                "tipo_respuesta": "multiple_choice", "num_opciones": 4,
                "max_tiempo_segundos": 60, "dificultad_score": 3.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "resta", "nivel": 4,
                "min_operando_1": 100, "max_operando_1": 500,
                "min_operando_2": 100, "max_operando_2": 500,
                "max_resultado": 500,
                "tipo_respuesta": "abierta", "num_opciones": None,
                "max_tiempo_segundos": 75, "dificultad_score": 4.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "resta", "nivel": 5,
                "min_operando_1": 500, "max_operando_1": 2000,
                "min_operando_2": 500, "max_operando_2": 2000,
                "max_resultado": 2000,
                "tipo_respuesta": "abierta", "num_opciones": None,
                "max_tiempo_segundos": 90, "dificultad_score": 5.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            
            # MULTIPLICACIÓN
            {
                "operacion": "mult", "nivel": 1,
                "min_operando_1": 0, "max_operando_1": 10,
                "min_operando_2": 0, "max_operando_2": 10,
                "max_resultado": 100,
                "tipo_respuesta": "multiple_choice", "num_opciones": 4,
                "max_tiempo_segundos": 30, "dificultad_score": 1.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "mult", "nivel": 2,
                "min_operando_1": 2, "max_operando_1": 12,
                "min_operando_2": 2, "max_operando_2": 12,
                "max_resultado": 144,
                "tipo_respuesta": "multiple_choice", "num_opciones": 4,
                "max_tiempo_segundos": 45, "dificultad_score": 2.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "mult", "nivel": 3,
                "min_operando_1": 10, "max_operando_1": 20,
                "min_operando_2": 10, "max_operando_2": 20,
                "max_resultado": 400,
                "tipo_respuesta": "multiple_choice", "num_opciones": 4,
                "max_tiempo_segundos": 60, "dificultad_score": 3.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "mult", "nivel": 4,
                "min_operando_1": 10, "max_operando_1": 50,
                "min_operando_2": 10, "max_operando_2": 50,
                "max_resultado": 2500,
                "tipo_respuesta": "abierta", "num_opciones": None,
                "max_tiempo_segundos": 75, "dificultad_score": 4.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "mult", "nivel": 5,
                "min_operando_1": 50, "max_operando_1": 100,
                "min_operando_2": 50, "max_operando_2": 100,
                "max_resultado": 10000,
                "tipo_respuesta": "abierta", "num_opciones": None,
                "max_tiempo_segundos": 90, "dificultad_score": 5.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            
            # DIVISIÓN
            {
                "operacion": "div", "nivel": 1,
                "min_operando_1": 2, "max_operando_1": 20,
                "min_operando_2": 2, "max_operando_2": 10,
                "max_resultado": 10,
                "tipo_respuesta": "multiple_choice", "num_opciones": 4,
                "max_tiempo_segundos": 30, "dificultad_score": 1.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "div", "nivel": 2,
                "min_operando_1": 10, "max_operando_1": 100,
                "min_operando_2": 2, "max_operando_2": 12,
                "max_resultado": 50,
                "tipo_respuesta": "multiple_choice", "num_opciones": 4,
                "max_tiempo_segundos": 45, "dificultad_score": 2.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "div", "nivel": 3,
                "min_operando_1": 50, "max_operando_1": 500,
                "min_operando_2": 5, "max_operando_2": 25,
                "max_resultado": 100,
                "tipo_respuesta": "multiple_choice", "num_opciones": 4,
                "max_tiempo_segundos": 60, "dificultad_score": 3.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "div", "nivel": 4,
                "min_operando_1": 100, "max_operando_1": 1000,
                "min_operando_2": 10, "max_operando_2": 50,
                "max_resultado": 100,
                "tipo_respuesta": "abierta", "num_opciones": None,
                "max_tiempo_segundos": 75, "dificultad_score": 4.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "operacion": "div", "nivel": 5,
                "min_operando_1": 500, "max_operando_1": 5000,
                "min_operando_2": 10, "max_operando_2": 100,
                "max_resultado": 500,
                "tipo_respuesta": "abierta", "num_opciones": None,
                "max_tiempo_segundos": 90, "dificultad_score": 5.0,
                "config_version": 1, "activa": True,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        # Insert all configs
        result = roble_client.insert_records("pine_configuracion_dificultad", configs)
        
        if result and result.get("inserted"):
            count = len(result["inserted"])
            print(f"[INIT] ✅ Inserted {count} difficulty configurations")
            return True
        else:
            print("[INIT] ⚠️  Warning: Could not insert difficulty configurations")
            return False
            
    except Exception as e:
        print(f"[INIT] ❌ Error initializing difficulty config: {e}")
        return False


def initialize_v2_data():
    """
    Main initialization function
    Called on server startup
    """
    print("\n" + "=" * 70)
    print("  GAMIFICATION V2 - INITIALIZATION")
    print("=" * 70)
    
    system_ok = initialize_system_config()
    difficulty_ok = initialize_difficulty_config()
    
    print("=" * 70)
    
    if system_ok and difficulty_ok:
        print("[INIT] ✅ All V2 configurations initialized successfully!")
        print(now_colombia_iso())
    else:
        print("[INIT] ⚠️  Some configurations could not be initialized")
        print("[INIT] ℹ️  Server will continue, but V2 features may not work properly")
    
    print("=" * 70 + "\n")
    
    return system_ok and difficulty_ok
