# core/config_manager.py
import json
import os


class ConfigManager:
    def __init__(self, config_path="data/config.json"):
        self.config_path = config_path
        self.config = self._load_or_create_config()

    def _load_or_create_config(self):
        default_config = {
            "model_path": "C:/Coding/VoidClientAI/CodeLlama-7b-hf",
            "workspace_path": "./workspace",
            "max_memory_entries": 1000,
            "auto_backup": True,
            "safe_mode": True,
            "minecraft_version": "1.20.1",
            "forge_version": "47.2.0"
        }

        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return {**default_config, **json.load(f)}
        else:
            self._save_config(default_config)
            return default_config