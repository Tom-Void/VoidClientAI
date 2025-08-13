# core/config_manager.py
import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class ConfigManager:
    """
    Centralized configuration management system for VoidClientAI
    Handles all configuration files and provides type-safe access to settings
    """

    def __init__(self, config_dir: str = "data/config"):
        # Setup logging first
        self.logger = logging.getLogger(__name__)

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Configuration file paths
        self.config_files = {
            'main': self.config_dir / 'main_config.json',
            'performance': self.config_dir / 'performance_config.json',
            'security': self.config_dir / 'security_config.json',
            'learning': self.config_dir / 'learning_config.json',
            'user_preferences': self.config_dir / 'user_preferences.json'
        }

        # Loaded configurations cache
        self._configs = {}

        # Initialize all configurations
        self._initialize_all_configs()

        self.logger.info("Configuration Manager initialized")

    def _initialize_all_configs(self):
        """Initialize all configuration files with defaults if they don't exist"""
        for config_name in self.config_files.keys():
            self._load_or_create_config(config_name)

    def _get_default_config(self, config_type: str) -> Dict[str, Any]:
        """Get default configuration for each config type"""
        defaults = {
            'main': {
                "version": "1.0.0",
                "app_name": "VoidClientAI",
                "model_path": "models/CodeLlama-7b-hf",
                "workspace_path": "./workspace",
                "minecraft_version": "1.20.1",
                "fabric_version": "0.14.22",
                "yarn_mappings": "1.20.1+build.10",
                "auto_backup": True,
                "safe_mode": True,
                "debug_mode": False,
                "max_memory_entries": 1000,
                "context_window_size": 4096,
                "generation_timeout": 30,
                "auto_save_interval": 300,
                "last_updated": datetime.now().isoformat()
            },

            'performance': {
                "model_optimization": {
                    "use_gpu": True,
                    "gpu_memory_limit": 8192,
                    "cpu_threads": 4,
                    "batch_size": 1,
                    "model_precision": "float16",
                    "enable_model_quantization": False,
                    "cache_enabled": True,
                    "cache_size_mb": 512
                },
                "generation_settings": {
                    "max_new_tokens": 256,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 50,
                    "repetition_penalty": 1.1,
                    "do_sample": True
                },
                "memory_management": {
                    "enable_memory_optimization": True,
                    "max_memory_usage_mb": 4096,
                    "garbage_collection_interval": 10,
                    "clear_cache_on_exit": True
                },
                "threading": {
                    "max_worker_threads": 8,
                    "enable_parallel_processing": True,
                    "thread_pool_size": 4
                }
            },

            'security': {
                "file_operations": {
                    "allowed_directories": [
                        "src/main/java",
                        "generated",
                        "workspace",
                        "data/memory_db"
                    ],
                    "blocked_directories": [
                        "/",
                        "C:\\",
                        "/usr",
                        "/etc",
                        "C:\\Windows",
                        "C:\\Program Files"
                    ],
                    "allowed_extensions": [".java", ".json", ".txt", ".md", ".gradle"],
                    "max_file_size_mb": 10,
                    "enable_backup_before_overwrite": True
                },
                "code_execution": {
                    "enable_sandbox": True,
                    "sandbox_timeout": 60,
                    "max_compilation_time": 30,
                    "allowed_imports": [
                        "java.util.*",
                        "net.minecraft.*",
                        "net.fabricmc.*"
                    ],
                    "blocked_imports": [
                        "java.io.File",
                        "java.nio.file.*",
                        "java.net.*",
                        "java.lang.Runtime"
                    ]
                },
                "network": {
                    "allow_internet_access": False,
                    "allowed_domains": [],
                    "enable_ssl_verification": True,
                    "request_timeout": 10
                },
                "audit": {
                    "log_all_operations": True,
                    "log_level": "INFO",
                    "retain_logs_days": 30,
                    "enable_real_time_monitoring": True
                }
            },

            'learning': {
                "ai_learning": {
                    "enable_learning": True,
                    "learning_rate": 0.001,
                    "pattern_recognition_threshold": 0.75,
                    "success_pattern_weight": 1.0,
                    "failure_pattern_weight": 0.8,
                    "context_similarity_threshold": 0.6
                },
                "feedback_system": {
                    "enable_user_feedback": True,
                    "auto_feedback_collection": True,
                    "feedback_weight": 1.2,
                    "min_feedback_threshold": 3
                },
                "pattern_learning": {
                    "max_patterns_stored": 10000,
                    "pattern_decay_factor": 0.95,
                    "pattern_update_frequency": "daily",
                    "enable_pattern_clustering": True
                },
                "model_adaptation": {
                    "enable_fine_tuning": False,
                    "fine_tune_threshold": 100,
                    "adaptation_learning_rate": 0.0001,
                    "max_adaptation_steps": 1000
                },
                "performance_tracking": {
                    "track_generation_speed": True,
                    "track_code_quality": True,
                    "track_user_satisfaction": True,
                    "benchmark_frequency": "weekly"
                }
            },

            'user_preferences': {
                "ui_preferences": {
                    "theme": "dark",
                    "font_family": "JetBrains Mono",
                    "font_size": 14,
                    "show_line_numbers": True,
                    "auto_complete": True,
                    "syntax_highlighting": True
                },
                "code_style": {
                    "indent_size": 4,
                    "use_tabs": False,
                    "max_line_length": 120,
                    "brace_style": "allman",
                    "package_naming": "lowercase",
                    "class_naming": "PascalCase",
                    "method_naming": "camelCase",
                    "variable_naming": "camelCase"
                },
                "generation_preferences": {
                    "include_comments": True,
                    "comment_style": "detailed",
                    "include_javadoc": True,
                    "include_imports": True,
                    "include_package_declaration": True,
                    "preferred_patterns": ["builder", "factory", "observer"]
                },
                "workflow": {
                    "auto_save": True,
                    "confirm_overwrites": True,
                    "show_progress": True,
                    "enable_notifications": True,
                    "default_output_directory": "src/main/java/com/example"
                },
                "shortcuts": {
                    "generate_code": "Ctrl+G",
                    "save_file": "Ctrl+S",
                    "open_project": "Ctrl+O",
                    "show_help": "F1"
                }
            }
        }

        return defaults.get(config_type, {})

    def _load_or_create_config(self, config_type: str) -> Dict[str, Any]:
        """Load configuration from file or create with defaults"""
        config_file = self.config_files[config_type]

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                # Merge with defaults to ensure all keys exist
                default_config = self._get_default_config(config_type)
                merged_config = self._deep_merge(default_config, loaded_config)

                # Save merged config back to ensure consistency
                self._save_config(config_type, merged_config)

                self._configs[config_type] = merged_config
                self.logger.info(f"Loaded configuration: {config_type}")
                return merged_config

            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Error loading {config_type} config: {e}. Using defaults.")
                return self._create_default_config(config_type)
        else:
            return self._create_default_config(config_type)

    def _create_default_config(self, config_type: str) -> Dict[str, Any]:
        """Create default configuration file"""
        default_config = self._get_default_config(config_type)
        self._save_config(config_type, default_config)
        self._configs[config_type] = default_config
        self.logger.info(f"Created default configuration: {config_type}")
        return default_config

    def _save_config(self, config_type: str, config_data: Dict[str, Any]):
        """Save configuration to file"""
        config_file = self.config_files[config_type]

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            self.logger.debug(f"Saved configuration: {config_type}")
        except Exception as e:
            self.logger.error(f"Error saving {config_type} config: {e}")
            raise

    def _deep_merge(self, default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, with override taking precedence"""
        result = default.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, config_type: str, key_path: str = None, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            config_type: Type of config ('main', 'performance', etc.)
            key_path: Dot-separated path to the value (e.g., 'model_optimization.use_gpu')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if config_type not in self._configs:
            self.logger.warning(f"Unknown config type: {config_type}")
            return default

        config = self._configs[config_type]

        if key_path is None:
            return config

        keys = key_path.split('.')
        current = config

        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            self.logger.debug(f"Key path '{key_path}' not found in {config_type} config")
            return default

    def set(self, config_type: str, key_path: str, value: Any, save: bool = True):
        """
        Set configuration value using dot notation

        Args:
            config_type: Type of config ('main', 'performance', etc.)
            key_path: Dot-separated path to the value
            value: Value to set
            save: Whether to save to file immediately
        """
        if config_type not in self._configs:
            self.logger.warning(f"Unknown config type: {config_type}")
            return

        config = self._configs[config_type]
        keys = key_path.split('.')
        current = config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the value
        current[keys[-1]] = value

        if save:
            self._save_config(config_type, config)

        self.logger.debug(f"Set {config_type}.{key_path} = {value}")

    def update_config(self, config_type: str, updates: Dict[str, Any], save: bool = True):
        """
        Update multiple configuration values

        Args:
            config_type: Type of config to update
            updates: Dictionary of updates to apply
            save: Whether to save to file immediately
        """
        if config_type not in self._configs:
            self.logger.warning(f"Unknown config type: {config_type}")
            return

        self._configs[config_type] = self._deep_merge(self._configs[config_type], updates)

        if save:
            self._save_config(config_type, self._configs[config_type])

        self.logger.info(f"Updated {config_type} configuration")

    def reload_config(self, config_type: str = None):
        """Reload configuration from files"""
        if config_type:
            self._load_or_create_config(config_type)
            self.logger.info(f"Reloaded {config_type} configuration")
        else:
            for cfg_type in self.config_files.keys():
                self._load_or_create_config(cfg_type)
            self.logger.info("Reloaded all configurations")

    def export_config(self, output_path: str, config_type: str = None):
        """Export configuration(s) to a file"""
        output_path = Path(output_path)

        if config_type:
            config_data = {config_type: self._configs.get(config_type, {})}
        else:
            config_data = self._configs.copy()

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Exported configuration to {output_path}")
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            raise

    def import_config(self, input_path: str, config_type: str = None):
        """Import configuration(s) from a file"""
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {input_path}")

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)

            if config_type:
                if config_type in imported_data:
                    self.update_config(config_type, imported_data[config_type])
                else:
                    raise ValueError(f"Config type '{config_type}' not found in import file")
            else:
                for cfg_type, cfg_data in imported_data.items():
                    if cfg_type in self.config_files:
                        self.update_config(cfg_type, cfg_data)

            self.logger.info(f"Imported configuration from {input_path}")
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
            raise

    def validate_config(self, config_type: str = None) -> Dict[str, bool]:
        """Validate configuration(s) for required fields and types"""
        results = {}

        configs_to_validate = [config_type] if config_type else self.config_files.keys()

        for cfg_type in configs_to_validate:
            try:
                config = self._configs.get(cfg_type, {})
                default = self._get_default_config(cfg_type)

                # Check if all required keys exist
                valid = self._validate_config_structure(config, default)
                results[cfg_type] = valid

                if valid:
                    self.logger.debug(f"{cfg_type} configuration is valid")
                else:
                    self.logger.warning(f"{cfg_type} configuration is invalid")

            except Exception as e:
                self.logger.error(f"Error validating {cfg_type} config: {e}")
                results[cfg_type] = False

        return results

    def _validate_config_structure(self, config: Dict, template: Dict) -> bool:
        """Recursively validate configuration structure"""
        for key, value in template.items():
            if key not in config:
                return False
            if isinstance(value, dict):
                if not isinstance(config[key], dict):
                    return False
                if not self._validate_config_structure(config[key], value):
                    return False
        return True

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of all configurations"""
        summary = {
            "config_files": {name: str(path) for name, path in self.config_files.items()},
            "loaded_configs": list(self._configs.keys()),
            "config_sizes": {name: len(str(config)) for name, config in self._configs.items()},
            "last_modified": {}
        }

        for name, path in self.config_files.items():
            if path.exists():
                summary["last_modified"][name] = datetime.fromtimestamp(path.stat().st_mtime).isoformat()

        return summary

    def reset_to_defaults(self, config_type: str = None):
        """Reset configuration(s) to default values"""
        if config_type:
            default_config = self._get_default_config(config_type)
            self._configs[config_type] = default_config
            self._save_config(config_type, default_config)
            self.logger.info(f"Reset {config_type} configuration to defaults")
        else:
            for cfg_type in self.config_files.keys():
                self.reset_to_defaults(cfg_type)
            self.logger.info("Reset all configurations to defaults")

    # Convenience methods for commonly used configurations
    @property
    def model_path(self) -> str:
        return self.get('main', 'model_path', 'models/CodeLlama-7b-hf')

    @property
    def workspace_path(self) -> str:
        return self.get('main', 'workspace_path', './workspace')

    @property
    def minecraft_version(self) -> str:
        return self.get('main', 'minecraft_version', '1.20.1')

    @property
    def safe_mode(self) -> bool:
        return self.get('main', 'safe_mode', True)

    @property
    def debug_mode(self) -> bool:
        return self.get('main', 'debug_mode', False)

    @property
    def use_gpu(self) -> bool:
        return self.get('performance', 'model_optimization.use_gpu', True)

    @property
    def max_new_tokens(self) -> int:
        return self.get('performance', 'generation_settings.max_new_tokens', 256)

    @property
    def temperature(self) -> float:
        return self.get('performance', 'generation_settings.temperature', 0.7)