
import sys
import os
from datetime import datetime

# Add generic path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from v2.batch_recorder import BatchRecorder
from v2.models import BatchResult, BatchType, UserGamificationState, ExerciseResult, Exercise
from roble_client import roble_client

def test_miniboss_logging():
    print("Testing pine_mini_jefes_intentos writing...")
    
    # 1. Direct write test
    try:
        test_record = {
            "user_ref": "test_user_debug",
            "operacion": "suma",
            "nivel_intentado": 1.5,
            "aprobado": True,
            "score": 100,
            "correctos": 5,
            "total": 5,
            "created_at": datetime.utcnow().isoformat(),
            "debug_created": True
        }
        print("Attempting direct insert...")
        res = roble_client.insert_records("pine_mini_jefes_intentos", [test_record])
        print(f"Direct insert result: {res}")
    except Exception as e:
        print(f"Direct insert failed: {e}")
        
    # 2. Test via BatchRecorder
    print("\nTesting via BatchRecorder...")
    recorder = BatchRecorder()
    
    # Mock result
    mock_exercise = Exercise(1, 1, "suma", 2, 1.0, "multiple_choice")
    mock_res = ExerciseResult(mock_exercise, 2, True, 1.0)
    
    batch_result = BatchResult(
        user_ref="test_user_debug_recorder",
        operacion="suma",
        batch_type=BatchType.MINIBOSS, # Use Enum
        ejercicios=[mock_res],
        nivel_central=1,
        nivel_invisible_antes=1.0,
        nivel_invisible_despues=1.5,
        miniboss_aprobado=True
    )
    
    gamif_state = UserGamificationState("test_user_debug_recorder")
    
    try:
        print("Calling record_batch...")
        success = recorder.record_batch(batch_result, gamif_state)
        print(f"record_batch returned: {success}")
    except Exception as e:
        print(f"record_batch failed: {e}")

if __name__ == "__main__":
    test_miniboss_logging()
