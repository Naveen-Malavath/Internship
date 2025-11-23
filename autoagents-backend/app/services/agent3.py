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
                "Generate detailed Mermaid diagrams showing component interactions, class structures, "
                "API endpoints, service layers, and data flow at an implementation level. "
                "Use appropriate Mermaid syntax like classDiagram, sequenceDiagram, or detailed flowcharts. "
                "ALWAYS add professional colors and styling for visual clarity."
            )
            user_prompt = (
                f"Project: {project_title or 'Untitled Project'}\n"
                f"{prompt_context}"
                f"Features from Agent1:\n" + "\n".join(feature_details) + "\n\n"
                f"User Stories from Agent2:\n{story_outline or 'None'}\n\n"
                "Create a COLORED LOW LEVEL DESIGN (LLD) Mermaid diagram showing:\n"
                "- Component/class/module interactions\n"
                "- API endpoints and service layers\n"
                "- Data flow between components\n"
                "- Database interactions\n"
                "- Use classDiagram, sequenceDiagram, or detailed flowchart syntax\n\n"
                "🎨 STYLING REQUIREMENTS (MANDATORY):\n"
                "- Define classDef styles with different colors for:\n"
                "  * Frontend components (e.g., fill:#E3F2FD,stroke:#1976D2,color:#000)\n"
                "  * Backend services (e.g., fill:#FFF3E0,stroke:#F57C00,color:#000)\n"
                "  * Database layer (e.g., fill:#E8F5E9,stroke:#388E3C,color:#000)\n"
                "  * External APIs (e.g., fill:#FCE4EC,stroke:#C2185B,color:#000)\n"
                "- Apply styles using ':::className' syntax\n"
                "- Use professional color schemes with good contrast\n\n"
                "Output ONLY valid Mermaid code, no explanations."
            )
        elif diagram_type.lower() == "database":
            system_prompt = (
                "You are Agent-3, an AI database architect. Generate COLORED Mermaid ER diagrams (erDiagram) "
                "showing tables, relationships, keys, and data models based on features and stories. "
                "Use professional styling and colors to distinguish different entity types."
            )
            user_prompt = (
                f"Project: {project_title or 'Untitled Project'}\n"
                f"{prompt_context}"
                f"Features from Agent1:\n" + "\n".join(feature_details) + "\n\n"
                f"User Stories from Agent2:\n{story_outline or 'None'}\n\n"
                "Create a COLORED DATABASE DESIGN (DBD) Mermaid diagram showing:\n"
                "- Entity-Relationship Diagram (ERD) with tables\n"
                "- Primary keys (PK), foreign keys (FK), and relationships\n"
                "- Data entities and their attributes with data types\n"
                "- Relationships: one-to-one (||--||), one-to-many (||--o{), many-to-many (}o--o{)\n"
                "- Use 'erDiagram' syntax in Mermaid\n\n"
                "🎨 STYLING REQUIREMENTS (MANDATORY):\n"
                "- After the erDiagram, add classDef statements to color different entity types:\n"
                "  * Core entities (e.g., classDef coreEntity fill:#E3F2FD,stroke:#1976D2)\n"
                "  * User-related (e.g., classDef userEntity fill:#F3E5F5,stroke:#7B1FA2)\n"
                "  * Transaction entities (e.g., classDef txEntity fill:#FFF3E0,stroke:#F57C00)\n"
                "  * Lookup/reference tables (e.g., classDef refEntity fill:#E8F5E9,stroke:#388E3C)\n"
                "- Apply styles to entities using ':::className' syntax\n"
                "- IMPORTANT: Entity attributes must NOT have quoted descriptions\n"
                "  * CORRECT: varchar name\n"
                "  * CORRECT: uuid id PK\n"
                "  * WRONG: uuid id PK \"Primary Key\"\n"
                "  * WRONG: varchar name \"Display Name\"\n\n"
                "Output ONLY valid Mermaid code, no explanations."
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
                if re.search(r'#[0-9A-Fa-f]{1,2}(?:[,\s]|$)', line_stripped):
                    # Found 1-2 hex digits - check if there's also a valid 3 or 6 digit hex
                    if not re.search(r'#[0-9A-Fa-f]{3}(?:[,\s:]|$)|#[0-9A-Fa-f]{6}(?:[,\s:]|$)', line_stripped):
                        logger.warning(f"[agent3] ⚠️ Detected incomplete hex color at line {line_num}")
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
            if 'erdiagram' in lines[0].lower() or 'entityrelationshipdiagram' in lines[0].lower():
                # Match: datatype fieldname PK/FK/UK "anything"
                if re.match(r'^\s*\w+\s+\w+\s+[A-Z]{2,}\s+"', line_stripped):
                    # Remove the quoted description part
                    cleaned = re.sub(r'\s+"[^"]*"', '', line)
                    logger.info(f"[agent3] 🔧 Cleaned erDiagram attribute description at line {line_num}")
                    fixed_lines.append(cleaned)
                    continue
                
                # Check for orphaned entity definitions (entity name on line after closing quote/bracket)
                if index > 0 and re.match(r'^[A-Z_][A-Z_0-9]*\s*\{', line_stripped):
                    prev_line = lines[index - 1] if index > 0 else ''
                    # If previous line ends with "] or just ", might be orphaned
                    if prev_line.strip().endswith('"]') or prev_line.strip().endswith('"'):
                        # Check if there's proper newline spacing
                        logger.warning(f"[agent3] ⚠️ Potential orphaned entity definition at line {line_num}: {line[:100]}")
                        # Add extra newline before this line in fixed output
                        if fixed_lines and not fixed_lines[-1].strip() == '':
                            fixed_lines.append('')  # Add blank line for separation
            
            # Check for classDiagram members appearing without class context
            if 'classdiagram' in lines[0].lower():
                # If line starts with +, -, #, ~ but previous line doesn't indicate we're in a class
                if re.match(r'^\s*[+\-#~]', line_stripped) and index > 0:
                    # Check if we're inside a class definition
                    in_class = False
                    for i in range(index - 1, -1, -1):
                        prev = lines[i].strip()
                        if prev.startswith('class ') or re.match(r'^[A-Z]\w+\s*\{', prev):
                            in_class = True
                            break
                        if prev == '' or prev.startswith('%%'):
                            continue
                        if 'classDiagram' in prev:
                            break
                    
                    if not in_class:
                        logger.warning(f"[agent3] ⚠️ Class member without class context at line {line_num}: {line[:100]}")
                        removed_lines.append((line_num, line[:100]))
                        continue
            
            # Check for lines ending with opening bracket without content (orphaned nodes)
            # Pattern: ..."]  NodeID[ with nothing following or just whitespace
            if re.search(r'"\]\s+[A-Za-z0-9_]+\[\s*$', line_stripped):
                logger.warning(f"[agent3] ⚠️ Orphaned node opening bracket at line {line_num}: {line[:100]}")
                removed_lines.append((line_num, line[:100]))
                continue
            
            fixed_lines.append(line)
        
        if removed_lines:
            logger.warning(f"[agent3] Removed {len(removed_lines)} incomplete/malformed line(s)")
            for line_num, line_preview in removed_lines:
                logger.debug(f"[agent3]   - Line {line_num}: {line_preview}")
            mermaid = '\n'.join(fixed_lines)
        else:
            mermaid = '\n'.join(fixed_lines)
        
        # Fix classDiagram-specific syntax issues (LLD diagrams)
        # This handles the parse error: "Expecting 'PS', 'TAGEND', 'STR', got 'PE'"
        # which occurs when class members are on the same line or have invalid syntax
        if 'classDiagram' in mermaid or diagram_type.lower() == 'lld':
            logger.info("[agent3] 🔧 Fixing classDiagram syntax for LLD")
            class_lines = mermaid.split('\n')
            fixed_class_lines = []
            inside_class = False
            class_indent = ''
            
            for i, line in enumerate(class_lines):
                stripped = line.strip()
                
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
        
        # Ensure it starts with a valid Mermaid diagram type
        valid_prefixes = ["graph", "classDiagram", "sequenceDiagram", "erDiagram", "entityRelationshipDiagram", "flowchart"]
        if not any(mermaid.startswith(prefix) for prefix in valid_prefixes):
            logger.warning("[agent3] Mermaid diagram doesn't start with valid type, prepending 'graph TD'")
            mermaid = f"graph TD\n{mermaid}"
        
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

