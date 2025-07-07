import os
import torch
import re
import gc
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
import warnings


class LLMEngine:
    def __init__(self, model_path="C:/Coding/VoidClientAI/CodeLlama-7b-hf"):
        try:
            print(f"🚀 Using local model at: {model_path}")

            # Clear memory before loading
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Initialize tokenizer
            print("🔄 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)

            # Set padding token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                print("🔧 Set pad_token to eos_token")

            # Initialize model
            print("🔄 Loading model...")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"⚙️ Using device: {self.device}")

            # Use float16 for GPU, float32 for CPU
            torch_dtype = torch.float16 if self.device == "cuda" else torch.float32

            # Load model with low memory footprint
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch_dtype,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )

            # Move to device if not using device_map
            if self.device != "cuda":
                self.model.to(self.device)

            print("✅ AI model ready")
            self.minecraft_context = self._load_minecraft_context()

        except Exception as e:
            raise RuntimeError(f"Model initialization failed: {str(e)}")

    def _load_minecraft_context(self):
        """Load optimized Minecraft context"""
        try:
            context_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'minecraft_api', 'fabric_context.txt')
            context_path = os.path.abspath(context_path)

            if os.path.exists(context_path):
                with open(context_path, 'r') as f:
                    content = f.read()
                    # Use simple compression
                    compressed = self._simple_compress_context(content)
                    print(f"Loaded Minecraft context ({len(compressed)} chars)")
                    return compressed
            print("⚠️ Using default Minecraft context")
            return "// Basic Minecraft context"
        except Exception as e:
            warnings.warn(f"Couldn't load Minecraft context: {str(e)}")
            return "// Basic Minecraft context"

    def _simple_compress_context(self, context):
        """Simple context compression without complex regex"""
        # Remove single-line comments
        lines = context.split('\n')
        clean_lines = []
        for line in lines:
            if '//' in line:
                line = line.split('//')[0]
            clean_lines.append(line.strip())

        # Join and remove multi-line comments
        compressed = ' '.join(clean_lines)
        while '/*' in compressed and '*/' in compressed:
            start = compressed.index('/*')
            end = compressed.index('*/', start) + 2
            compressed = compressed[:start] + compressed[end:]

        # Remove excessive whitespace
        compressed = re.sub(r'\s+', ' ', compressed)
        return compressed[:2000]  # Limit to 2000 characters

    def generate_code(self, user_input, max_new_tokens=128):
        """Generate Java code with resource constraints"""
        try:
            # Optimize context
            optimized_context = self._simple_compress_context(self.minecraft_context)

            prompt = f"""// MINECRAFT CONTEXT
{optimized_context}

// USER REQUEST
{user_input}

// GENERATED JAVA CODE
"""

            print("\n🤖 Generating code...")
            start_time = time.time()

            # Tokenize with strict limits
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,  # Reduced token limit
                return_attention_mask=True
            ).to(self.device)

            # Generate with resource limits
            outputs = self.model.generate(
                input_ids=inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                top_p=0.9,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                do_sample=True
            )

            # Decode output
            full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Log generation time
            gen_time = time.time() - start_time
            print(f"✅ Generation completed in {gen_time:.1f}s")

            # Extract generated code
            generated_code = self._extract_generated_code(full_output)

            # Clean up resources immediately
            del inputs
            del outputs
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            return generated_code

        except Exception as e:
            print(f"⚠️ Generation error: {str(e)}")
            return "// Error during code generation"

    def _extract_generated_code(self, full_output):
        """Extract only the generated code portion"""
        # Find the start of the generated code
        start_marker = "// GENERATED JAVA CODE"
        code_start = full_output.find(start_marker)

        if code_start == -1:
            # Fallback: return everything after the last marker
            markers = ["// MINECRAFT CONTEXT", "// USER REQUEST"]
            last_marker_pos = max(full_output.rfind(m) for m in markers)
            if last_marker_pos != -1:
                return full_output[last_marker_pos + len(markers[0]):].strip()
            return full_output

        code_start += len(start_marker)
        generated_code = full_output[code_start:].strip()

        # Remove any trailing context
        end_markers = ["// END", "// USER REQUEST", "// MINECRAFT CONTEXT"]
        for marker in end_markers:
            if marker in generated_code:
                generated_code = generated_code.split(marker)[0].strip()
                break

        return generated_code