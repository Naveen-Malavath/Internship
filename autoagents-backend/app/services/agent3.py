"""Agent-3 service responsible for Mermaid diagram generation."""

from __future__ import annotations

import datetime
import json
import logging
import os
import re
import unicodedata
from typing import Any, Dict, List

import anthropic
from anthropic import APIError
from bson import ObjectId
from fastapi import HTTPException

from .claude_client import (
    DEFAULT_CLAUDE_MODEL,
    extract_text,
    get_claude_client,
)

logger = logging.getLogger(__name__)


class Agent3Service:
    """Service wrapper for generating Mermaid diagrams via Claude."""

    def __init__(self, model: str | None = None) -> None:
        # Priority: explicit model > CLAUDE_MODEL_DEBUG > CLAUDE_MODEL > default
        debug_model = os.getenv("CLAUDE_MODEL_DEBUG")
        if model is None and debug_model:
            self.model = debug_model
            logger.info(f"[agent3] Using DEBUG model from CLAUDE_MODEL_DEBUG: {self.model}")
        else:
            self.model = model or os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)
            logger.info(f"[agent3] Initialized with Claude Sonnet 4.5 model: {self.model}")

    async def generate_mermaid(
        self,
        project_title: str,
        features: List[Dict],
        stories: List[Dict],
        diagram_type: str = "hld",
        original_prompt: str = "",
    ) -> str:
        """Generate a Mermaid diagram linking project features and stories.
        
        Args:
            project_title: Title of the project
            features: List of feature dictionaries from Agent1
            stories: List of story dictionaries from Agent2
            diagram_type: Type of diagram to generate - 'hld' (High Level Design), 
                         'lld' (Low Level Design), or 'database' (Database Design)
            original_prompt: Original user prompt for context
        
        Returns:
            Mermaid diagram source code as string
        """
        logger.info(f"[agent3] 🎨 Starting COLORED Mermaid diagram generation | model={self.model} | type={diagram_type.upper()} | features={len(features)} | stories={len(stories)} | prompt_length={len(original_prompt)}")
        logger.debug(f"[agent3] Project Title: '{project_title}'")
        try:
            client = get_claude_client()
            logger.debug("[agent3] Claude client obtained successfully")
        except RuntimeError as exc:
            logger.error(f"[agent3] Failed to get Claude client: {exc}", exc_info=True)
            raise

        # Format features with more detail
        feature_details = []
        for idx, feature in enumerate(features, 1):
            feature_text = feature.get('feature_text') or feature.get('title') or f'Feature {idx}'
            feature_details.append(f"{idx}. {feature_text}")

        # Format stories grouped by feature
        stories_by_feature = {}
        for story in stories:
            feature_id = story.get('feature_id') or 'unknown'
            if feature_id not in stories_by_feature:
                stories_by_feature[feature_id] = []
            story_text = story.get('story_text') or story.get('user_story') or 'Story'
            stories_by_feature[feature_id].append(story_text)

        story_outline = "\n".join(
            f"- Feature {fid}: " + "\n  - ".join(story_list[:3])  # Limit to 3 stories per feature
            for fid, story_list in list(stories_by_feature.items())[:10]  # Limit to 10 features
        )

        # Include original prompt context
        prompt_context = ""
        if original_prompt and original_prompt.strip():
            prompt_context = f"\n\nOriginal User Requirements:\n{original_prompt.strip()}\n\n"
        
        # Create type-specific prompts with COLORED diagrams
        if diagram_type.lower() == "lld":
            system_prompt = (
                "You are Agent-3, an AI software architect specializing in Low Level Design (LLD). "
                "You create DETAILED technical diagrams showing classes, methods, properties, relationships, "
                "and implementation details. LLD is MORE DETAILED than HLD - show specific classes, methods, "
                "and technical implementation for each feature. Use Mermaid classDiagram syntax."
            )
            user_prompt = (
                f"Project: {project_title or 'Untitled Project'}\n"
                f"{prompt_context}"
                f"Features to implement:\n" + "\n".join(feature_details) + "\n\n"
                f"User Stories context:\n{story_outline or 'None'}\n\n"
                "Create a DETAILED LOW LEVEL DESIGN (LLD) Mermaid classDiagram showing:\n\n"
                "📋 WHAT TO INCLUDE (based on features above):\n"
                "1. **Controllers/API Layer** - For each feature, create specific controller classes:\n"
                "   - Map features to RESTful API endpoints\n"
                "   - Example: UserController, ProductController, OrderController\n"
                "   - Methods: +createResource(), +getResource(), +updateResource(), +deleteResource()\n\n"
                "2. **Service Layer** - Business logic classes for each feature:\n"
                "   - Map each feature to a service class\n"
                "   - Example: UserService, ProductService, OrderService\n"
                "   - Methods: +processBusinessLogic(), +validateData(), +applyBusinessRules()\n"
                "   - Fields: -repository: Repository, -validator: Validator\n\n"
                "3. **Repository Layer** - Data access for each entity:\n"
                "   - Create repository classes for data operations\n"
                "   - Example: UserRepository, ProductRepository\n"
                "   - Methods: +findById(), +save(), +update(), +delete(), +findAll()\n\n"
                "4. **Model/Entity Classes** - Domain objects:\n"
                "   - Extract entities from features and stories\n"
                "   - Example: User, Product, Order, Payment\n"
                "   - Properties: -id: UUID, -name: String, -email: String, -createdAt: DateTime\n\n"
                "5. **Relationships** - Show how classes interact:\n"
                "   - Controller --> Service (dependency)\n"
                "   - Service --> Repository (dependency)\n"
                "   - Repository --> Entity (manages)\n"
                "   - Service --> Entity (uses)\n\n"
                "⚠️ CRITICAL SYNTAX REQUIREMENTS:\n"
                "```\n"
                "classDiagram\n"
                "  class ClassName {\n"
                "    -privateField: Type\n"
                "    +publicMethod() ReturnType\n"
                "  }\n"
                "```\n"
                "- Each class MUST have { and } on separate lines\n"
                "- ALL methods and properties MUST be INSIDE { }\n"
                "- NEVER EVER put members outside a class block\n"
                "- Close each class with } before starting relationships\n"
                "- Members MUST be inside braces with 4-space indent\n"
                "- Visibility: + (public), - (private), # (protected)\n\n"
                "❌ WRONG EXAMPLE:\n"
                "```\n"
                "classDiagram\n"
                "  class MyService {\n"
                "    +method1()\n"
                "  }\n"
                "  +method2()  ← WRONG! This is outside the class!\n"
                "```\n\n"
                "✅ CORRECT EXAMPLE:\n"
                "```\n"
                "classDiagram\n"
                "  class MyService {\n"
                "    +method1()\n"
                "    +method2()\n"
                "  }\n"
                "```\n\n"
                "🎨 STYLING (Subtle professional colors):\n"
                "```\n"
                "classDef controllerClass fill:#E3F2FD,stroke:#1976D2,stroke-width:2px,color:#000000\n"
                "classDef serviceClass fill:#FFF3E0,stroke:#F57C00,stroke-width:2px,color:#000000\n"
                "classDef repoClass fill:#E8F5E9,stroke:#388E3C,stroke-width:2px,color:#000000\n"
                "classDef modelClass fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px,color:#000000\n"
                "```\n"
                "- Use pastel fills with darker stroke colors\n"
                "- Apply with :::className after class name\n"
                "- Example: UserController:::controllerClass\n\n"
                "Output ONLY valid Mermaid classDiagram code, no explanations."
            )
        elif diagram_type.lower() == "database":
            system_prompt = (
                "You are Agent-3, an AI database architect. You create DETAILED database schemas showing "
                "all tables, fields, data types, constraints, and relationships needed to implement the features. "
                "Analyze features to identify entities, create comprehensive database design with proper normalization."
            )
            user_prompt = (
                f"Project: {project_title or 'Untitled Project'}\n"
                f"{prompt_context}"
                f"Features to implement:\n" + "\n".join(feature_details) + "\n\n"
                f"User Stories context:\n{story_outline or 'None'}\n\n"
                "Create a DETAILED DATABASE DESIGN (DBD) Mermaid erDiagram showing:\n\n"
                "📋 WHAT TO INCLUDE (based on features above):\n"
                "1. **Identify Core Entities** from features:\n"
                "   - Extract nouns from feature descriptions (User, Product, Order, Payment, etc.)\n"
                "   - Create a table for each core business entity\n"
                "   - Include common fields: id (PK), created_at, updated_at\n\n"
                "2. **Define Fields** for each entity:\n"
                "   - Map feature requirements to database columns\n"
                "   - Use appropriate data types:\n"
                "     * uuid for IDs\n"
                "     * varchar for short text (names, emails, status)\n"
                "     * text for long content\n"
                "     * int for counts/quantities\n"
                "     * float for prices/amounts\n"
                "     * boolean for flags\n"
                "     * timestamp/datetime for dates\n"
                "     * json for complex data\n"
                "   - Add constraints: PK (Primary Key), FK (Foreign Key), UK (Unique Key)\n\n"
                "3. **Define Relationships** between entities:\n"
                "   - One-to-Many: PARENT ||--o{ CHILD : has\n"
                "   - Many-to-Many: TABLE1 }o--o{ TABLE2 : links\n"
                "   - One-to-One: TABLE1 ||--|| TABLE2 : owns\n"
                "   - Label relationships clearly (owns, contains, belongs_to, has, manages)\n\n"
                "4. **Common Patterns** to include:\n"
                "   - USER table for authentication/profiles\n"
                "   - Audit fields: created_at, updated_at, created_by, updated_by\n"
                "   - Status fields for workflow tracking\n"
                "   - Foreign keys linking related entities\n"
                "   - Junction tables for many-to-many relationships\n\n"
                "Example based on e-commerce features:\n"
                "```\n"
                "erDiagram\n"
                "  USER ||--o{ ORDER : places\n"
                "  ORDER ||--o{ ORDER_ITEM : contains\n"
                "  PRODUCT ||--o{ ORDER_ITEM : included_in\n"
                "  \n"
                "  USER {\n"
                "    uuid id PK\n"
                "    varchar email UK\n"
                "    varchar name\n"
                "    varchar password_hash\n"
                "    timestamp created_at\n"
                "  }\n"
                "  \n"
                "  ORDER {\n"
                "    uuid id PK\n"
                "    uuid user_id FK\n"
                "    float total_amount\n"
                "    varchar status\n"
                "    timestamp created_at\n"
                "  }\n"
                "```\n\n"
                "⚠️ CRITICAL SYNTAX REQUIREMENTS:\n"
                "- Entity definitions: ENTITY_NAME { ... }\n"
                "- Each entity MUST have opening { and closing } on separate lines\n"
                "- ALL fields MUST be INSIDE { } braces\n"
                "- NEVER EVER put fields outside an entity block\n"
                "- Close each entity with } before starting relationships\n"
                "- Fields format: datatype fieldname constraint\n"
                "- NO QUOTES in field definitions or relationship labels\n"
                "- Relationships: ENTITY1 ||--o{ ENTITY2 : label (no quotes)\n\n"
                "❌ WRONG EXAMPLE:\n"
                "```\n"
                "erDiagram\n"
                "  USER {\n"
                "    uuid id PK\n"
                "  }\n"
                "  varchar name  ← WRONG! This is outside!\n"
                "```\n\n"
                "✅ CORRECT EXAMPLE:\n"
                "```\n"
                "erDiagram\n"
                "  USER {\n"
                "    uuid id PK\n"
                "    varchar name\n"
                "  }\n"
                "```\n\n"
                "🎨 STYLING (Subtle professional colors):\n"
                "- Use pastel fills with darker borders\n"
                "- Example:\n"
                "```\n"
                "classDef coreEntity fill:#E3F2FD,stroke:#1976D2,stroke-width:2px\n"
                "classDef userEntity fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px\n"
                "classDef txEntity fill:#FFF3E0,stroke:#F57C00,stroke-width:2px\n"
                "```\n"
                "- Apply: USER:::userEntity, PRODUCT:::coreEntity\n\n"
                "Output ONLY valid Mermaid erDiagram code, no explanations."
            )
        else:  # Default to HLD
            system_prompt = (
                "You are Agent-3, an AI solution architect specializing in High Level Design (HLD). "
                "Generate COLORED Mermaid diagrams showing system architecture, high-level components, "
                "and business flow at a conceptual level. Use professional colors and styling."
            )
            user_prompt = (
                f"Project: {project_title or 'Untitled Project'}\n"
                f"{prompt_context}"
                f"Features from Agent1:\n" + "\n".join(feature_details) + "\n\n"
                f"User Stories from Agent2:\n{story_outline or 'None'}\n\n"
                "Create a COLORED HIGH LEVEL DESIGN (HLD) Mermaid diagram showing:\n"
                "- System architecture and major components\n"
                "- Business process flow from features to stories\n"
                "- High-level interactions between system modules\n"
                "- User journey through features\n"
                "- Use flowchart (graph TD or graph LR) syntax\n\n"
                "🎨 STYLING REQUIREMENTS (MANDATORY):\n"
                "- Define classDef styles at the END of the diagram with vibrant colors:\n"
                "  * User/Client nodes (e.g., classDef userClass fill:#E1F5FE,stroke:#01579B,stroke-width:3px,color:#000)\n"
                "  * Frontend/UI (e.g., classDef frontendClass fill:#E8EAF6,stroke:#3F51B5,stroke-width:2px,color:#000)\n"
                "  * Backend/API (e.g., classDef backendClass fill:#FFF9C4,stroke:#F57F17,stroke-width:2px,color:#000)\n"
                "  * Database (e.g., classDef dbClass fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#000)\n"
                "  * External Services/AI (e.g., classDef externalClass fill:#F8BBD0,stroke:#C2185B,stroke-width:2px,color:#000)\n"
                "  * Process/Logic (e.g., classDef processClass fill:#FFE0B2,stroke:#E65100,stroke-width:2px,color:#000)\n"
                "- Apply styles to nodes using ':::className' syntax\n"
                "- Example: User[\"👤 User\"]:::userClass\n\n"
                "Output ONLY valid Mermaid code, no explanations."
            )

        try:
            # Use reasonable max_tokens to avoid streaming requirement (SDK limits non-streaming to ~10 minutes)
            # For complex diagrams, 16K tokens is sufficient and avoids the 10-minute timeout requirement
            max_tokens = 16000  # Sweet spot: allows large diagrams without requiring streaming
            logger.info(f"[agent3] Attempting API call | model={self.model} | max_tokens={max_tokens} | temperature=0.3")
            logger.debug(f"[agent3] System prompt length: {len(system_prompt)} chars")
            logger.debug(f"[agent3] User prompt length: {len(user_prompt)} chars")
            response = await client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for faster, more focused responses
                timeout=600.0,  # 10 minute timeout for complex diagram generation
                system=system_prompt,
                messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
            )
            usage = getattr(response, "usage", None)
            if usage:
                logger.info(f"[agent3] API call successful | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}")
                # Check if response was likely truncated (within 5% of limit)
                if usage.output_tokens >= max_tokens * 0.95:
                    logger.warning(f"[agent3] ⚠️ Response may be truncated (used {usage.output_tokens}/{max_tokens} tokens)")
                # Also warn if using more than 80% - approaching limit
                elif usage.output_tokens >= max_tokens * 0.80:
                    logger.info(f"[agent3] ℹ️ Response used {usage.output_tokens}/{max_tokens} tokens (80%+ of limit)")
            else:
                logger.info("[agent3] API call successful")
        except APIError as exc:
            error_type = getattr(exc, 'type', 'unknown')
            error_status = getattr(exc, 'status_code', None)
            logger.error(f"[agent3] APIError - Type: {error_type}, Status: {error_status}, Message: {str(exc)}", exc_info=True)
            raise RuntimeError(f"Agent-3 failed to generate diagram: {exc}") from exc

        logger.debug("[agent3] Extracting Mermaid diagram from response")
        mermaid = extract_text(response).strip()
        
        # Clean up mermaid code - remove markdown fences if present
        if mermaid.startswith("```"):
            logger.debug("[agent3] Removing markdown code fences from response")
            lines = mermaid.split("\n")
            if lines[0].startswith("```mermaid"):
                mermaid = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
            elif lines[0].strip() == "```":
                mermaid = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        mermaid = mermaid.strip()
        
        # Remove emojis from all node labels to prevent parse errors
        # This is a common source of Mermaid parse errors
        def remove_emojis(text: str) -> str:
            """Remove emojis and other non-ASCII symbols that can break Mermaid parsing."""
            # Remove emojis and other symbols that might break parsing
            # Keep only ASCII printable characters, newlines, and common punctuation
            result = []
            for char in text:
                # Keep ASCII printable (32-126), newline (10), tab (9)
                if ord(char) < 128 and (char.isprintable() or char in '\n\t'):
                    result.append(char)
                # Replace emojis and other non-ASCII with space
                elif unicodedata.category(char) in ['So', 'Sk', 'Sm']:  # Symbol, Modifier, Mark
                    result.append(' ')
                else:
                    result.append(' ')
            return ''.join(result)
        
        # Apply emoji removal to node labels (inside quotes and brackets)
        # Pattern: Node["Label with emoji"] or Node[("Label with emoji")]
        def clean_node_labels(line: str) -> str:
            """Remove emojis from node labels while preserving structure."""
            # Match node definitions with labels: NodeID["label"] or NodeID[("label")]
            # Pattern to match: identifier["text"] or identifier[("text")]
            # Also handle cases with <br/> tags
            pattern = r'(\w+)\[\(?"([^"]*)"\)?\]'
            def replace_label(match):
                node_id = match.group(1)
                label = match.group(2)
                cleaned_label = remove_emojis(label).strip()
                # Also remove any remaining problematic characters from label
                # Keep alphanumeric, spaces, and safe punctuation
                cleaned_label = re.sub(r'[^\w\s\-_.,;:()\[\]<>/]', ' ', cleaned_label)
                cleaned_label = ' '.join(cleaned_label.split())  # Normalize spaces
                # Remove backslashes to prevent escape sequence issues
                cleaned_label = cleaned_label.replace('\\', '')
                # Escape internal quotes properly
                cleaned_label = cleaned_label.replace('"', "'")  # Replace double quotes with single quotes
                # Preserve the original bracket style
                original = match.group(0)
                if '[("' in original:
                    return f'{node_id}[("{cleaned_label}")]'
                else:
                    return f'{node_id}["{cleaned_label}"]'
            return re.sub(pattern, replace_label, line)
        
        # Clean all lines - remove emojis from node labels
        lines = mermaid.split('\n')
        cleaned_lines = [clean_node_labels(line) for line in lines]
        mermaid = '\n'.join(cleaned_lines)
        
        # Also clean erDiagram entity names (they don't use quotes but can have emojis)
        # Pattern: ENTITY_NAME { or ENTITY_NAME ||--o{ OTHER_ENTITY
        er_diagram_pattern = r'^(\s*)([A-Z_][A-Z_0-9]*)\s*(\{|\|\|--o\{|\}o--o\{)'
        def clean_er_entity(match):
            indent = match.group(1)
            entity_name = match.group(2)
            connector = match.group(3)
            # Remove emojis from entity name
            cleaned_name = remove_emojis(entity_name).strip().replace(' ', '_').upper()
            # Ensure it's a valid identifier
            cleaned_name = re.sub(r'[^A-Z_0-9]', '', cleaned_name)
            if not cleaned_name:
                cleaned_name = 'ENTITY'
            return f'{indent}{cleaned_name} {connector}'
        
        # Apply erDiagram cleaning if it's an erDiagram
        if 'erdiagram' in mermaid.lower() or 'entityrelationshipdiagram' in mermaid.lower():
            lines = mermaid.split('\n')
            er_cleaned = []
            for line in lines:
                if re.match(er_diagram_pattern, line, re.IGNORECASE):
                    er_cleaned.append(re.sub(er_diagram_pattern, clean_er_entity, line, flags=re.IGNORECASE))
                else:
                    # Also clean relationship lines: ENTITY1 ||--o{ ENTITY2 : "relationship"
                    # Remove quotes from relationship labels as they can cause issues
                    line = re.sub(r'([\|\}o][\{\|o])(\s*:\s*)"([^"]*)"', r'\1\2\3', line)
                    er_cleaned.append(line)
            mermaid = '\n'.join(er_cleaned)
        
        # Replace special characters that can break parsing
        # Replace & with 'and' in node labels
        mermaid = re.sub(r'(\["[^"]*)"&([^"]*"\])', r'\1"and\2', mermaid)
        mermaid = re.sub(r'(\[\(?"[^"]*)"&([^"]*"\)?\])', r'\1"and\2', mermaid)
        
        # Check for truncated or malformed style statements throughout the diagram
        lines = mermaid.split('\n') if mermaid else []
        fixed_lines = []
        removed_lines = []
        
        # Detect diagram type ONCE at the start for better detection
        diagram_type_detected = None
        for check_line in lines[:10]:
            check_stripped = check_line.strip().lower()
            if 'erdiagram' in check_stripped or 'entityrelationshipdiagram' in check_stripped:
                diagram_type_detected = 'er'
                break
            elif 'classdiagram' in check_stripped:
                diagram_type_detected = 'class'
                break
        
        logger.info(f"[agent3] 🔍 Detected diagram type: {diagram_type_detected or 'unknown'}")
        
        for index, (line_num, line) in enumerate(zip(range(1, len(lines) + 1), lines)):
            line_stripped = line.strip()
            
            # Skip empty lines
            if not line_stripped:
                fixed_lines.append(line)
                continue
            
            # Check for incomplete classDef or style statements
            if "classDef" in line or line_stripped.startswith("style "):
                # Valid endings for style definitions
                valid_endings = ("px", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", 
                                "a", "b", "c", "d", "e", "f", "A", "B", "C", "D", "E", "F",
                                ")", "bold", "italic", "normal", "lighter", "bolder", ";")
                
                is_incomplete = False
                
                # Check for truncated property names - these are ALWAYS incomplete
                # Use regex to detect truncated properties more accurately
                truncated_property_patterns = [
                    (r'stroke-widt(?!h)', 'stroke-width'),  # stroke-widt but not stroke-width
                    (r'stroke-wid(?!th)', 'stroke-width'),  # stroke-wid but not stroke-width
                    (r'stroke-w(?!idth)', 'stroke-width'),  # stroke-w but not stroke-width
                    (r'font-weigh(?!t)', 'font-weight'),    # font-weigh but not font-weight
                    (r'font-siz(?!e)', 'font-size'),        # font-siz but not font-size
                    (r'font-famil(?!y)', 'font-family'),    # font-famil but not font-family
                    (r'border-radi(?!us)', 'border-radius'),  # border-radi but not border-radius
                    (r'stroke-das(?!harray)', 'stroke-dasharray'),  # stroke-das but not stroke-dasharray
                ]
                
                for pattern_regex, property_name in truncated_property_patterns:
                    if re.search(pattern_regex, line):
                        logger.warning(f"[agent3] ⚠️ Detected truncated property '{property_name}' at line {line_num}")
                        is_incomplete = True
                        break
                
                # Check for incomplete color values (hex colors should be 3 or 6 digits)
                # Match incomplete hex patterns: #X, #XX, #XXXX, #XXXXX (not 3 or 6)
                # IMPORTANT: In classDef/style context, we need FULL 6-digit hex colors
                # 3-digit shorthand (#fff, #000) can be ambiguous if truncated
                
                # Check for style/classDef lines with hex colors
                if 'classdef' in line_stripped.lower() or line_stripped.lower().startswith('style '):
                    # In style definitions, hex colors MUST be 6 digits (Mermaid requirement)
                    # Find all hex color patterns
                    hex_colors = re.findall(r'#([0-9A-Fa-f]+)(?:[,\s}]|$)', line_stripped)
                    for hex_val in hex_colors:
                        hex_len = len(hex_val)
                        # Only accept 6-digit hex colors in style definitions
                        # 3-digit shorthand is NOT reliable (could be truncated from 6)
                        if hex_len != 6:
                            logger.warning(f"[agent3] ⚠️ Detected incomplete hex color #{hex_val} ({hex_len} digits) in style at line {line_num}")
                            logger.warning(f"[agent3]    Style definitions require 6-digit hex colors, found {hex_len} digits")
                            is_incomplete = True
                            break
                else:
                    # For non-style lines, check for obviously incomplete hex colors
                    if re.search(r'#[0-9A-Fa-f]{1,2}(?:[,\s]|$)', line_stripped):
                        # Found 1-2 hex digits - definitely incomplete
                        logger.warning(f"[agent3] ⚠️ Detected incomplete hex color (1-2 digits) at line {line_num}")
                        is_incomplete = True
                    elif re.search(r'#[0-9A-Fa-f]{4,5}(?:[,\s]|$)', line_stripped):
                        # Found 4-5 hex digits - definitely incomplete
                        logger.warning(f"[agent3] ⚠️ Detected incomplete hex color (4-5 digits) at line {line_num}")
                        is_incomplete = True
                
                # Check for trailing commas or colons (incomplete lines)
                if line_stripped.endswith(',') or line_stripped.endswith(':'):
                    logger.warning(f"[agent3] ⚠️ Line ends with comma or colon at line {line_num}")
                    is_incomplete = True
                
                # Check for properties with missing or invalid values
                if ":" in line_stripped:
                    # Split by comma to check each property
                    properties = [p.strip() for p in line_stripped.split(',')]
                    for prop in properties:
                        if ':' in prop:
                            parts = prop.split(':', 1)
                            if len(parts) == 2:
                                prop_name = parts[0].strip()
                                prop_value = parts[1].strip()
                                
                                # Check if value is empty or suspiciously short
                                if not prop_value or len(prop_value) < 2:
                                    logger.warning(f"[agent3] ⚠️ Property '{prop_name}' has empty/short value at line {line_num}")
                                    is_incomplete = True
                                    break
                                
                                # Check if value ends with a dash (truncated)
                                if prop_value.endswith('-'):
                                    logger.warning(f"[agent3] ⚠️ Property value ends with dash at line {line_num}")
                                    is_incomplete = True
                                    break
                
                if is_incomplete:
                    logger.warning(f"[agent3] ⚠️ Removing incomplete style at line {line_num}: {line[:100]}")
                    removed_lines.append((line_num, line[:100]))
                    continue  # Skip this line
            
            # Check for malformed node labels
            # Look for patterns like: Node["Label<br/>Text"]  - these should not have extra closing quotes
            if '["' in line and '<br/>' in line:
                # Count quotes to ensure they're balanced
                quote_count = line.count('"')
                if quote_count % 2 != 0:
                    # Odd number of quotes - malformed
                    logger.warning(f"[agent3] ⚠️ Malformed label at line {line_num}: {line[:100]}")
                    removed_lines.append((line_num, line[:100]))
                    continue
            
            # Check for erDiagram entity attributes with quoted descriptions (emoji descriptions)
            # Pattern: datatype field_name KEY_TYPE "Description with emoji"
            # These cause parse errors - remove the quoted descriptions
            if diagram_type_detected == 'er':
                # Match: datatype fieldname PK/FK/UK "anything"
                if re.match(r'^\s*\w+\s+\w+\s+[A-Z]{2,}\s+"', line_stripped):
                    # Remove the quoted description part
                    cleaned = re.sub(r'\s+"[^"]*"', '', line)
                    logger.info(f"[agent3] 🔧 Cleaned erDiagram attribute description at line {line_num}")
                    fixed_lines.append(cleaned)
                    continue
                
                # Check for malformed relationship lines with extra closing braces
                # Pattern: "ENTITY : relationship    }        ANOTHER_ENTITY"
                # This happens when braces are misplaced in relationship definitions
                if ('||--' in line_stripped or '}o--' in line_stripped or 'o{--' in line_stripped or '}|--' in line_stripped):
                    # Check if there are stray braces or fields in the relationship line
                    # Valid format: ENTITY1 ||--o{ ENTITY2 : relationship_name
                    # Remove any trailing field definitions that don't belong
                    if re.search(r':\s*\w+\s*\}\s+(uuid|varchar|text|int|float)', line_stripped):
                        logger.warning(f"[agent3] ⚠️ Malformed relationship with trailing field at line {line_num}: {line_stripped[:80]}")
                        # Remove everything after the closing brace in relationship
                        cleaned = re.sub(r'(\}[^\}]*)\s+(uuid|varchar|text|int|float).*$', r'\1', line)
                        fixed_lines.append(cleaned)
                        continue
                
                # CRITICAL FIX: Detect orphaned entity fields (fields outside entity blocks)
                # BUT ONLY if we haven't already detected a completely malformed diagram
                # Check if there are any entity definitions at all
                has_any_entity_def = any(re.match(r'^[A-Z_][A-Z_0-9]*\s*\{', lines[j].strip()) for j in range(len(lines)))
                
                if has_any_entity_def:  # Only try to fix orphaned fields if there ARE some entity definitions
                    # Use SIMPLE state machine: track if we're currently inside an entity block
                    is_field_line = re.match(r'^\s*(uuid|varchar|text|int|float|boolean|datetime|timestamp|json|bigint|smallint|decimal|double|real|date|time)\s+\w+', line_stripped)
                    
                    if is_field_line:
                        # Simple forward-looking check: are we inside an entity block?
                        # Count all braces from the start of the diagram to current line
                        in_entity = False
                        brace_count = 0
                        
                        for i in range(index):
                            prev_line = lines[i].strip()
                            
                            # Check if this is an entity definition line
                            if re.match(r'^[A-Z_][A-Z_0-9]*\s*\{', prev_line):
                                brace_count += 1
                            
                            # Check for standalone opening brace
                            if prev_line == '{' and i > 0:
                                # Previous line should be entity name
                                entity_line = lines[i-1].strip()
                                if re.match(r'^[A-Z_][A-Z_0-9]*$', entity_line):
                                    brace_count += 1
                            
                            # Check for closing brace
                            if prev_line == '}' or prev_line.endswith('}'):
                                brace_count -= 1
                        
                        # If brace_count > 0, we're inside an entity block
                        in_entity = brace_count > 0
                        
                        # If we're not in an entity, this field is orphaned - REMOVE IT
                        if not in_entity:
                            logger.warning(f"[agent3] ⚠️ ORPHANED entity field outside entity block at line {line_num}: {line_stripped[:80]}")
                            removed_lines.append((line_num, line_stripped[:100]))
                            continue  # Skip this line completely
            
            # Check for classDiagram members appearing without class context
            # CRITICAL FIX: Detect orphaned class members (methods/properties outside class blocks)
            # BUT ONLY if we haven't already detected a completely malformed diagram
            # (the malformed diagram will be replaced with a fallback later)
            if diagram_type_detected == 'class':
                # Check if this is a fundamentally broken diagram (will be caught and fixed later)
                # If the ENTIRE diagram has no class definitions, don't try to fix individual lines
                # Just let it through so the later logic can generate a fallback
                has_any_class_def = any('class ' in lines[j] for j in range(len(lines)))
                
                if has_any_class_def:  # Only try to fix orphaned members if there ARE some class definitions
                    # Check if this line looks like a class member: +method(), -field, etc.
                    is_member_line = re.match(r'^\s*[+\-#~]\w', line_stripped)
                    
                    if is_member_line:
                        # Simple forward-looking check: are we inside a class block?
                        # Count all braces from the start of the diagram to current line
                        in_class = False
                        brace_count = 0
                        
                        for i in range(index):
                            prev_line = lines[i].strip()
                            
                            # Check if this is a class definition line with opening brace
                            if re.match(r'^class\s+\w+.*\{', prev_line):
                                brace_count += 1
                            
                            # Check for standalone opening brace after class definition
                            if prev_line == '{' and i > 0:
                                check_prev = lines[i-1].strip()
                                if check_prev.startswith('class '):
                                    brace_count += 1
                            
                            # Check for closing brace
                            if prev_line == '}':
                                brace_count -= 1
                        
                        # If brace_count > 0, we're inside a class block
                        in_class = brace_count > 0
                        
                        # If we're not in a class, this member is orphaned - REMOVE IT
                        if not in_class:
                            logger.warning(f"[agent3] ⚠️ ORPHANED class member outside class block at line {line_num}: {line_stripped[:80]}")
                            removed_lines.append((line_num, line_stripped[:100]))
                            continue  # Skip this line completely
            
            # Check for lines ending with opening bracket without content (orphaned nodes)
            # Pattern: ..."]  NodeID[ with nothing following or just whitespace
            if re.search(r'"\]\s+[A-Za-z0-9_]+\[\s*$', line_stripped):
                logger.warning(f"[agent3] ⚠️ Orphaned node opening bracket at line {line_num}: {line[:100]}")
                removed_lines.append((line_num, line[:100]))
                continue
            
            fixed_lines.append(line)
        
        if removed_lines:
            logger.warning(f"[agent3] 🧹 Removed {len(removed_lines)} orphaned/malformed line(s)")
            for line_num, line_preview in removed_lines:
                logger.debug(f"[agent3]   - Line {line_num}: {line_preview}")
        
        mermaid = '\n'.join(fixed_lines)
        
        # FINAL VALIDATION: Check for common structural issues
        logger.info("[agent3] 🔍 Performing final structural validation")
        
        # For classDiagram: Validate all classes have proper { } structure
        if 'classDiagram' in mermaid:
            lines = mermaid.split('\n')
            for i, line in enumerate(lines):
                stripped = line.strip()
                # Check if line starts with + - # ~ but we're not in a class
                if re.match(r'^[+\-#~]\w', stripped):
                    logger.error(f"[agent3] ❌ CRITICAL: Found orphaned member at line {i+1}: {stripped[:50]}")
                    logger.error(f"[agent3]    This should have been caught earlier - check detection logic")
        
        # For erDiagram: Validate all entities have proper { } structure  
        if 'erDiagram' in mermaid:
            lines = mermaid.split('\n')
            for i, line in enumerate(lines):
                stripped = line.strip()
                # Check if line looks like a field but we're not in an entity
                if re.match(r'^(uuid|varchar|text|int|float|boolean|datetime|timestamp|json)\s+\w+', stripped):
                    logger.error(f"[agent3] ❌ CRITICAL: Found orphaned field at line {i+1}: {stripped[:50]}")
                    logger.error(f"[agent3]    This should have been caught earlier - check detection logic")
            
            # Check if all entities are empty (fields were removed as orphaned)
            entity_pattern = r'^[A-Z_][A-Z_0-9]*\s*\{'
            field_pattern = r'^\s*(uuid|varchar|text|int|float|boolean|datetime|timestamp|json|bigint|smallint|decimal|double|real|date|time)\s+\w+'
            
            has_entities = any(re.match(entity_pattern, line.strip()) for line in lines)
            has_fields_in_entities = False
            
            logger.info(f"[agent3] 🔍 Checking erDiagram: has_entities={has_entities}")
            
            if has_entities:
                # Check if any entity actually has fields
                in_entity = False
                for line in lines:
                    stripped = line.strip()
                    if re.match(entity_pattern, stripped):
                        in_entity = True
                    elif stripped == '}':
                        in_entity = False
                    elif in_entity and re.match(field_pattern, stripped):
                        has_fields_in_entities = True
                        break
            
            logger.info(f"[agent3] 🔍 has_fields_in_entities={has_fields_in_entities}")
            
            # If all entities are empty, generate a fallback
            if has_entities and not has_fields_in_entities:
                logger.error("[agent3] ❌ CRITICAL: All entities are empty (all fields were orphaned)!")
                logger.error("[agent3] Generating fallback erDiagram with sample data")
                mermaid = """erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--o{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : included_in
    CATEGORY ||--o{ PRODUCT : categorizes
    
    USER {
        uuid id PK
        varchar email UK
        varchar name
        varchar password_hash
        timestamp created_at
        timestamp updated_at
    }
    
    PRODUCT {
        uuid id PK
        varchar name
        text description
        float price
        int stock_quantity
        uuid category_id FK
        timestamp created_at
    }
    
    CATEGORY {
        uuid id PK
        varchar name UK
        text description
    }
    
    ORDER {
        uuid id PK
        uuid user_id FK
        float total_amount
        varchar status
        timestamp created_at
    }
    
    ORDER_ITEM {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        float unit_price
        float subtotal
    }"""
                logger.info("[agent3] ✅ Generated fallback erDiagram with sample entities")
        
        # Fix classDiagram-specific syntax issues (LLD diagrams)
        # This handles the parse error: "Expecting 'PS', 'TAGEND', 'STR', got 'PE'"
        # which occurs when class members are on the same line or have invalid syntax
        if 'classDiagram' in mermaid or diagram_type.lower() == 'lld':
            logger.info("[agent3] 🔧 Fixing classDiagram syntax for LLD")
            class_lines = mermaid.split('\n')
            
            # CRITICAL CHECK: Is this diagram completely malformed (no class definitions at all)?
            has_class_defs = any(re.match(r'^\s*class\s+\w+', line) for line in class_lines)
            has_members = any(re.match(r'^\s*[+\-#~]\w', line.strip()) for line in class_lines)
            
            if has_members and not has_class_defs:
                logger.error("[agent3] ❌ CRITICAL: classDiagram has NO class definitions, only orphaned members!")
                logger.error("[agent3] This diagram is fundamentally malformed - generating fallback")
                # Generate a simple fallback classDiagram
                mermaid = """classDiagram
    class SystemController {
        +initialize()
        +processRequest()
        +handleResponse()
    }
    class ServiceLayer {
        +executeBusinessLogic()
        +validateData()
        +transformData()
    }
    class Repository {
        +findData()
        +saveData()
        +updateData()
        +deleteData()
    }
    class DomainModel {
        -id: UUID
        -createdAt: DateTime
        +getId()
        +isValid()
    }
    
    SystemController --> ServiceLayer : uses
    ServiceLayer --> Repository : delegates
    Repository --> DomainModel : manages
    
    classDef controllerClass fill:#E3F2FD,stroke:#1976D2,stroke-width:2px,color:#000000
    classDef serviceClass fill:#FFF3E0,stroke:#F57C00,stroke-width:2px,color:#000000
    classDef repoClass fill:#E8F5E9,stroke:#388E3C,stroke-width:2px,color:#000000
    classDef modelClass fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px,color:#000000
    
    class SystemController controllerClass
    class ServiceLayer serviceClass
    class Repository repoClass
    class DomainModel modelClass"""
                logger.info("[agent3] ✅ Generated fallback classDiagram with proper structure")
                # Skip the rest of the fixing logic since we have a new diagram
                class_lines = mermaid.split('\n')
            
            fixed_class_lines = []
            inside_class = False
            class_indent = ''
            
            for i, line in enumerate(class_lines):
                stripped = line.strip()
                
                # CRITICAL FIX: Check if classDiagram declaration has members on the same line or nearby
                # Pattern: "classDiagram    +renderCatalogManage" or "classDiagram    +method"
                if stripped.lower().startswith('classdiagram'):
                    # Check if there are class members on the same line (with any amount of whitespace)
                    member_match = re.search(r'classdiagram\s+([+\-#~].+)', stripped, re.IGNORECASE)
                    if member_match:
                        logger.warning(f"[agent3] ⚠️ classDiagram has inline members at line {i+1} - removing them")
                        # Keep only the classDiagram declaration
                        fixed_class_lines.append('classDiagram')
                        # Remove the inline members (they're orphaned and invalid)
                        logger.info(f"[agent3] 🔧 Removed invalid inline member from classDiagram: {member_match.group(1)[:50]}")
                        continue
                    else:
                        # Normal classDiagram line
                        fixed_class_lines.append(line)
                        continue
                
                # ADDITIONAL FIX: If this is right after classDiagram and looks like a member, skip it
                if i > 0 and class_lines[i-1].strip().lower() == 'classdiagram':
                    if re.match(r'^[+\-#~]\w', stripped):
                        logger.warning(f"[agent3] ⚠️ Orphaned member right after classDiagram at line {i+1}: {stripped[:50]}")
                        logger.info(f"[agent3] 🔧 Removed orphaned member: {stripped[:50]}")
                        continue
                
                # Track when we enter/exit a class definition
                if re.match(r'^class\s+\w+\s*\{', stripped):
                    inside_class = True
                    class_indent = '    '  # Standard 4-space indent for class members
                    fixed_class_lines.append(line)
                    continue
                elif stripped == '}':
                    inside_class = False
                    fixed_class_lines.append(line)
                    continue
                
                # Fix class members that are on the same line as other content
                # Pattern: +method1()        +method2() or +method()        +attribute
                if inside_class and re.search(r'[+\-#~]\w+\([^)]*\)\s{2,}[+\-#~]', stripped):
                    # Multiple members on same line - split them
                    # Match all members: +/-/#/~ followed by identifier and optional ()
                    member_pattern = r'([+\-#~]\w+(?:\([^)]*\))?)'
                    members = re.findall(member_pattern, stripped)
                    logger.info(f"[agent3] 🔧 Splitting {len(members)} class members from line {i+1}")
                    for member in members:
                        # Ensure methods have (), attributes don't
                        if '(' not in member and not member.endswith(')'):
                            # It's an attribute - leave as is
                            fixed_class_lines.append(f"{class_indent}{member}")
                        else:
                            # It's a method - ensure it has ()
                            if not member.endswith(')'):
                                member = member + '()'
                            fixed_class_lines.append(f"{class_indent}{member}")
                    continue
                
                # Fix individual member lines
                if inside_class and re.match(r'^\s*[+\-#~]', stripped):
                    # This is a class member
                    # Extract the member signature
                    match = re.match(r'^([+\-#~])(\w+)(?:\(([^)]*)\))?\s*(.*)?$', stripped)
                    if match:
                        visibility = match.group(1)
                        name = match.group(2)
                        params = match.group(3) if match.group(3) is not None else None
                        trailing = match.group(4) or ''
                        
                        # If params is None, it's an attribute; if params exists (even empty), it's a method
                        if params is not None:
                            # It's a method - ensure it has ()
                            member_line = f"{class_indent}{visibility}{name}({params})"
                        else:
                            # It's an attribute - no parentheses
                            # But check if trailing content suggests it should be a method
                            if trailing and re.match(r'^[+\-#~]', trailing):
                                # There's another member on the same line
                                logger.info(f"[agent3] 🔧 Splitting multiple members from line {i+1}")
                                member_line = f"{class_indent}{visibility}{name}"
                                fixed_class_lines.append(member_line)
                                # Process the trailing content on next iteration (add it to the list)
                                class_lines.insert(i + 1, trailing)
                                continue
                            else:
                                member_line = f"{class_indent}{visibility}{name}"
                        
                        fixed_class_lines.append(member_line)
                        continue
                
                # Keep all other lines as-is
                fixed_class_lines.append(line)
            
            mermaid = '\n'.join(fixed_class_lines)
            logger.info("[agent3] ✅ classDiagram syntax fixed")
            
            # CRITICAL SAFETY CHECK: Ensure we don't have malformed output like "classDiagram    }    }    }"
            # This happens when all class content is removed but closing braces remain
            if re.match(r'^classDiagram\s+(\}\s*)+$', mermaid.strip(), re.MULTILINE | re.DOTALL):
                logger.error("[agent3] ❌ Detected malformed classDiagram with only closing braces - regenerating fallback")
                # Generate a simple fallback classDiagram
                mermaid = """classDiagram
    class SystemComponent {
        +initialize()
        +process()
        +shutdown()
    }
    class DataService {
        +fetchData()
        +saveData()
    }
    class APIClient {
        +sendRequest()
        +handleResponse()
    }
    
    SystemComponent --> DataService
    DataService --> APIClient"""
                logger.info("[agent3] 🔧 Generated fallback classDiagram")
        
        # Final cleanup: remove any remaining problematic last line
        if mermaid:
            last_line = mermaid.split('\n')[-1].strip()
            if last_line and ("classDef" in last_line or "style " in last_line):
                # Check if it ends properly
                if not any(last_line.endswith(ending) for ending in ["px", "bold", "normal", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "A", "B", "C", "D", "E", "F"]):
                    logger.warning(f"[agent3] ⚠️ Final cleanup: removing incomplete last line: {last_line[:100]}")
                    mermaid = '\n'.join(mermaid.split('\n')[:-1])
        
        # Additional safety: Remove any Unicode characters that might break parsing
        # Keep only ASCII printable + newlines + tabs
        def sanitize_for_mermaid(text: str) -> str:
            """Remove all non-ASCII characters except basic punctuation."""
            result = []
            for char in text:
                # Keep ASCII printable (32-126) + newline (10) + tab (9)
                code = ord(char)
                if 32 <= code <= 126 or code in (9, 10):
                    result.append(char)
                else:
                    # Replace with space
                    result.append(' ')
            return ''.join(result)
        
        mermaid = sanitize_for_mermaid(mermaid)
        
        # Fix comma-separated class assignments (Mermaid doesn't support this syntax)
        # Transform: class Node1,Node2,Node3 className
        # Into: class Node1 className\nclass Node2 className\nclass Node3 className
        lines = mermaid.split('\n')
        fixed_class_lines = []
        for line in lines:
            stripped = line.strip()
            # Match pattern: class <comma-separated-nodes> <className>
            match = re.match(r'^(\s*)class\s+([A-Za-z0-9_,]+)\s+([A-Za-z0-9_]+)\s*$', line)
            if match and ',' in match.group(2):
                indent = match.group(1)
                nodes = match.group(2).split(',')
                class_name = match.group(3)
                logger.info(f"[agent3] 🔧 Splitting comma-separated class assignment: {len(nodes)} nodes with class '{class_name}'")
                # Create individual class assignments for each node
                for node in nodes:
                    node = node.strip()
                    if node:
                        fixed_class_lines.append(f"{indent}class {node} {class_name}")
            else:
                fixed_class_lines.append(line)
        mermaid = '\n'.join(fixed_class_lines)
        
        # Remove multiple consecutive spaces (but preserve indentation at line starts)
        lines = mermaid.split('\n')
        cleaned_lines = []
        for line in lines:
            # Preserve leading spaces, but compress multiple spaces in the middle
            leading_spaces = len(line) - len(line.lstrip())
            rest_of_line = ' '.join(line.split())
            if rest_of_line:
                cleaned_lines.append(' ' * leading_spaces + rest_of_line)
            else:
                cleaned_lines.append('')
        mermaid = '\n'.join(cleaned_lines)
        
        # ============================================================================
        # FINAL BULLETPROOF VALIDATION - Ensure diagram starts with valid type
        # ============================================================================
        valid_prefixes = ["graph", "classDiagram", "sequenceDiagram", "erDiagram", "entityRelationshipDiagram", "flowchart"]
        if not any(mermaid.startswith(prefix) for prefix in valid_prefixes):
            logger.warning("[agent3] Mermaid diagram doesn't start with valid type, prepending 'graph TD'")
            mermaid = f"graph TD\n{mermaid}"
        
        # ============================================================================
        # CRITICAL FIX: Remove any trailing incomplete syntax
        # ============================================================================
        lines = mermaid.split('\n')
        safe_lines = []
        for line in lines:
            stripped = line.strip()
            
            # Check if line is incomplete/malformed
            is_incomplete = False
            
            # Skip lines that are clearly incomplete or malformed
            if stripped.endswith('-->') or stripped.endswith('---') or stripped.endswith('-.-'):
                is_incomplete = True  # Incomplete arrow/connection
            elif stripped.endswith('[') or stripped.endswith('('):
                is_incomplete = True  # Unclosed bracket/paren
            elif stripped.endswith('{'):
                # Opening brace is OK for entity/class definitions
                # Valid patterns: "class ClassName {" or "ENTITY_NAME {"
                if not (re.match(r'^class\s+\w+\s*\{', stripped) or re.match(r'^[A-Z_][A-Z_0-9]*\s*\{', stripped)):
                    is_incomplete = True  # Invalid opening brace
            elif stripped.endswith('::'):
                is_incomplete = True  # Incomplete style application
            elif (stripped.startswith('style ') or stripped.startswith('classDef ')) and stripped.count(',') > 0 and not stripped.endswith(';'):
                is_incomplete = True  # Incomplete style definition
            
            if not is_incomplete:
                safe_lines.append(line)
            else:
                if stripped:  # Only log non-empty incomplete lines
                    logger.warning(f"[agent3] 🔧 Removed potentially incomplete line: {stripped[:80]}")
        
        mermaid = '\n'.join(safe_lines)
        
        # ============================================================================
        # ADDITIONAL SAFETY: Ensure all brackets and quotes are balanced
        # ============================================================================
        # Count brackets
        open_square = mermaid.count('[')
        close_square = mermaid.count(']')
        open_paren = mermaid.count('(')
        close_paren = mermaid.count(')')
        open_brace = mermaid.count('{')
        close_brace = mermaid.count('}')
        
        if open_square != close_square:
            logger.warning(f"[agent3] ⚠️ Unbalanced square brackets: [ {open_square} vs ] {close_square}")
        if open_paren != close_paren:
            logger.warning(f"[agent3] ⚠️ Unbalanced parentheses: ( {open_paren} vs ) {close_paren}")
        if open_brace != close_brace:
            logger.warning(f"[agent3] ⚠️ Unbalanced braces: {{ {open_brace} vs }} {close_brace}")
        
        # If erDiagram, ensure braces are balanced (entity definitions)
        if 'erDiagram' in mermaid or 'entityRelationshipDiagram' in mermaid:
            if open_brace != close_brace:
                logger.error(f"[agent3] ❌ erDiagram has unbalanced braces - this will cause parse errors")
                # Try to fix by removing incomplete entities
                lines = mermaid.split('\n')
                fixed_er = []
                in_entity = False
                for line in lines:
                    if '{' in line and '}' not in line:
                        in_entity = True
                        fixed_er.append(line)
                    elif '}' in line and '{' not in line:
                        in_entity = False
                        fixed_er.append(line)
                    elif not in_entity:
                        fixed_er.append(line)
                mermaid = '\n'.join(fixed_er)
        
        # Check if diagram contains styling (classDef)
        has_styling = "classDef" in mermaid or "style " in mermaid
        logger.info(f"[agent3] ✅ {diagram_type.upper()} diagram generation complete | length={len(mermaid)} chars | has_colors={has_styling}")
        
        if has_styling:
            logger.debug(f"[agent3] 🎨 Colored {diagram_type.upper()} diagram generated successfully with styling")
        else:
            logger.warning(f"[agent3] ⚠️ {diagram_type.upper()} diagram rendered without color styling for safety")
        
        # Log first 200 chars for debugging
        logger.debug(f"[agent3] Diagram preview: {mermaid[:200]}...")
        
        return mermaid


async def generate_diagram_for_project(project_id: str, db) -> Dict[str, Any]:
    """Generate and persist a Mermaid system diagram for a given project."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Claude API key not configured")

    client = anthropic.Anthropic(api_key=api_key)

    try:
        object_id = ObjectId(project_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid project ID") from exc

    project = await db["projects"].find_one({"_id": object_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    features_cursor = db["features"].find({"project_id": project_id}).sort("order_index", 1)
    features = await features_cursor.to_list(length=None)
    if not features:
        raise HTTPException(
            status_code=400, detail="No features found for this project. Run Agent-1 first."
        )

    stories_cursor = db["stories"].find({"project_id": project_id}).sort("created_at", 1)
    stories = await stories_cursor.to_list(length=None)

    project_title = project.get("title") or "Untitled Project"
    project_description = project.get("prompt") or project.get("description") or ""

    feature_lines = "\n".join(
        f"{idx}. {feature.get('feature_text') or feature.get('title') or 'Feature'}"
        for idx, feature in enumerate(features, start=1)
    )
    story_lines = "\n".join(
        f"{idx}. {story.get('story_text') or 'As a user, I want ...'}"
        for idx, story in enumerate(stories, start=1)
    )

    prompt_sections = [
        "You are a senior software architect.",
        f"Project title: {project_title}",
        f"Project description: {project_description}",
        "",
        "Main features:",
        feature_lines or "None provided",
        "",
        "Example user stories:",
        story_lines or "None provided",
        "",
        "Task:",
        "Design a high-level system architecture / flow for this application and express it using Mermaid.",
        "Use a flowchart LR diagram (or another Mermaid type if more appropriate).",
        "Show:",
        "- The user or client",
        "- The frontend (Angular web app)",
        "- The backend (FastAPI)",
        "- The database (MongoDB)",
        "- The AI agents / Claude where relevant",
        "- Key flows between these components.",
        "",
        "IMPORTANT:",
        "- Respond with ONLY valid Mermaid code.",
        "- Do NOT wrap it in ``` fences.",
        "- Do NOT add explanations or comments.",
    ]

    prompt = "\n".join(prompt_sections)

    # Use debug model if available, otherwise default
    model = os.getenv("CLAUDE_MODEL_DEBUG") or os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)
    logger.info(f"[agent3] generate_diagram_for_project using model: {model}")
    
    try:
        max_tokens = 32000  # Increased to prevent truncation
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.3,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )
        usage = getattr(response, "usage", None)
        if usage:
            logger.info(f"[agent3] generate_diagram_for_project API call successful | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}")
            if usage.output_tokens >= max_tokens * 0.95:  # 95% of max_tokens
                logger.warning(f"[agent3] ⚠️ Response may be truncated (used {usage.output_tokens}/{max_tokens} tokens)")
            elif usage.output_tokens >= max_tokens * 0.80:  # 80% of max_tokens
                logger.info(f"[agent3] ℹ️ Response used {usage.output_tokens}/{max_tokens} tokens (80%+ of limit)")
    except anthropic.APIError as exc:
        error_type = getattr(exc, 'type', 'unknown')
        error_status = getattr(exc, 'status_code', None)
        logger.error(f"[agent3] generate_diagram_for_project APIError - Type: {error_type}, Status: {error_status}, Message: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Claude API error while generating diagram"
        ) from exc

    response_text_parts: List[str] = []
    for block in getattr(response, "content", []):
        if getattr(block, "type", None) == "text" and getattr(block, "text", None):
            response_text_parts.append(block.text)

    mermaid_source = "\n".join(response_text_parts).strip()

    def _strip_fences(text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        if cleaned.lower().startswith("mermaid"):
            cleaned = cleaned[len("mermaid") :].strip()
        return cleaned.strip()

    mermaid_source = _strip_fences(mermaid_source)

    document = {
        "project_id": project_id,
        "diagram_type": "system_flow",
        "mermaid_source": mermaid_source,
        "created_at": datetime.datetime.utcnow(),
    }

    insert_result = await db["diagrams"].insert_one(document)
    document["_id"] = str(insert_result.inserted_id)
    return document


async def generate_designs_for_project(project_id: str, db):
    """Generate and persist HLD, LLD, and DBD Mermaid designs for a project.
    
    This function generates all three diagram types (HLD, LLD, DBD) based on:
    - Original user prompt
    - Agent1 features
    - Agent2 stories
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Claude API key not configured")

    client = anthropic.Anthropic(api_key=api_key)

    try:
        object_id = ObjectId(project_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid project ID") from exc

    project = await db["projects"].find_one({"_id": object_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    features_cursor = db["features"].find({"project_id": project_id}).sort("order_index", 1)
    features = await features_cursor.to_list(length=None)
    if not features:
        raise HTTPException(
            status_code=400, detail="No features found for this project. Run Agent-1 first."
        )

    stories_cursor = db["stories"].find({"project_id": project_id}).sort("created_at", 1)
    stories = await stories_cursor.to_list(length=None)

    project_title = project.get("title") or "Untitled Project"
    project_description = project.get("prompt") or project.get("description") or ""

    feature_lines = "\n".join(
        f"{idx}. {feature.get('feature_text') or feature.get('title') or 'Feature'}"
        for idx, feature in enumerate(features, start=1)
    )

    story_lines = "\n".join(
        f"{idx}. {story.get('story_text') or 'As a user, I want ...'}"
        for idx, story in enumerate(stories, start=1)
    )

    prompt = (
        "You are Agent-3, a senior software architect. Generate architecture diagrams based on:\n"
        f"- Original User Requirements: {project_description}\n"
        f"- Agent1 Features: {feature_lines or 'None provided'}\n"
        f"- Agent2 Stories: {story_lines or 'None provided'}\n\n"
        "Generate THREE Mermaid diagrams:\n\n"
        "1) High-Level Design (HLD):\n"
        "   - System architecture showing user, frontend (Angular), backend (FastAPI), database (MongoDB), AI agents\n"
        "   - Use `flowchart LR` or `graph TD` syntax\n\n"
        "2) Low-Level Design (LLD):\n"
        "   - Detailed component interactions, API endpoints, service layers, data flow\n"
        "   - Use `classDiagram`, `sequenceDiagram`, or detailed `flowchart` syntax\n\n"
        "3) Database Design (DBD):\n"
        "   - Entity-Relationship Diagram with tables, keys, relationships\n"
        "   - Use `erDiagram` or `entityRelationshipDiagram` syntax\n\n"
        "Return ONLY valid JSON:\n"
        "{\n"
        '  "hld_mermaid": "<Mermaid code>",\n'
        '  "lld_mermaid": "<Mermaid code>",\n'
        '  "dbd_mermaid": "<Mermaid code>"\n'
        "}\n"
        "No markdown fences, no extra text."
    )

    # Use debug model if available, otherwise default
    model = os.getenv("CLAUDE_MODEL_DEBUG") or os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)
    logger.info(f"[agent3] generate_designs_for_project using model: {model}")
    
    try:
        # Increased max_tokens to prevent diagram truncation
        max_tokens = 32000
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.3,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )
        usage = getattr(response, "usage", None)
        if usage:
            logger.info(f"[agent3] generate_designs_for_project API call successful | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}")
            if usage.output_tokens >= max_tokens * 0.95:  # 95% of max_tokens
                logger.warning(f"[agent3] ⚠️ Response may be truncated (used {usage.output_tokens}/{max_tokens} tokens)")
            elif usage.output_tokens >= max_tokens * 0.80:  # 80% of max_tokens
                logger.info(f"[agent3] ℹ️ Response used {usage.output_tokens}/{max_tokens} tokens (80%+ of limit)")
    except anthropic.APIError as exc:
        error_type = getattr(exc, 'type', 'unknown')
        error_status = getattr(exc, 'status_code', None)
        logger.error(f"[agent3] generate_designs_for_project APIError - Type: {error_type}, Status: {error_status}, Message: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Claude API error while generating designs"
        ) from exc

    response_text_parts: List[str] = []
    for block in getattr(response, "content", []):
        if getattr(block, "type", None) == "text" and getattr(block, "text", None):
            response_text_parts.append(block.text)

    response_text = "\n".join(response_text_parts).strip()

    try:
        design_data = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500, detail="Claude response could not be parsed as JSON"
        ) from exc

    hld_mermaid = design_data.get("hld_mermaid", "").strip()
    lld_mermaid = design_data.get("lld_mermaid", "").strip()
    dbd_mermaid = design_data.get("dbd_mermaid", "").strip()

    document = {
        "project_id": project_id,
        "hld_mermaid": hld_mermaid,
        "lld_mermaid": lld_mermaid,
        "dbd_mermaid": dbd_mermaid,
        "created_at": datetime.datetime.utcnow(),
    }

    insert_result = await db["designs"].insert_one(document)
    document["_id"] = str(insert_result.inserted_id)
    return document

