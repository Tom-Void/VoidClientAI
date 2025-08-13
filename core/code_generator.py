# core/code_generator.py
"""
Enhanced Code Generator for VoidClientAI (Simplified Version)
"""

import re
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from core.config_manager import ConfigManager


class CodePattern(Enum):
    """Common Minecraft modding code patterns"""
    BASIC_BLOCK = "basic_block"
    BASIC_ITEM = "basic_item"
    ENTITY = "entity"
    GENERAL = "general"


@dataclass
class GenerationRequest:
    """Represents a code generation request"""
    request_id: str
    user_input: str
    pattern_type: Optional[CodePattern] = None
    context_type: str = "general"
    additional_context: Dict[str, Any] = None


@dataclass
class GenerationResult:
    """Represents the result of code generation"""
    request_id: str
    generated_code: str
    pattern_detected: Optional[CodePattern] = None
    quality_score: float = 0.0
    suggestions: List[str] = None
    metadata: Dict[str, Any] = None


class CodeGenerator:
    """Enhanced code generator with pattern recognition"""

    def __init__(self, config_manager: ConfigManager = None):
        """Initialize the code generator"""
        self.config = config_manager or ConfigManager()
        self.logger = logging.getLogger(__name__)

        # Pattern keywords for detection
        self.pattern_keywords = {
            CodePattern.BASIC_BLOCK: ['block', 'blocks', 'stone', 'wood', 'ore'],
            CodePattern.BASIC_ITEM: ['item', 'items', 'tool', 'weapon', 'sword'],
            CodePattern.ENTITY: ['entity', 'mob', 'creature'],
            CodePattern.GENERAL: ['mod', 'class', 'general']
        }

        self.logger.info("Enhanced Code Generator initialized")

    def detect_pattern(self, user_input: str) -> Optional[CodePattern]:
        """Detect the most likely code pattern from user input"""
        user_input_lower = user_input.lower()
        pattern_scores = {}

        for pattern, keywords in self.pattern_keywords.items():
            score = sum(1 for keyword in keywords if keyword in user_input_lower)
            if score > 0:
                pattern_scores[pattern] = score

        if pattern_scores:
            best_pattern = max(pattern_scores.items(), key=lambda x: x[1])
            return best_pattern[0]

        return CodePattern.GENERAL

    def generate_code_enhanced(self, request: GenerationRequest) -> GenerationResult:
        """Enhanced code generation with pattern detection"""
        try:
            # Detect pattern if not specified
            detected_pattern = request.pattern_type or self.detect_pattern(request.user_input)

            # Generate code based on pattern
            generated_code = self._generate_by_pattern(request.user_input, detected_pattern)

            # Calculate quality score
            quality_score = self._calculate_quality_score(generated_code)

            # Generate suggestions
            suggestions = self._generate_suggestions(generated_code, detected_pattern)

            return GenerationResult(
                request_id=request.request_id,
                generated_code=generated_code,
                pattern_detected=detected_pattern,
                quality_score=quality_score,
                suggestions=suggestions,
                metadata={'pattern_used': detected_pattern.value}
            )

        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return GenerationResult(
                request_id=request.request_id,
                generated_code=f"// Generation failed: {str(e)}",
                quality_score=0.0,
                suggestions=[],
                metadata={'error': True}
            )

    def _generate_by_pattern(self, user_input: str, pattern: CodePattern) -> str:
        """Generate code based on detected pattern"""
        class_name = self._extract_class_name(user_input, pattern)

        if pattern == CodePattern.BASIC_BLOCK:
            return self._generate_block_code(class_name, user_input)
        elif pattern == CodePattern.BASIC_ITEM:
            return self._generate_item_code(class_name, user_input)
        elif pattern == CodePattern.ENTITY:
            return self._generate_entity_code(class_name, user_input)
        else:  # GENERAL
            return self._generate_general_code(class_name, user_input)

    def _generate_block_code(self, class_name: str, user_input: str) -> str:
        """Generate block code"""
        template = """package com.example.mod.blocks;

import net.minecraft.block.Block;
import net.minecraft.block.Material;
import net.minecraft.sound.BlockSoundGroup;
import net.fabricmc.fabric.api.object.builder.v1.block.FabricBlockSettings;

/**
 * {class_name} - Generated for: {user_input}
 */
public class {class_name} extends Block {{

    public {class_name}() {{
        super(FabricBlockSettings.of(Material.STONE)
            .strength(3.0f, 3.0f)
            .sounds(BlockSoundGroup.STONE)
        );
    }}
}}"""
        return template.format(class_name=class_name, user_input=user_input)

    def _generate_item_code(self, class_name: str, user_input: str) -> str:
        """Generate item code"""
        template = """package com.example.mod.items;

import net.minecraft.item.Item;
import net.minecraft.item.ItemGroup;
import net.fabricmc.fabric.api.item.v1.FabricItemSettings;

/**
 * {class_name} - Generated for: {user_input}
 */
public class {class_name} extends Item {{

    public {class_name}() {{
        super(new FabricItemSettings()
            .group(ItemGroup.MISC)
        );
    }}
}}"""
        return template.format(class_name=class_name, user_input=user_input)

    def _generate_entity_code(self, class_name: str, user_input: str) -> str:
        """Generate entity code"""
        template = """package com.example.mod.entities;

import net.minecraft.entity.EntityType;
import net.minecraft.entity.mob.PathAwareEntity;
import net.minecraft.world.World;

/**
 * {class_name} - Generated for: {user_input}
 */
public class {class_name} extends PathAwareEntity {{

    public {class_name}(EntityType<? extends PathAwareEntity> entityType, World world) {{
        super(entityType, world);
    }}
}}"""
        return template.format(class_name=class_name, user_input=user_input)

    def _generate_general_code(self, class_name: str, user_input: str) -> str:
        """Generate general code"""
        template = """package com.example.mod;

/**
 * {class_name} - Generated for: {user_input}
 */
public class {class_name} {{

    public {class_name}() {{
        // Constructor implementation
    }}

    // Add your implementation here
}}"""
        return template.format(class_name=class_name, user_input=user_input)

    def _extract_class_name(self, user_input: str, pattern: CodePattern) -> str:
        """Extract appropriate class name from user input"""
        # Look for capitalized words first
        words = re.findall(r'\b[A-Z][a-zA-Z]*\b', user_input)
        if words:
            base_name = words[0]
        else:
            # Extract from first word
            first_word = user_input.split()[0] if user_input.split() else "Generated"
            base_name = first_word.capitalize()

        # Add appropriate suffix
        if pattern == CodePattern.BASIC_BLOCK and not base_name.endswith('Block'):
            return base_name + 'Block'
        elif pattern == CodePattern.BASIC_ITEM and not base_name.endswith('Item'):
            return base_name + 'Item'
        elif pattern == CodePattern.ENTITY and not base_name.endswith('Entity'):
            return base_name + 'Entity'

        return base_name

    def _calculate_quality_score(self, code: str) -> float:
        """Calculate a quality score for generated code"""
        score = 0.5  # Base score

        if 'package ' in code: score += 0.1
        if 'import ' in code: score += 0.1
        if 'class ' in code: score += 0.2
        if '/**' in code: score += 0.15  # Javadoc
        if 'public ' in code: score += 0.05

        return min(score, 1.0)

    def _generate_suggestions(self, code: str, pattern: CodePattern) -> List[str]:
        """Generate suggestions for improving the code"""
        suggestions = []

        if '/**' not in code:
            suggestions.append("Consider adding Javadoc documentation")

        if pattern == CodePattern.BASIC_BLOCK and 'Registry.register' not in code:
            suggestions.append("Don't forget to register your block in your mod initializer")
        elif pattern == CodePattern.BASIC_ITEM and 'Registry.register' not in code:
            suggestions.append("Don't forget to register your item in your mod initializer")

        return suggestions

    def get_generator_stats(self) -> Dict[str, Any]:
        """Get code generator statistics"""
        return {
            'total_templates': 3,  # Simplified
            'patterns_supported': len(self.pattern_keywords)
        }
