"""
Test directo de inserción - nombres correctos
"""

import sys
sys.path.append('pineServer')

from roble_client import roble_client
from datetime import datetime
import json

print("Testing insert to pine_configuracion_sistema with CORRECT column names...")
print()

# Test single config with EXACT column names from Roble
test_config = {
    "config_key": "test.value",  # Correct name
    "config_value": json.dumps({"value": 999, "type": "integer"}),  # Correct name  
    "description": "Test config",
    "version": 1,
    "activa": True,  # Correct name (Spanish)
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat()
}

print("Attempting to insert:")
print(json.dumps(test_config, indent=2))
print()

try:
    result = roble_client.insert_records("pine_configuracion_sistema", [test_config])
    print("Result:")
    print(json.dumps(result, indent=2))
    
    if result.get("inserted"):
        print(f"\n✅ Insert successful! {len(result['inserted'])} record(s)")
    else:
        print(f"\n❌ Insert failed!")
        if result.get("skipped"):
            print(f"Skipped: {result['skipped']}")
except Exception as e:
    print(f"❌ Insert failed!")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\nReading back to verify...")
try:
    records = roble_client.read_table("pine_configuracion_sistema", {})
    print(f"Found {len(records)} total records in table")
    if records:
        print("\nRecords:")
        for rec in records:
            print(f"  - {rec.get('config_key')}")
except Exception as e:
    print(f"Error reading: {e}")
