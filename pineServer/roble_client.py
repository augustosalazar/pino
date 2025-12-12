"""
Roble Database Client
Handles all interactions with the Roble backend
"""

import requests
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class RobleClient:
    """Client for Roble database operations"""
    
    def __init__(self):
        self.project_id = os.getenv("ROBLE_PROJECT_ID")
        self.base_url = os.getenv("ROBLE_BASE_URL", "https://roble-api.openlab.uninorte.edu.co")
        self.admin_email = os.getenv("ADMIN_EMAIL")
        self.admin_password = os.getenv("ADMIN_PASSWORD")
        
        if not all([self.project_id, self.admin_email, self.admin_password]):
            raise ValueError("Missing required environment variables")
        
        self.auth_url = f"{self.base_url}/auth/{self.project_id}".rstrip('/')
        self.db_url = f"{self.base_url}/database/{self.project_id}"
        self.session = requests.Session()
        self.access_token: Optional[str] = None
    
    def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token:
            self._login()
    
    def _login(self):
        """Authenticate with Roble"""
        url = f"{self.auth_url}/login"
        response = self.session.post(url, json={
            "email": self.admin_email,
            "password": self.admin_password
        })
        
        response.raise_for_status()
        data = response.json()
        self.access_token = data.get("accessToken")
        self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
    
    def read_table(self, table_name: str, filters: Dict = None) -> List[Dict]:
        """Read records from a table"""
        self._ensure_authenticated()
        
        url = f"{self.db_url}/read"
        params = {"tableName": table_name}
        
        if filters:
            params.update(filters)
        
        response = self.session.get(url, params=params)
        
        if response.status_code == 401:
            # Token expired, retry once
            self._login()
            response = self.session.get(url, params=params)
        
        response.raise_for_status()
        return response.json()
    
    def insert_records(self, table_name: str, records: List[Dict]) -> Dict:
        """Insert records into a table"""
        self._ensure_authenticated()
        
        url = f"{self.db_url}/insert"
        payload = {
            "tableName": table_name,
            "records": records
        }

        print(f"[RobleClient] Inserting records into {table_name}: {records}")
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 401:
            self._login()
            response = self.session.post(url, json=payload)
        
        response.raise_for_status()
        return response.json()
    
    def update_record(self, table_name: str, record_id: str, updates: Dict) -> bool:
        """Update a record by _id"""
        self._ensure_authenticated()
        
        url = f"{self.db_url}/update"
        payload = {
            "tableName": table_name,
            "idColumn": "_id",
            "idValue": record_id,
            "updates": updates
        }

        print(f"[RobleClient] Updating record {record_id} in table {table_name} with updates: {updates}")
        
        response = self.session.put(url, json=payload)
        
        if response.status_code == 401:
            self._login()
            response = self.session.put(url, json=payload)
        
        response.raise_for_status()
        return True
    
    def update_or_replace(self, table_name: str, record_id: str, updates: Dict) -> bool:
        """
        Update a record, with fallback to delete+insert if update fails.
        This is a workaround for Roble's limited UPDATE support.
        """
        try:
            # Try normal update first
            return self.update_record(table_name, record_id, updates)
        except Exception as e:
            print(f"[WARNING] Update failed for {table_name}, using delete+insert: {e}")
            
            # Fallback: Read current record, merge with updates, delete, re-insert
            try:
                # Read current record
                records = self.read_table(table_name, {"_id": record_id})
                if not records:
                    raise Exception(f"Record {record_id} not found for update")
                
                current_record = records[0]
                
                # Merge updates into current record
                updated_record = {**current_record, **updates}
                
                # Remove the _id field as Roble auto-generates it
                updated_record.pop('_id', None)
                updated_record.pop('created_at', None)
                updated_record.pop('updated_at', None)
                
                # Delete old record
                self._delete_record(table_name, record_id)
                
                # Insert updated record
                result = self.insert_records(table_name, [updated_record])
                return result.get("inserted") is not None
                
            except Exception as fallback_error:
                print(f"[ERROR] Fallback delete+insert also failed: {fallback_error}")
                raise
    
    def _delete_record(self, table_name: str, record_id: str) -> bool:
        """Delete a record by _id"""
        self._ensure_authenticated()
        
        url = f"{self.db_url}/delete"
        payload = {
            "tableName": table_name,
            "idColumn": "_id",
            "idValue": record_id
        }
        
        response = self.session.delete(url, json=payload)
        
        if response.status_code == 401:
            self._login()
            response = self.session.delete(url, json=payload)
        
        response.raise_for_status()
        return True


# Global instance
roble_client = RobleClient()
