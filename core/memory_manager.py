import os
import json
import hashlib
from datetime import datetime


class MemoryManager:
    def __init__(self, storage_dir="data/memory_db/"):
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        self.storage_dir = storage_dir
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"📝 Memory system initialized at {storage_dir}")

    def _generate_memory_id(self, input_string):
        return hashlib.sha256(input_string.encode()).hexdigest()[:12]

    def store_interaction(self, user_input, generated_code, feedback=None):
        memory_id = self._generate_memory_id(user_input)
        memory_entry = {
            "id": memory_id,
            "timestamp": str(datetime.now()),
            "input": user_input,
            "generated_code": generated_code,
            "feedback": feedback,
            "session": self.session_id
        }

        file_path = os.path.join(self.storage_dir, f"{memory_id}.json")
        with open(file_path, 'w') as f:
            json.dump(memory_entry, f, indent=2)

        return memory_id

    def get_similar_solutions(self, user_input, threshold=0.7):
        """Find similar past solutions using simple text similarity"""
        import difflib

        similar_memories = []
        for memory_file in os.listdir(self.storage_dir):
            if memory_file.endswith('.json'):
                with open(os.path.join(self.storage_dir, memory_file), 'r') as f:
                    memory = json.load(f)
                    similarity = difflib.SequenceMatcher(
                        None, user_input.lower(), memory['input'].lower()
                    ).ratio()

                    if similarity >= threshold:
                        similar_memories.append((similarity, memory))

        return sorted(similar_memories, key=lambda x: x[0], reverse=True)