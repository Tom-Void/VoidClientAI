# config_integration_examples.py
"""
Examples showing how to integrate the new ConfigManager with existing VoidClientAI components
"""

from core.config_manager import ConfigManager
import os


class EnhancedLLMEngine:
    """
    Example of how to update the existing LLMEngine to use ConfigManager
    """

    def __init__(self, config_manager: ConfigManager = None):
        # Use ConfigManager if provided, otherwise create one
        self.config = config_manager or ConfigManager()

        # Get configuration values
        model_path = self.config.model_path
        self.max_new_tokens = self.config.get('performance', 'generation_settings.max_new_tokens')
        self.temperature = self.config.get('performance', 'generation_settings.temperature')
        self.use_gpu = self.config.use_gpu
        self.cache_enabled = self.config.get('performance', 'model_optimization.cache_enabled')

        print(f"🤖 Enhanced LLM Engine initialized with:")
        print(f"   Model Path: {model_path}")
        print(f"   Max Tokens: {self.max_new_tokens}")
        print(f"   Temperature: {self.temperature}")
        print(f"   Use GPU: {self.use_gpu}")
        print(f"   Cache Enabled: {self.cache_enabled}")

    def generate_code(self, prompt: str):
        """Generate code using configuration settings"""
        # Use configured generation settings
        generation_params = {
            'max_new_tokens': self.max_new_tokens,
            'temperature': self.temperature,
            'top_p': self.config.get('performance', 'generation_settings.top_p'),
            'top_k': self.config.get('performance', 'generation_settings.top_k'),
            'repetition_penalty': self.config.get('performance', 'generation_settings.repetition_penalty'),
            'do_sample': self.config.get('performance', 'generation_settings.do_sample')
        }

        print(f"🔄 Generating code with params: {generation_params}")
        # Here you would integrate with the actual model generation
        return f"// Generated code for: {prompt[:50]}..."


class EnhancedFileManager:
    """
    Example of how to update FileManager to use security configuration
    """

    def __init__(self, config_manager: ConfigManager = None):
        self.config = config_manager or ConfigManager()

        # Load security settings
        self.allowed_dirs = self.config.get('security', 'file_operations.allowed_directories')
        self.blocked_dirs = self.config.get('security', 'file_operations.blocked_directories')
        self.allowed_extensions = self.config.get('security', 'file_operations.allowed_extensions')
        self.max_file_size_mb = self.config.get('security', 'file_operations.max_file_size_mb')
        self.enable_backup = self.config.get('security', 'file_operations.enable_backup_before_overwrite')

        print(f"📁 Enhanced File Manager initialized with security settings:")
        print(f"   Allowed directories: {len(self.allowed_dirs)}")
        print(f"   Blocked directories: {len(self.blocked_dirs)}")
        print(f"   Allowed extensions: {self.allowed_extensions}")

    def validate_file_path(self, file_path: str) -> bool:
        """Validate file path against security configuration"""
        abs_path = os.path.abspath(file_path)

        # Check blocked directories
        for blocked_dir in self.blocked_dirs:
            if abs_path.startswith(os.path.abspath(blocked_dir)):
                print(f"🚫 Blocked directory: {blocked_dir}")
                return False

        # Check allowed directories
        allowed = False
        for allowed_dir in self.allowed_dirs:
            if abs_path.startswith(os.path.abspath(allowed_dir)):
                allowed = True
                break

        if not allowed:
            print(f"🚫 Directory not in allowed list: {os.path.dirname(abs_path)}")
            return False

        # Check file extension
        file_ext = os.path.splitext(file_path)[1]
        if file_ext not in self.allowed_extensions:
            print(f"🚫 File extension not allowed: {file_ext}")
            return False

        print(f"✅ File path validated: {file_path}")
        return True

    def create_java_file(self, file_path: str, content: str):
        """Create Java file with security validation"""
        if not self.validate_file_path(file_path):
            raise PermissionError(f"File path not allowed: {file_path}")

        # Check file size
        content_size_mb = len(content.encode('utf-8')) / (1024 * 1024)
        if content_size_mb > self.max_file_size_mb:
            raise ValueError(f"File too large: {content_size_mb:.2f}MB > {self.max_file_size_mb}MB")

        # Create backup if file exists and backup is enabled
        if os.path.exists(file_path) and self.enable_backup:
            backup_path = f"{file_path}.bak"
            with open(file_path, 'r') as original:
                backup_content = original.read()
            with open(backup_path, 'w') as backup:
                backup.write(backup_content)
            print(f"📄 Backup created: {backup_path}")

        # Create the file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)

        print(f"✅ File created: {file_path}")
        return os.path.abspath(file_path)


class EnhancedMemoryManager:
    """
    Example of how to integrate MemoryManager with learning configuration
    """

    def __init__(self, config_manager: ConfigManager = None):
        self.config = config_manager or ConfigManager()

        # Load learning settings
        self.max_memory_entries = self.config.get('main', 'max_memory_entries')
        self.enable_learning = self.config.get('learning', 'ai_learning.enable_learning')
        self.pattern_threshold = self.config.get('learning', 'ai_learning.pattern_recognition_threshold')
        self.enable_feedback = self.config.get('learning', 'feedback_system.enable_user_feedback')

        # Load storage path
        storage_dir = "data/memory_db/"
        self.storage_dir = storage_dir

        print(f"🧠 Enhanced Memory Manager initialized:")
        print(f"   Max entries: {self.max_memory_entries}")
        print(f"   Learning enabled: {self.enable_learning}")
        print(f"   Pattern threshold: {self.pattern_threshold}")
        print(f"   Feedback enabled: {self.enable_feedback}")

    def store_interaction(self, user_input: str, generated_code: str, feedback: dict = None):
        """Store interaction with learning configuration applied"""
        if not self.enable_learning:
            print("📝 Learning disabled, skipping storage")
            return None

        # Here you would implement the actual storage logic
        # using the configuration settings
        memory_id = f"mem_{hash(user_input) % 10000:04d}"

        if self.enable_feedback and feedback:
            print(f"📊 Storing interaction with feedback: {memory_id}")
        else:
            print(f"📝 Storing interaction: {memory_id}")

        return memory_id


class EnhancedCLIInterface:
    """
    Example of how to update CLI interface to use all configuration systems
    """

    def __init__(self):
        # Initialize configuration manager
        self.config = ConfigManager()

        # Initialize enhanced components
        self.llm = EnhancedLLMEngine(self.config)
        self.file_manager = EnhancedFileManager(self.config)
        self.memory = EnhancedMemoryManager(self.config)

        # Load CLI-specific settings
        self.safe_mode = self.config.safe_mode
        self.debug_mode = self.config.debug_mode
        self.auto_save = self.config.get('user_preferences', 'workflow.auto_save')
        self.confirm_overwrites = self.config.get('user_preferences', 'workflow.confirm_overwrites')

        print(f"💻 Enhanced CLI Interface initialized:")
        print(f"   Safe mode: {self.safe_mode}")
        print(f"   Debug mode: {self.debug_mode}")
        print(f"   Auto save: {self.auto_save}")
        print(f"   Confirm overwrites: {self.confirm_overwrites}")

    def handle_command(self, command: str, output_path: str = None):
        """Handle command with full configuration integration"""
        try:
            print(f"\n🚀 Processing command: {command[:50]}...")

            # Generate code using configured LLM
            generated_code = self.llm.generate_code(command)

            # Handle file operations if output path provided
            if output_path:
                if self.confirm_overwrites and os.path.exists(output_path):
                    response = input(f"File exists: {output_path}. Overwrite? (y/n): ")
                    if response.lower() != 'y':
                        print("❌ Operation cancelled by user")
                        return None, None

                # Use enhanced file manager with security
                file_path = self.file_manager.create_java_file(output_path, generated_code)

                if self.auto_save:
                    print("✅ Auto-save enabled, file saved automatically")

            # Store in memory with learning settings
            memory_id = self.memory.store_interaction(command, generated_code)

            print(f"✅ Command processed successfully")
            return generated_code, memory_id

        except Exception as e:
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            print(f"❌ Error processing command: {e}")
            return None, None


def demonstrate_integration():
    """Demonstrate the integrated configuration system"""
    print("🔗 VoidClientAI Configuration Integration Demo")
    print("=" * 60)

    # Create enhanced CLI interface
    cli = EnhancedCLIInterface()

    # Test command processing
    print("\n📝 Testing command processing...")
    code, memory_id = cli.handle_command(
        "create a simple block class for emerald ore",
        "src/main/java/com/example/EmeraldOre.java"
    )

    if code and memory_id:
        print(f"✅ Generated code length: {len(code)} characters")
        print(f"✅ Memory ID: {memory_id}")

    # Show configuration summary
    print("\n📊 Configuration Summary:")
    summary = cli.config.get_config_summary()
    for config_type in summary['loaded_configs']:
        print(f"   ✅ {config_type} configuration loaded")

    print("\n🎉 Integration demonstration complete!")


if __name__ == "__main__":
    demonstrate_integration()