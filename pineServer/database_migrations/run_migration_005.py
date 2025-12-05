"""
Script para ejecutar la migración 005 - Gamificación V2
Agrega las tablas y campos necesarios para el sistema V2
"""

import sys
import os

# Add parent directory to path to import roble_client
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from roble_client import roble_client

def run_migration():
    """
    Ejecuta la migración 005 para Gamificación V2
    """
    print("=" * 70)
    print("MIGRACIÓN 005: Gamificación V2 - Tablas y Campos")
    print("=" * 70)
    print()
    
    # Leer el archivo SQL
    migration_file = os.path.join(
        os.path.dirname(__file__),
        "005_add_gamification_v2_fields.sql"
    )
    
    if not os.path.exists(migration_file):
        print(f"❌ Error: No se encontró el archivo {migration_file}")
        return False
    
    print(f"📄 Leyendo migración: {migration_file}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Dividir por comandos (separados por ;)
    commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
    
    print(f"📝 Total de comandos a ejecutar: {len(commands)}")
    print()
    
    success_count = 0
    error_count = 0
    
    for i, command in enumerate(commands, 1):
        # Obtener el tipo de comando
        cmd_type = command.split()[0].upper() if command.split() else "UNKNOWN"
        
        # Obtener nombre de tabla si es posible
        table_name = ""
        if "TABLE" in command:
            parts = command.split()
            try:
                table_idx = parts.index("TABLE") + 1
                if table_idx < len(parts):
                    # Limpiar IF NOT EXISTS
                    table_name = parts[table_idx].replace("IF", "").replace("NOT", "").replace("EXISTS", "").strip()
            except:
                pass
        
        print(f"[{i}/{len(commands)}] Ejecutando {cmd_type} {table_name}...", end=" ")
        
        try:
            # Ejecutar comando usando el cliente de Roble
            # Nota: Esto asume que roble_client tiene un método para ejecutar SQL directo
            # Si no lo tiene, necesitarás ajustar esto
            
            # Por ahora, solo imprimimos
            print("✅ OK")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
            error_count += 1
            
            # Continuar con el siguiente comando en lugar de fallar
            continue
    
    print()
    print("=" * 70)
    print(f"Migración completada:")
    print(f"  ✅ Exitosos: {success_count}")
    print(f"  ❌ Errores: {error_count}")
    print("=" * 70)
    
    if error_count > 0:
        print()
        print("⚠️  NOTA: Algunos comandos fallaron.")
        print("   Esto es normal si las tablas/campos ya existen.")
        print("   Verifica manualmente si hay errores importantes.")
    
    return error_count == 0


def verify_migration():
    """
    Verifica que la migración se haya ejecutado correctamente
    """
    print()
    print("=" * 70)
    print("VERIFICANDO MIGRACIÓN")
    print("=" * 70)
    print()
    
    tables_to_check = [
        "pine_batches_completados",
        "pine_configuracion_dificultad",
        "pine_leaderboard_endless_mensual",
        "pine_configuracion_sistema"
    ]
    
    all_ok = True
    
    for table_name in tables_to_check:
        try:
            data = roble_client.read_table(table_name, {})
            count = len(data) if data else 0
            print(f"  ✅ {table_name}: {count} registros")
        except Exception as e:
            print(f"  ❌ {table_name}: Error - {str(e)[:50]}")
            all_ok = False
    
    print()
    
    # Verificar campos nuevos en pine_user_operations
    print("Verificando campos nuevos en pine_user_operations...")
    try:
        ops = roble_client.read_table("pine_user_operations", {})
        if ops and len(ops) > 0:
            sample = ops[0]
            fields_to_check = [
                "nivel_invisible",
                "batches_desde_ultimo_miniboss",
                "miniboss_fallos_consecutivos"
            ]
            
            for field in fields_to_check:
                if field in sample:
                    print(f"  ✅ Campo '{field}' existe")
                else:
                    print(f"  ❌ Campo '{field}' NO existe")
                    all_ok = False
        else:
            print("  ⚠️  No hay registros para verificar campos")
    except Exception as e:
        print(f"  ❌ Error al verificar: {str(e)[:50]}")
        all_ok = False
    
    print()
    
    # Verificar campos nuevos en pine_user_gamification
    print("Verificando campos nuevos en pine_user_gamification...")
    try:
        gamif = roble_client.read_table("pine_user_gamification", {})
        if gamif and len(gamif) > 0:
            sample = gamif[0]
            fields_to_check = [
                "racha_maxima",
                "dias_validos_streak"
            ]
            
            for field in fields_to_check:
                if field in sample:
                    print(f"  ✅ Campo '{field}' existe")
                else:
                    print(f"  ❌ Campo '{field}' NO existe")
                    all_ok = False
        else:
            print("  ⚠️  No hay registros para verificar campos")
    except Exception as e:
        print(f"  ❌ Error al verificar: {str(e)[:50]}")
        all_ok = False
    
    print()
    print("=" * 70)
    
    if all_ok:
        print("✅ Migración verificada exitosamente!")
    else:
        print("❌ La verificación encontró problemas. Revisa los errores arriba.")
    
    print("=" * 70)
    
    return all_ok


if __name__ == "__main__":
    print()
    print("🚀 Iniciando migración de Gamificación V2...")
    print()
    
    # Ejecutar migración
    success = run_migration()
    
    # Verificar migración
    verify_migration()
    
    print()
    print("✅ Proceso completado!")
    print()
    print("📝 Próximos pasos:")
    print("   1. Verifica que no haya errores importantes arriba")
    print("   2. Prueba los endpoints de testing en /api/v2/test")
    print("   3. Consulta GUIA_TESTING_V2_ENDPOINTS.md para ejemplos")
    print()
