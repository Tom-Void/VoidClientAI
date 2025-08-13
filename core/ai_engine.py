# core/ai_engine.py
"""
Central AI Engine Orchestrator for VoidClientAI
Coordinates all AI operations, manages context, and orchestrates code generation
"""

import logging
import time
import gc
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from core.config_manager import ConfigManager
from core.memory_manager import MemoryManager

# Try to import LLM integration, fallback if not available
try:
    from core.llm_integration import LLMEngine
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️ LLM integration not available - AI Engine will use fallback mode")


class TaskType(Enum):
    """Types of AI tasks that can be performed"""
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    ERROR_FIXING = "error_fixing"
    CODE_OPTIMIZATION = "code_optimization"
    PATTERN_RECOGNITION = "pattern_recognition"
    DOCUMENTATION = "documentation"


class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AITask:
    """Represents an AI task to be processed"""
    task_id: str
    task_type: TaskType
    priority: Priority
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: float = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


@dataclass
class AIResult:
    """Represents the result of an AI task"""
    task_id: str
    success: bool
    result: Any
    execution_time: float
    context_used: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class AIEngine:
    """
    Central AI Engine that orchestrates all AI operations
    """

    def __init__(self, config_manager: ConfigManager = None):
        """Initialize the AI Engine with all subsystems"""
        self.config = config_manager or ConfigManager()
        self.logger = logging.getLogger(__name__)

        # Initialize core components
        self._initialize_components()

        # Task management
        self.task_queue = []
        self.active_tasks = {}
        self.completed_tasks = {}

        # Performance tracking
        self.stats = {
            'tasks_completed': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0,
            'success_rate': 0.0,
            'cache_hits': 0,
            'context_switches': 0
        }

        self.logger.info("AI Engine initialized successfully")

    def _initialize_components(self):
        """Initialize all AI engine components"""
        try:
            # Initialize LLM Engine with configuration if available
            if LLM_AVAILABLE:
                model_path = self.config.model_path
                self.llm_engine = LLMEngine(model_path=model_path)
                self.has_llm = True
            else:
                self.has_llm = False

            # Initialize Memory Manager
            self.memory_manager = MemoryManager()

            # Load generation settings from configuration
            self.generation_config = {
                'max_new_tokens': self.config.get('performance', 'generation_settings.max_new_tokens', 256),
                'temperature': self.config.get('performance', 'generation_settings.temperature', 0.7),
                'top_p': self.config.get('performance', 'generation_settings.top_p', 0.9),
                'top_k': self.config.get('performance', 'generation_settings.top_k', 50),
                'repetition_penalty': self.config.get('performance', 'generation_settings.repetition_penalty', 1.1),
                'do_sample': self.config.get('performance', 'generation_settings.do_sample', True)
            }

            self.logger.info("AI Engine components initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize AI Engine components: {e}")
            raise

    def generate_code(self, 
                     user_input: str, 
                     context_type: str = "general",
                     priority: Priority = Priority.NORMAL,
                     additional_context: Dict[str, Any] = None) -> AIResult:
        """Generate code with intelligent context management"""
        task_id = f"gen_{int(time.time())}_{hash(user_input) % 10000:04d}"

        task = AITask(
            task_id=task_id,
            task_type=TaskType.CODE_GENERATION,
            priority=priority,
            input_data={
                'user_input': user_input,
                'context_type': context_type,
                'additional_context': additional_context or {}
            }
        )

        return self._execute_task(task)

    def _execute_task(self, task: AITask) -> AIResult:
        """Execute an AI task with proper context and error handling"""
        start_time = time.time()

        try:
            self.logger.debug(f"Executing task {task.task_id} of type {task.task_type.value}")

            # Add to active tasks
            self.active_tasks[task.task_id] = task

            # Execute based on task type
            if task.task_type == TaskType.CODE_GENERATION:
                result = self._execute_code_generation(task)
            else:
                raise ValueError(f"Unsupported task type: {task.task_type}")

            execution_time = time.time() - start_time

            # Create successful result
            ai_result = AIResult(
                task_id=task.task_id,
                success=True,
                result=result,
                execution_time=execution_time,
                confidence=0.8,  # Default confidence
                metadata={
                    'task_type': task.task_type.value,
                    'has_llm': self.has_llm
                }
            )

            # Update statistics
            self._update_stats(ai_result)

            # Move to completed tasks
            self.completed_tasks[task.task_id] = ai_result
            del self.active_tasks[task.task_id]

            return ai_result

        except Exception as e:
            execution_time = time.time() - start_time

            # Create error result
            ai_result = AIResult(
                task_id=task.task_id,
                success=False,
                result=None,
                execution_time=execution_time,
                error_message=str(e),
                metadata={'task_type': task.task_type.value}
            )

            # Update statistics
            self._update_stats(ai_result)

            # Move to completed tasks
            self.completed_tasks[task.task_id] = ai_result
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]

            self.logger.error(f"Task {task.task_id} failed: {e}")

            return ai_result

    def _execute_code_generation(self, task: AITask) -> str:
        """Execute code generation task"""
        user_input = task.input_data['user_input']

        if self.has_llm:
            # Use LLM engine
            generated_code = self.llm_engine.generate_code(user_input)
        else:
            # Simple fallback generation
            generated_code = self._simple_fallback_generation(user_input)

        return generated_code

    def _simple_fallback_generation(self, user_input: str) -> str:
        """Simple fallback when LLM is not available"""
        # Extract class name
        words = user_input.split()
        class_name = "GeneratedClass"

        if words:
            class_name = words[0].capitalize()
            if "block" in user_input.lower():
                class_name += "Block"
            elif "item" in user_input.lower():
                class_name += "Item"

        if "block" in user_input.lower():
            return f"""package com.example.mod.blocks;

import net.minecraft.block.Block;
import net.minecraft.block.Material;
import net.fabricmc.fabric.api.object.builder.v1.block.FabricBlockSettings;

/**
 * Generated for: {user_input}
 */
public class {class_name} extends Block {{

    public {class_name}() {{
        super(FabricBlockSettings.of(Material.STONE)
            .strength(3.0f, 3.0f)
        );
    }}
}}"""
        elif "item" in user_input.lower():
            return f"""package com.example.mod.items;

import net.minecraft.item.Item;
import net.minecraft.item.ItemGroup;
import net.fabricmc.fabric.api.item.v1.FabricItemSettings;

/**
 * Generated for: {user_input}
 */
public class {class_name} extends Item {{

    public {class_name}() {{
        super(new FabricItemSettings()
            .group(ItemGroup.MISC)
        );
    }}
}}"""
        else:
            return f"""package com.example.mod;

/**
 * Generated for: {user_input}
 */
public class {class_name} {{

    public {class_name}() {{
        // Constructor implementation
    }}

    // Add your implementation here
}}"""

    def _update_stats(self, result: AIResult):
        """Update performance statistics"""
        self.stats['tasks_completed'] += 1
        self.stats['total_execution_time'] += result.execution_time
        self.stats['average_execution_time'] = (
            self.stats['total_execution_time'] / self.stats['tasks_completed']
        )

        success_count = sum(1 for r in self.completed_tasks.values() if r.success)
        self.stats['success_rate'] = success_count / len(self.completed_tasks) if self.completed_tasks else 0.0

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        return {
            **self.stats,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'has_llm_engine': self.has_llm
        }
