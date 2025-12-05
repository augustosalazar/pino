"""
Limpiar el registro de prueba y dejar que la inicialización pueble la tabla
"""

import sys
sys.path.append('pineServer')

from roble_client import roble_client

print("Limpiando registros de prueba de pine_configuracion_sistema...")
print()

try:
    # Leer todos los registros
    records = roble_client.read_table("pine_configuracion_sistema", {})
    
    if not records:
        print("✅ Tabla ya está vacía")
    else:
        print(f"Encontrados {len(records)} registros. Eliminando...")
        
        for rec in records:
            rec_id = rec.get("_id")
            key = rec.get("config_key")
            print(f"  Eliminando: {key} (ID: {rec_id})")
            
            try:
                roble_client._delete_record("pine_configuracion_sistema", rec_id)
            except Exception as e:
                print(f"    Error: {e}")
        
        print("\n✅ Limpieza completada")
        
        # Verificar
        remaining = roble_client.read_table("pine_configuracion_sistema", {})
        print(f"Registros restantes: {len(remaining) if remaining else 0}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
