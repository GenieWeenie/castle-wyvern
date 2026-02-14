import json
import os
from datetime import datetime

class Grimoorum:
    def __init__(self, storage_file='grimoorum/clan_memory.json'):
        self.storage_file = storage_file
        self._initialize_vault()

    def _initialize_vault(self):
        """Creates the memory file if it doesn't exist."""
        if not os.path.exists(self.storage_file):
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            with open(self.storage_file, 'w') as f:
                json.dump([], f)

    def record_interaction(self, user_input, agent_response):
        """Saves a new interaction to the vault."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = {
            "timestamp": timestamp,
            "user": user_input,
            "agent": agent_response
        }

        try:
            with open(self.storage_file, 'r+') as f:
                memory = json.load(f)
                memory.append(new_entry)
                f.seek(0)
                json.dump(memory, f, indent=4)
        except Exception as e:
            print(f"Error archiving memory: {e}")

    def consult_archives(self, limit=5):
        """Retrieves the last few interactions for context."""
        try:
            with open(self.storage_file, 'r') as f:
                memory = json.load(f)
                return memory[-limit:]
        except (FileNotFoundError, json.JSONDecodeError):
            return []