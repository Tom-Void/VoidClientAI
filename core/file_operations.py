import os
import re


class FileManager:
    @staticmethod
    def create_java_file(file_path, content):
        # Create directories if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        return os.path.abspath(file_path)

    @staticmethod
    def parse_generated_code(llm_output):
        """Extract clean Java code from LLM output"""
        # Try to find generated code section
        pattern = r"// GENERATED JAVA CODE\s*(.*?)(?:// \w+|\Z)"
        matches = re.search(pattern, llm_output, re.DOTALL)
        if matches:
            return matches.group(1).strip()

        # Fallback: return the whole output
        return llm_output

    @staticmethod
    def backup_original(file_path):
        """Create backup before modification"""
        if os.path.exists(file_path):
            backup_path = f"{file_path}.bak"
            with open(file_path, 'r') as original:
                content = original.read()
            with open(backup_path, 'w') as backup:
                backup.write(content)
            return backup_path
        return None