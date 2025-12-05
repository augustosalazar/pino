#!/usr/bin/env python3
"""
Test script for Gamification V2 endpoints
Tests new tables and modifications
"""

import requests
import json
from datetime import datetime

# Server configuration
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_health():
    """Test if server is responding"""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_verify_tables():
    """Test verification of V2 tables"""
    print_section("2. Verify V2 Tables")
    try:
        response = requests.get(f"{BASE_URL}/api/v2/test/verify/tables")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            
            tables = data.get('tables', {})
            
            # New tables
            new_tables = [
                "pine_batches_completados",
                "pine_configuracion_dificultad",
                "pine_leaderboard_endless_mensual",
                "pine_configuracion_sistema"
            ]
            
            print("\n📊 New Tables:")
            for table in new_tables:
                if table in tables:
                    info = tables[table]
                    exists = info.get('exists', False)
                    count = info.get('count', 0)
                    status = "✅" if exists else "❌"
                    print(f"  {status} {table}: {count} records")
                else:
                    print(f"  ❌ {table}: NOT FOUND")
            
            # Modified tables
            print("\n📝 Modified Tables (new fields):")
            
            # pine_user_operations
            if 'pine_user_operations' in tables:
                op_info = tables['pine_user_operations']
                fields = {
                    'nivel_invisible': op_info.get('has_nivel_invisible', False),
                    'batches_desde_ultimo_miniboss': op_info.get('has_batches_desde_ultimo_miniboss', False),
                    'miniboss_fallos_consecutivos': op_info.get('has_miniboss_fallos_consecutivos', False)
                }
                print(f"  pine_user_operations:")
                for field, exists in fields.items():
                    status = "✅" if exists else "❌"
                    print(f"    {status} {field}")
            
            # pine_user_gamification
            if 'pine_user_gamification' in tables:
                gam_info = tables['pine_user_gamification']
                fields = {
                    'racha_maxima': gam_info.get('has_racha_maxima', False),
                    'dias_validos_streak': gam_info.get('has_dias_validos_streak', False)
                }
                print(f"  pine_user_gamification:")
                for field, exists in fields.items():
                    status = "✅" if exists else "❌"
                    print(f"    {status} {field}")
            
            return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_system_config():
    """Test system configuration"""
    print_section("3. System Configuration")
    try:
        response = requests.get(f"{BASE_URL}/api/v2/test/config/system")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            configs = data.get('config', [])
            count = data.get('count', 0)
            
            print(f"Found {count} configurations:")
            
            # Group by category
            categories = {}
            for config in configs:
                key = config.get('config_key', '')
                category = key.split('.')[0] if '.' in key else 'other'
                if category not in categories:
                    categories[category] = []
                categories[category].append(config)
            
            for category, items in sorted(categories.items()):
                print(f"\n  {category.upper()}:")
                for item in items:
                    key = item.get('config_key', '')
                    value = item.get('config_value', {}).get('value', 'N/A')
                    print(f"    • {key}: {value}")
            
            return count >= 14  # Should have at least 14 configs
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_difficulty_config():
    """Test difficulty configuration"""
    print_section("4. Difficulty Configuration")
    try:
        # Test a few levels
        tests = [
            ('suma', 1),
            ('suma', 5),
            ('mult', 3),
            ('div', 5)
        ]
        
        all_ok = True
        for operacion, nivel in tests:
            response = requests.get(
                f"{BASE_URL}/api/v2/test/config/difficulty/{operacion}/{nivel}"
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    config = data.get('config', {})
                    print(f"✅ {operacion.upper()} nivel {nivel}:")
                    print(f"   Operandos: {config.get('min_operando_1')}-{config.get('max_operando_1')}")
                    print(f"   Tipo: {config.get('tipo_respuesta')}")
                    print(f"   Tiempo: {config.get('max_tiempo_segundos')}s")
                else:
                    print(f"❌ {operacion.upper()} nivel {nivel}: NOT FOUND")
                    all_ok = False
            else:
                print(f"❌ {operacion.upper()} nivel {nivel}: HTTP {response.status_code}")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_get_user_operations(user_ref):
    """Test getting user operations with new fields"""
    print_section("5. User Operations (with new fields)")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v2/test/user/{user_ref}/operations"
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            operations = data.get('operations', [])
            
            if not operations:
                print("⚠️  User has no operations yet")
                return True  # Not an error, just empty
            
            print(f"Found {len(operations)} operations:")
            
            for op in operations:
                print(f"\n  • {op.get('operacion').upper()}:")
                print(f"    Nivel Dominio (visible): {op.get('nivel_dominio')}")
                print(f"    Nivel Invisible: {op.get('nivel_invisible')} ⭐ NEW")
                print(f"    PD: {op.get('pd_operacion')}")
                print(f"    Unlocked: {op.get('unlocked')}")
                print(f"    Batches desde miniboss: {op.get('batches_desde_ultimo_miniboss')} ⭐ NEW")
                print(f"    Fallos miniboss: {op.get('miniboss_fallos_consecutivos')} ⭐ NEW")
            
            return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_create_batch(user_ref):
    """Test creating a test batch"""
    print_section("6. Create Test Batch")
    try:
        batch_data = {
            "user_ref": user_ref,
            "operacion": "suma",
            "batch_type": "regular",
            "nivel_central": 2,
            "ejercicios_correctos": 8,
            "total_ejercicios": 10
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v2/test/batches/create",
            json=batch_data
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Score Ganado: {data.get('score_ganado')}")
            print(f"Cambio Nivel Invisible: {data.get('nivel_invisible_change'):+.1f}")
            
            batch = data.get('batch', {})
            if batch:
                print(f"\nBatch created:")
                print(f"  ID: {batch.get('id')}")
                print(f"  Tipo: {batch.get('batch_type')}")
                print(f"  Operación: {batch.get('operacion')}")
            
            return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_get_batches(user_ref):
    """Test getting user batch history"""
    print_section("7. User Batch History")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v2/test/user/{user_ref}/batches?limit=5"
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            batches = data.get('batches', [])
            
            if not batches:
                print("⚠️  No batches found for user")
                return True  # Not an error
            
            print(f"Found {len(batches)} recent batches:")
            
            for i, batch in enumerate(batches, 1):
                print(f"\n  {i}. Batch #{batch.get('id')}:")
                print(f"     Tipo: {batch.get('batch_type')}")
                print(f"     Operación: {batch.get('operacion')}")
                print(f"     Nivel Central: {batch.get('nivel_central')}")
                print(f"     Nivel Invisible: {batch.get('nivel_invisible_antes'):.2f} → {batch.get('nivel_invisible_despues'):.2f}")
                print(f"     Correctos: {batch.get('ejercicios_correctos')}")
                print(f"     Score: {batch.get('score_ganado')}")
            
            return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_gamification_profile(user_ref):
    """Test getting gamification profile with new fields"""
    print_section("8. Gamification Profile (with new fields)")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v2/test/user/{user_ref}/gamification"
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            profile = data.get('profile', {})
            
            print(f"Gamification Profile:")
            print(f"  PP Total: {profile.get('pp_total')}")
            print(f"  PD Global: {profile.get('pd_global')}")
            print(f"  XP Total: {profile.get('xp_total')}")
            print(f"  Nivel Jugador: {profile.get('nivel_jugador')}")
            print(f"  Racha Actual: {profile.get('racha_dias')} días")
            print(f"  Racha Máxima: {profile.get('racha_maxima')} días ⭐ NEW")
            print(f"  Días Válidos Streak: {profile.get('dias_validos_streak')} ⭐ NEW")
            
            return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_batch_stats():
    """Test global batch statistics"""
    print_section("9. Global Batch Statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/v2/test/stats/batches")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'no_data':
                print("⚠️  No batches in database yet")
                return True
            
            print(f"Total Batches: {data.get('total_batches')}")
            
            by_type = data.get('by_type', {})
            if by_type:
                print(f"\nBy Type:")
                for batch_type, count in by_type.items():
                    print(f"  {batch_type}: {count}")
            
            by_operation = data.get('by_operation', {})
            if by_operation:
                print(f"\nBy Operation:")
                for operation, count in by_operation.items():
                    print(f"  {operation}: {count}")
            
            return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run all tests and show summary"""
    print("\n" + "🔍" * 35)
    print("  GAMIFICATION V2 - TEST SUITE")
    print(f"  Server: {BASE_URL}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔍" * 35)

    # Get a test user (you can change this)
    test_user_ref = "test_user_123"  # Change to a real user_ref from your DB

    results = {
        "Health Check": test_health(),
        "Verify V2 Tables": test_verify_tables(),
        "System Config": test_system_config(),
        "Difficulty Config": test_difficulty_config(),
        "User Operations": test_get_user_operations(test_user_ref),
        "Create Batch": test_create_batch(test_user_ref),
        "Batch History": test_get_batches(test_user_ref),
        "Gamification Profile": test_gamification_profile(test_user_ref),
        "Batch Stats": test_batch_stats()
    }

    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! V2 tables and endpoints are working!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check output above.")
    
    print("\n📝 Note: Some tests may show warnings if user has no data yet.")
    print("   This is normal and not an error.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
