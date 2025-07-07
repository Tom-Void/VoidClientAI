import argparse
import os
import sys
import re
from datetime import datetime
from core.llm_integration import LLMEngine
from core.memory_manager import MemoryManager
from core.file_operations import FileManager
import torch

class CLIInterface:
    def __init__(self, safe_mode=True):
        try:
            # Point to your downloaded model
            model_path = "/models/CodeLlama-7b-hf"
            self.llm = LLMEngine(model_path=model_path)

            # Initialize memory manager
            self.memory = MemoryManager()

            self.safe_mode = safe_mode
            self.operation_log = []

            print("✅ System ready")
        except Exception as e:
            print(f"🔴 Failed to initialize AI engine: {str(e)}")
            sys.exit(1)

    def log_operation(self, action, details):
        """Record all system actions with timestamps"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        self.operation_log.append(entry)
        print(f"[LOG] {action}: {details}")

    def get_user_consent(self, action_description):
        """Interactive consent prompt"""
        if not self.safe_mode:
            return True

        print(f"\n⚠️ ACTION REQUIRES CONSENT ⚠️")
        print(f"Proposed action: {action_description}")
        response = input("Allow this action? (y/n/d=details): ").lower()

        while response not in ['y', 'n']:
            if response == 'd':
                print("\nAction details:")
                print("\n".join(f"- {log['action']}: {log['details']}"
                                for log in self.operation_log[-3:]))
            response = input("Please confirm (y/n): ").lower()

        return response == 'y'

    def validate_file_path(self, path):
        """Prevent path traversal and unsafe locations"""
        if not path.endswith('.java'):
            raise ValueError("Only .java files can be generated")

        abs_path = os.path.abspath(path)
        safe_dirs = [
            os.path.abspath('src/main/java'),
            os.path.abspath('generated')
        ]

        if not any(abs_path.startswith(safe_dir) for safe_dir in safe_dirs):
            raise PermissionError(f"File creation restricted to approved directories: {safe_dirs}")
        return abs_path

    def handle_command(self, command, output_path=None):
        try:
            # Step 0: Log initiation
            self.log_operation("Process started", f"Command: {command[:50]}...")

            # Step 1: Generate code
            print("\n🤖 AI Thinking...")
            self.log_operation("LLM Processing", "Generating code response")
            generated_code = self.llm.generate_code(command)

            # Step 2: Handle file operations with consent
            if output_path:
                try:
                    abs_path = self.validate_file_path(output_path)

                    if os.path.exists(abs_path):
                        action_desc = f"Overwrite existing file: {abs_path}"
                        if not self.get_user_consent(action_desc):
                            raise PermissionError("User denied file overwrite")

                        FileManager.backup_original(abs_path)
                        self.log_operation("Backup created", f"Original saved to {abs_path}.bak")

                    action_desc = f"Create new file at: {abs_path}"
                    if self.get_user_consent(action_desc):
                        final_path = FileManager.create_java_file(abs_path, generated_code)
                        self.log_operation("File created", final_path)
                        print(f"\n✅ Generated code saved to: {final_path}")
                    else:
                        print("\n❌ File creation canceled by user")
                        return None, None
                except (ValueError, PermissionError) as e:
                    self.log_operation("Security Blocked", str(e))
                    print(f"\n🔒 Security restriction: {e}")
                    return None, None

            # Step 3: Store in memory
            memory_id = self.memory.store_interaction(command, generated_code)
            self.log_operation("Memory stored", f"ID: {memory_id}")

            # Display generated code
            print("\n🧾 Generated Code:")
            print("-" * 50)
            print(generated_code[:1000])  # Show first 1000 characters
            if len(generated_code) > 1000:
                print("... (truncated)")
            print("-" * 50)

            return generated_code, memory_id

        except Exception as e:
            self.log_operation("System Error", str(e))
            print(f"\n💥 Critical error: {e}", file=sys.stderr)
            return None, None


# Add to LLMEngine class
def _adaptive_context_loading(self, user_input):
    """Load only relevant context based on user request"""
    context_keywords = {
        'block': 'block_api_context.txt',
        'item': 'item_api_context.txt',
        'entity': 'entity_api_context.txt',
        'event': 'event_api_context.txt'
    }

    relevant_contexts = []
    for keyword, file in context_keywords.items():
        if keyword in user_input.lower():
            relevant_contexts.append(self._load_context_file(file))

    return '\n'.join(relevant_contexts) if relevant_contexts else self.minecraft_context

def setup_arg_parser():
    """Configure the argument parser with all options"""
    parser = argparse.ArgumentParser(
        description='Minecraft AI Coding Assistant',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'command',
        nargs='?',
        default=None,
        help='Coding command (e.g. "create block entity for furnace")'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output file path (must be within project/src/main/java/)'
    )
    parser.add_argument(
        '--unsafe',
        action='store_true',
        default=False,
        help='Disable safety checks (NOT RECOMMENDED)'
    )
    return parser


def interactive_mode(cli):
    """Handles the interactive command loop"""
    print("\n" + "=" * 50)
    print("INTERACTIVE MODE (type 'exit' to quit)")
    print("=" * 50)

    while True:
        try:
            command = input("\nWhat would you like to create?\n> ").strip()

            if command.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break

            if not command:
                continue

            save_choice = input("Save to file? (y/n): ").lower()
            output_path = None
            if save_choice == 'y':
                default_path = "src/main/java/com/example/Generated.java"
                output_path = input(f"File path [{default_path}]: ").strip() or default_path

            cli.handle_command(command, output_path)

        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            break
        except Exception as e:
            print(f"\n⚠️ Error during command: {str(e)}")


def main():
    try:
        parser = setup_arg_parser()
        args = parser.parse_args()

        # Initialize CLI interface
        cli = CLIInterface(safe_mode=not args.unsafe)

        if args.command:
            # Command-line mode
            cli.handle_command(args.command, args.output)
        else:
            # Interactive mode
            interactive_mode(cli)

    except Exception as e:
        print(f"\n💥 Critical error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Free resources before starting
    import gc

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    main()