# integration_examples.py
"""
Integration examples for VoidClientAI Phase 1.2
"""

from core.config_manager import ConfigManager
from core.ai_engine import AIEngine, Priority
from core.context_manager import ContextManager
from core.code_generator import CodeGenerator, GenerationRequest
from core.memory_manager import MemoryManager
from core.file_operations import FileManager
import logging
import time
import re


class EnhancedCLIInterface:
    """Enhanced CLI Interface with Phase 1.2 capabilities"""

    def __init__(self):
        """Initialize with new AI Engine system"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize configuration
        self.config = ConfigManager()

        # Try to initialize AI Engine
        try:
            self.ai_engine = AIEngine(self.config)
            self.has_ai_engine = True
            self.logger.info("🤖 AI Engine initialized successfully")
        except Exception as e:
            self.logger.warning(f"⚠️ AI Engine unavailable: {e}")
            # Initialize fallback components
            self.context_manager = ContextManager(self.config)
            self.code_generator = CodeGenerator(self.config)
            self.memory_manager = MemoryManager()
            self.has_ai_engine = False

        # Initialize file manager
        self.file_manager = FileManager()

        # Load settings
        self.safe_mode = self.config.safe_mode
        self.debug_mode = self.config.debug_mode

        print("✅ Enhanced CLI Interface ready!")
        print(f"   AI Engine: {'Available' if self.has_ai_engine else 'Fallback mode'}")
        print(f"   Safe Mode: {self.safe_mode}")
        print(f"   Debug Mode: {self.debug_mode}")

    def handle_command_enhanced(self, command: str, output_path: str = None) -> tuple:
        """Enhanced command handling"""
        start_time = time.time()

        try:
            print(f"\n🚀 Processing: {command}")

            if self.has_ai_engine:
                result = self._handle_with_ai_engine(command, output_path)
            else:
                result = self._handle_with_fallback(command, output_path)

            execution_time = time.time() - start_time
            print(f"✅ Completed in {execution_time:.2f} seconds")

            return result

        except Exception as e:
            self.logger.error(f"Command handling failed: {e}")
            return None, {'error': str(e)}

    def _handle_with_ai_engine(self, command: str, output_path: str = None) -> tuple:
        """Handle command using AI Engine"""
        context_type = self._detect_context_type(command)

        result = self.ai_engine.generate_code(
            user_input=command,
            context_type=context_type,
            priority=Priority.NORMAL
        )

        if not result.success:
            raise Exception(result.error_message or "Code generation failed")

        generated_code = result.result

        if output_path:
            self._save_code_to_file(generated_code, output_path)

        print(f"📋 Generated {len(generated_code)} characters")
        print(f"⏱️ Execution time: {result.execution_time:.2f}s")
        print(f"🎯 Confidence: {result.confidence:.2f}")

        return generated_code, {
            'execution_time': result.execution_time,
            'confidence': result.confidence,
            'context_type': context_type,
            'ai_engine_used': True
        }

    def _handle_with_fallback(self, command: str, output_path: str = None) -> tuple:
        """Handle command using fallback components"""
        pattern = self.code_generator.detect_pattern(command)
        context_type = self._detect_context_type(command)

        request = GenerationRequest(
            request_id=f"cli_{int(time.time())}",
            user_input=command,
            pattern_type=pattern,
            context_type=context_type
        )

        result = self.code_generator.generate_code_enhanced(request)
        generated_code = result.generated_code

        if output_path:
            self._save_code_to_file(generated_code, output_path)

        if hasattr(self.memory_manager, 'store_interaction'):
            self.memory_manager.store_interaction(command, generated_code)

        print(f"📋 Generated {len(generated_code)} characters")
        print(f"🎯 Pattern: {pattern.value if pattern else 'General'}")
        print(f"⭐ Quality: {result.quality_score:.2f}")

        if result.suggestions:
            print("💡 Suggestions:")
            for suggestion in result.suggestions[:3]:
                print(f"   • {suggestion}")

        return generated_code, {
            'pattern': pattern.value if pattern else None,
            'quality_score': result.quality_score,
            'suggestions': result.suggestions,
            'fallback_mode': True
        }

    def _detect_context_type(self, command: str) -> str:
        """Detect context type from command"""
        command_lower = command.lower()

        if any(word in command_lower for word in ['block', 'ore', 'stone']):
            return 'block'
        elif any(word in command_lower for word in ['item', 'tool', 'sword']):
            return 'item'
        elif any(word in command_lower for word in ['entity', 'mob']):
            return 'entity'
        else:
            return 'general'

    def _save_code_to_file(self, code: str, output_path: str):
        """Save code to file with security checks"""
        try:
            saved_path = self.file_manager.create_java_file(output_path, code)
            print(f"💾 Saved to: {saved_path}")
        except Exception as e:
            print(f"❌ Failed to save file: {e}")

    def interactive_mode_enhanced(self):
        """Enhanced interactive mode"""
        print("\n" + "="*60)
        print("🤖 VoidClientAI Enhanced Interactive Mode")
        print("="*60)
        print("Type 'help' for commands, 'exit' to quit")
        print("="*60)

        while True:
            try:
                command = input("\n🎯 What would you like to create?\n> ").strip()

                if command.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break

                elif command.lower() in ['help', 'h']:
                    print("\n📚 Commands:")
                    print("  help - Show this help")
                    print("  exit - Exit the program")
                    print("\n🎯 Examples:")
                    print("  create a diamond block")
                    print("  make an emerald sword")
                    continue

                elif not command:
                    continue

                # Generate code
                code, metadata = self.handle_command_enhanced(command)

                if code:
                    save_choice = input("\n💾 Save to file? (y/n): ").strip()
                    if save_choice.lower() == 'y':
                        file_path = "src/main/java/com/example/Generated.java"
                        self._save_code_to_file(code, file_path)

            except KeyboardInterrupt:
                print("\n⚠️ Operation cancelled")
                continue
            except Exception as e:
                print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 VoidClientAI Phase 1.2 Integration Examples")
    print("="*50)

    try:
        cli = EnhancedCLIInterface()

        print("\n🎯 Testing code generation...")
        code, metadata = cli.handle_command_enhanced("create a simple emerald block")

        if code:
            print("✅ Enhanced CLI working correctly!")
            print(f"Generated {len(code)} characters")

    except Exception as e:
        print(f"⚠️ Test completed with some limitations: {e}")

    print("\n🎉 Integration examples complete!")
