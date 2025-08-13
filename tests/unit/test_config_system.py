# tests/unit/test_config_system.py
"""
Unit tests for the VoidClientAI Configuration System
"""

import sys
import os
import tempfile
import shutil
import unittest
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.config_manager import ConfigManager
import logging


class TestConfigurationSystem(unittest.TestCase):
    """Test cases for the Configuration System"""

    def setUp(self):
        """Set up test environment with temporary directory"""
        # Create temporary directory for test configs
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.test_dir, "config")

        # Setup basic logging
        logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_config_manager_initialization(self):
        """Test ConfigManager initialization"""
        config = ConfigManager(config_dir=self.config_dir)

        # Verify config manager is properly initialized
        self.assertIsNotNone(config)
        self.assertTrue(hasattr(config, 'logger'))
        self.assertTrue(hasattr(config, '_configs'))
        self.assertEqual(len(config._configs), 5)  # Should have 5 config types

    def test_basic_configuration_access(self):
        """Test basic configuration value access"""
        config = ConfigManager(config_dir=self.config_dir)

        # Test property access
        model_path = config.model_path
        workspace_path = config.workspace_path
        minecraft_version = config.minecraft_version
        safe_mode = config.safe_mode

        self.assertIsInstance(model_path, str)
        self.assertIsInstance(workspace_path, str)
        self.assertIsInstance(minecraft_version, str)
        self.assertIsInstance(safe_mode, bool)

    def test_dot_notation_access(self):
        """Test dot notation configuration access"""
        config = ConfigManager(config_dir=self.config_dir)

        # Test nested value access
        temperature = config.get('performance', 'generation_settings.temperature')
        max_tokens = config.get('performance', 'generation_settings.max_new_tokens')
        use_gpu = config.get('performance', 'model_optimization.use_gpu')

        self.assertIsInstance(temperature, float)
        self.assertIsInstance(max_tokens, int)
        self.assertIsInstance(use_gpu, bool)

    def test_configuration_setting(self):
        """Test setting configuration values"""
        config = ConfigManager(config_dir=self.config_dir)

        # Test setting a value
        config.set('main', 'debug_mode', True, save=False)
        debug_mode = config.get('main', 'debug_mode')
        self.assertTrue(debug_mode)

        # Test setting nested value
        config.set('performance', 'generation_settings.temperature', 0.8, save=False)
        new_temp = config.get('performance', 'generation_settings.temperature')
        self.assertEqual(new_temp, 0.8)

    def test_batch_configuration_updates(self):
        """Test batch configuration updates"""
        config = ConfigManager(config_dir=self.config_dir)

        # Test batch update
        updates = {
            'generation_settings': {
                'temperature': 0.9,
                'max_new_tokens': 512
            }
        }
        config.update_config('performance', updates, save=False)

        new_temp = config.get('performance', 'generation_settings.temperature')
        new_tokens = config.get('performance', 'generation_settings.max_new_tokens')

        self.assertEqual(new_temp, 0.9)
        self.assertEqual(new_tokens, 512)

    def test_configuration_validation(self):
        """Test configuration validation"""
        config = ConfigManager(config_dir=self.config_dir)

        validation_results = config.validate_config()

        # All configs should be valid
        self.assertEqual(len(validation_results), 5)
        for config_type, is_valid in validation_results.items():
            self.assertTrue(is_valid, f"{config_type} configuration should be valid")

    def test_default_values(self):
        """Test that default values are properly returned"""
        config = ConfigManager(config_dir=self.config_dir)

        # Test non-existent key with default
        non_existent = config.get('main', 'non_existent_key', 'default_value')
        self.assertEqual(non_existent, 'default_value')

        # Test non-existent nested key with default
        nested_non_existent = config.get('performance', 'non_existent.nested.key', 42)
        self.assertEqual(nested_non_existent, 42)

    def test_security_configuration(self):
        """Test security configuration access"""
        config = ConfigManager(config_dir=self.config_dir)

        allowed_dirs = config.get('security', 'file_operations.allowed_directories')
        blocked_dirs = config.get('security', 'file_operations.blocked_directories')
        sandbox_enabled = config.get('security', 'code_execution.enable_sandbox')

        self.assertIsInstance(allowed_dirs, list)
        self.assertIsInstance(blocked_dirs, list)
        self.assertIsInstance(sandbox_enabled, bool)
        self.assertTrue(len(allowed_dirs) > 0)
        self.assertTrue(len(blocked_dirs) > 0)

    def test_learning_configuration(self):
        """Test learning configuration access"""
        config = ConfigManager(config_dir=self.config_dir)

        learning_enabled = config.get('learning', 'ai_learning.enable_learning')
        pattern_threshold = config.get('learning', 'ai_learning.pattern_recognition_threshold')
        feedback_enabled = config.get('learning', 'feedback_system.enable_user_feedback')

        self.assertIsInstance(learning_enabled, bool)
        self.assertIsInstance(pattern_threshold, float)
        self.assertIsInstance(feedback_enabled, bool)

    def test_user_preferences(self):
        """Test user preferences configuration"""
        config = ConfigManager(config_dir=self.config_dir)

        theme = config.get('user_preferences', 'ui_preferences.theme')
        font_family = config.get('user_preferences', 'ui_preferences.font_family')
        include_comments = config.get('user_preferences', 'generation_preferences.include_comments')

        self.assertIsInstance(theme, str)
        self.assertIsInstance(font_family, str)
        self.assertIsInstance(include_comments, bool)

    def test_config_files_creation(self):
        """Test that configuration files are created properly"""
        config = ConfigManager(config_dir=self.config_dir)

        # Check that all config files exist
        for config_name, config_path in config.config_files.items():
            self.assertTrue(config_path.exists(), f"{config_name} config file should exist")

        # Check that files contain valid JSON
        import json
        for config_name, config_path in config.config_files.items():
            with open(config_path, 'r') as f:
                try:
                    data = json.load(f)
                    self.assertIsInstance(data, dict, f"{config_name} should contain valid JSON object")
                except json.JSONDecodeError:
                    self.fail(f"{config_name} config file contains invalid JSON")


def run_simple_test():
    """Run a simple test without unittest framework for basic verification"""
    print("🧪 Running Simple Configuration System Test")
    print("=" * 50)

    try:
        # Create temporary directory
        test_dir = tempfile.mkdtemp()
        config_dir = os.path.join(test_dir, "config")

        print("1. Initializing ConfigManager...")
        config = ConfigManager(config_dir=config_dir)
        print("✅ ConfigManager initialized successfully")

        print("\n2. Testing basic configuration access...")
        model_path = config.model_path
        workspace_path = config.workspace_path
        minecraft_version = config.minecraft_version
        use_gpu = config.use_gpu

        print(f"✅ Model Path: {model_path}")
        print(f"✅ Workspace Path: {workspace_path}")
        print(f"✅ Minecraft Version: {minecraft_version}")
        print(f"✅ Use GPU: {use_gpu}")

        print("\n3. Testing dot notation access...")
        temp = config.get('performance', 'generation_settings.temperature')
        max_tokens = config.get('performance', 'generation_settings.max_new_tokens')
        cache_enabled = config.get('performance', 'model_optimization.cache_enabled')

        print(f"✅ Temperature: {temp}")
        print(f"✅ Max Tokens: {max_tokens}")
        print(f"✅ Cache Enabled: {cache_enabled}")

        print("\n4. Testing configuration updates...")
        config.set('main', 'debug_mode', True, save=False)
        debug_mode = config.get('main', 'debug_mode')
        print(f"✅ Debug mode updated to: {debug_mode}")

        print("\n5. Testing validation...")
        validation_results = config.validate_config()
        all_valid = all(validation_results.values())
        print(f"✅ All configurations valid: {all_valid}")

        print("\n6. Testing security configuration...")
        allowed_dirs = config.get('security', 'file_operations.allowed_directories')
        print(f"✅ Security config loaded: {len(allowed_dirs)} allowed directories")

        # Clean up
        shutil.rmtree(test_dir)

        print("\n" + "=" * 50)
        print("🎉 Simple Configuration Test Complete!")
        print("All basic functionality is working correctly.")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # First run simple test
    print("Running simple verification test...")
    simple_success = run_simple_test()

    if simple_success:
        print("\n" + "=" * 60)
        print("Running comprehensive unit tests...")

        # Run unit tests
        unittest.main(verbosity=2, exit=False)
    else:
        print("❌ Simple test failed, skipping unit tests")
        sys.exit(1)