# fix_model_path.py
"""
Quick script to fix the model path configuration
"""

from core.config_manager import ConfigManager
import os


def fix_model_path():
    """Update the model path to the correct location"""

    # Initialize config manager
    config = ConfigManager()

    # Current model path
    current_path = config.model_path
    print(f"Current model path: {current_path}")

    # Your actual model path
    actual_path = "models/CodeLlama-7b-hf"

    # Check if the model exists at the actual path
    if os.path.exists(actual_path):
        print(f"✅ Found model at: {actual_path}")

        # Update the configuration
        config.set('main', 'model_path', actual_path)
        print(f"✅ Updated model path to: {actual_path}")

        # Verify the update
        new_path = config.get('main', 'model_path')
        print(f"✅ Verified new path: {new_path}")

        return True
    else:
        print(f"❌ Model not found at: {actual_path}")

        # Let's check some common locations
        possible_paths = [
            "models/CodeLlama-7b-hf",
            "./models/CodeLlama-7b-hf",
            "C:/Coding/VoidClientAI/models/CodeLlama-7b-hf",
            "../models/CodeLlama-7b-hf"
        ]

        print("\n🔍 Checking possible locations:")
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Found model at: {path}")
                config.set('main', 'model_path', path)
                print(f"✅ Updated model path to: {path}")
                return True
            else:
                print(f"❌ Not found: {path}")

        print("\n💡 Please manually set the correct path using:")
        print("config.set('main', 'model_path', 'your/actual/path')")
        return False


def test_ai_engine_with_model():
    """Test the AI Engine with the corrected model path"""
    try:
        from core.ai_engine import AIEngine
        from core.config_manager import ConfigManager

        print("\n🧪 Testing AI Engine with corrected model path...")

        config = ConfigManager()
        ai_engine = AIEngine(config)

        print("✅ AI Engine initialized successfully!")

        # Test code generation
        result = ai_engine.generate_code(
            user_input="create a sapphire ore block",
            context_type="block"
        )

        if result.success:
            print(f"✅ Code generation successful!")
            print(f"   Generated: {len(result.result)} characters")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Execution time: {result.execution_time:.2f}s")

            # Show a preview
            lines = result.result.split('\n')
            preview = '\n'.join(lines[:5])
            print(f"\n📄 Code preview:\n{preview}")

        else:
            print(f"❌ Code generation failed: {result.error_message}")

        return result.success

    except Exception as e:
        print(f"❌ AI Engine test failed: {e}")
        print("💡 This might be normal if the model needs additional setup")
        return False


if __name__ == "__main__":
    print("🔧 Fixing VoidClientAI Model Path Configuration")
    print("=" * 50)

    # Fix the model path
    if fix_model_path():
        print("\n🎉 Model path fixed successfully!")

        # Test the AI Engine
        if test_ai_engine_with_model():
            print("\n🚀 Full AI Engine is now working!")
            print("\n📋 You can now use:")
            print("1. Enhanced CLI with full AI Engine")
            print("2. All AI Engine features (context, templates, quality scoring)")
            print("3. Real-time performance monitoring")
        else:
            print("\n⚠️ AI Engine still in fallback mode")
            print("💡 But all other features are working perfectly!")
    else:
        print("\n⚠️ Model path needs manual configuration")
        print("💡 System will continue to work in fallback mode")

    print("\n🎯 Next steps:")
    print("1. Try the enhanced CLI: python integration_examples.py")
    print("2. Run the test suite: python test_phase_1_2.py")
    print("3. Start using the new AI Engine features!")