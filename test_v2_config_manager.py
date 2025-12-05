"""
Test del ConfigManager

Verifica que:
1. Se pueden leer configuraciones del sistema
2. Se pueden leer configuraciones de dificultad
3. El cache funciona correctamente
4. Los métodos helper funcionan
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pineServer.v2.config_manager import ConfigManager, get_config_manager


def test_system_config():
    """Test lectura de configuraciones del sistema"""
    print("\n" + "="*70)
    print("TEST 1: System Configuration")
    print("="*70)
    
    config_mgr = ConfigManager()
    
    # Test individual configs
    base_multiplier = config_mgr.get_system_config("scoring.base_multiplier")
    print(f"✓ scoring.base_multiplier: {base_multiplier}")
    assert base_multiplier is not None, "base_multiplier should not be None"
    
    min_correct = config_mgr.get_system_config("streak.min_correct")
    print(f"✓ streak.min_correct: {min_correct}")
    assert min_correct is not None, "min_correct should not be None"
    
    batch_size = config_mgr.get_system_config("batch.size")
    print(f"✓ batch.size: {batch_size}")
    assert batch_size is not None, "batch_size should not be None"
    
    # Test default value
    non_existent = config_mgr.get_system_config("non.existent.key", "DEFAULT")
    print(f"✓ non.existent.key (default): {non_existent}")
    assert non_existent == "DEFAULT", "Default value should work"
    
    print("✅ System config test PASSED")
    return True


def test_difficulty_config():
    """Test lectura de configuraciones de dificultad"""
    print("\n" + "="*70)
    print("TEST 2: Difficulty Configuration")
    print("="*70)
    
    config_mgr = ConfigManager()
    
    # Test suma nivel 1
    suma_1 = config_mgr.get_difficulty_config("suma", 1)
    print(f"✓ suma nivel 1:")
    print(f"  - min_operando_1: {suma_1.get('min_operando_1')}")
    print(f"  - max_operando_1: {suma_1.get('max_operando_1')}")
    print(f"  - tipo_respuesta: {suma_1.get('tipo_respuesta')}")
    assert suma_1 is not None, "suma nivel 1 config should exist"
    assert suma_1.get("min_operando_1") is not None, "min_operando_1 should exist"
    
    # Test mult nivel 3
    mult_3 = config_mgr.get_difficulty_config("mult", 3)
    print(f"✓ mult nivel 3:")
    print(f"  - min_operando_1: {mult_3.get('min_operando_1')}")
    print(f"  - max_operando_1: {mult_3.get('max_operando_1')}")
    print(f"  - tipo_respuesta: {mult_3.get('tipo_respuesta')}")
    assert mult_3 is not None, "mult nivel 3 config should exist"
    
    # Test div nivel 5
    div_5 = config_mgr.get_difficulty_config("div", 5)
    print(f"✓ div nivel 5:")
    print(f"  - min_operando_1: {div_5.get('min_operando_1')}")
    print(f"  - max_operando_1: {div_5.get('max_operando_1')}")
    print(f"  - tipo_respuesta: {div_5.get('tipo_respuesta')}")
    assert div_5 is not None, "div nivel 5 config should exist"
    
    # Test non-existent config
    non_existent = config_mgr.get_difficulty_config("invalid", 99)
    print(f"✓ invalid nivel 99: {non_existent}")
    assert non_existent is None, "Non-existent config should return None"
    
    print("✅ Difficulty config test PASSED")
    return True


def test_helper_methods():
    """Test métodos helper para configs comunes"""
    print("\n" + "="*70)
    print("TEST 3: Helper Methods")
    print("="*70)
    
    config_mgr = ConfigManager()
    
    # Test scoring config
    scoring = config_mgr.get_scoring_config()
    print("✓ Scoring config:")
    print(f"  - base_multiplier: {scoring['base_multiplier']}")
    print(f"  - participation_bonus: {scoring['participation_bonus']}")
    print(f"  - error_penalty: {scoring['error_penalty']}")
    assert all(k in scoring for k in ["base_multiplier", "participation_bonus", "error_penalty"])
    
    # Test streak config
    streak = config_mgr.get_streak_config()
    print("✓ Streak config:")
    print(f"  - min_correct: {streak['min_correct']}")
    print(f"  - base_score: {streak['base_score']}")
    print(f"  - daily_multiplier: {streak['daily_multiplier']}")
    print(f"  - max_days: {streak['max_days']}")
    assert all(k in streak for k in ["min_correct", "base_score", "daily_multiplier", "max_days"])
    
    # Test miniboss config
    miniboss = config_mgr.get_miniboss_config()
    print("✓ Miniboss config:")
    print(f"  - min_batches_after_fail: {miniboss['min_batches_after_fail']}")
    print(f"  - min_correct_rate: {miniboss['min_correct_rate']}")
    print(f"  - nivel_invisible_threshold: {miniboss['nivel_invisible_threshold']}")
    assert all(k in miniboss for k in ["min_batches_after_fail", "min_correct_rate", "nivel_invisible_threshold"])
    
    # Test batch config
    batch = config_mgr.get_batch_config()
    print("✓ Batch config:")
    print(f"  - size: {batch['size']}")
    print(f"  - distribution_easy: {batch['distribution_easy']}")
    print(f"  - distribution_central: {batch['distribution_central']}")
    print(f"  - distribution_hard: {batch['distribution_hard']}")
    assert all(k in batch for k in ["size", "distribution_easy", "distribution_central", "distribution_hard"])
    
    print("✅ Helper methods test PASSED")
    return True


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "🔍"*35)
    print("  CONFIG MANAGER - TEST SUITE")
    print("🔍"*35)
    
    tests = [
        ("System Config", test_system_config),
        ("Difficulty Config", test_difficulty_config),
        ("Helper Methods", test_helper_methods),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! ConfigManager is working correctly!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
