"""
Ver estructura de pine_configuracion_sistema
"""

import sys
sys.path.append('pineServer')

from roble_client import roble_client

print("Reading pine_configuracion_sistema structure...")
print()

try:
    # Read any existing records to see the fields
    records = roble_client.read_table("pine_configuracion_sistema", {})
    
    if records and len(records) > 0:
        print(f"Found {len(records)} existing records")
        print("\nFirst record structure:")
        for key in records[0].keys():
            print(f"  - {key}")
    else:
        print("Table is empty - trying to read schema...")
        print("\nTable exists but is empty.")
        print("We need to know what columns the table has.")
        print("\nTry listing all tables:")
        # This might not work with Roble, but let's try
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
