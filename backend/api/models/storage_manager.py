import json
import os
from pathlib import Path

class StorageManager:
    def __init__(self):
        # Get the absolute path to the backend directory
        backend_dir = Path(__file__).parent.parent.parent
        self.storage_dir = backend_dir / "storage" / "sessions"
        print(f"Initializing storage at: {self.storage_dir}")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_session_file(self, session_id: str) -> Path:
        return self.storage_dir / f"{session_id}.json"

    def save_session(self, session_id: str, session_data: dict):
        """Save session data to a JSON file"""
        file_path = self._get_session_file(session_id)
        print(f"Saving session {session_id} to {file_path}")
        with open(file_path, 'w') as f:
            json.dump(session_data, f)

    def load_session(self, session_id: str) -> dict:
        """Load session data from a JSON file"""
        file_path = self._get_session_file(session_id)
        print(f"Loading session {session_id} from {file_path}")
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                print(f"Loaded session with {len(data['chat_history'])} messages and {len(data['memorized_key_messages'])} key points")
                return data
        print(f"No existing session found for {session_id}")
        return {
            'chat_history': [],
            'memorized_key_messages': []
        }

    def delete_session(self, session_id: str):
        """Delete session data file"""
        file_path = self._get_session_file(session_id)
        print(f"Deleting session {session_id} at {file_path}")
        if file_path.exists():
            file_path.unlink()
            print(f"Session {session_id} deleted")
        else:
            print(f"No session file found to delete for {session_id}")

# Create singleton instance
storage_manager = StorageManager() 