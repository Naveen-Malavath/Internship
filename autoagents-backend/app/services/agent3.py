"""Agent-3 service responsible for Mermaid diagram generation."""

from __future__ import annotations

import datetime
import json
import logging
import os
from typing import Any, Dict, List

import anthropic
from anthropic import APIError
from bson import ObjectId
from fastapi import HTTPException

from .claude_client import (
    DEFAULT_CLAUDE_MODEL,
    coerce_json,
    extract_text,
    get_claude_client,
)
from .mermaid_style_generator import (
    apply_style_to_mermaid,
)
from .style_config_generator import StyleConfigGenerator
from .diagram_complexity import (
    get_diagram_type_guidance,
)
from .node_shape_selector import NodeShapeSelector

logger = logging.getLogger(__name__)


def infer_project_domain(project_title: str, project_description: str) -> tuple[str, str]:
    """
    Infer the project domain/type from title and description using keyword checks.
    
    Returns:
        tuple: (domain_name, domain_hints) where domain_hints are domain-specific examples
    """
    text = f"{project_title} {project_description}".lower()
    
    # E-commerce / Retail
    if any(word in text for word in ['e-commerce', 'ecommerce', 'shopping', 'store', 'retail', 'cart', 'checkout', 'product catalog', 'merchant', 'marketplace']):
        return (
            "e-commerce",
            "shopping cart, product catalog, orders, payments, inventory, shipping, reviews"
        )
    
    # Banking / Finance
    if any(word in text for word in ['banking', 'bank', 'financial', 'finance', 'payment', 'transaction', 'account', 'ledger', 'wallet', 'credit', 'debit', 'loan', 'mortgage']):
        return (
            "banking/finance",
            "accounts, transactions, statements, payments, transfers, balances, interest, loans"
        )
    
    # Social Networking
    if any(word in text for word in ['social', 'network', 'community', 'feed', 'post', 'comment', 'like', 'share', 'follow', 'friend', 'message', 'chat', 'timeline']):
        return (
            "social networking",
            "profiles, posts, comments, notifications, feeds, connections, messaging, activity streams"
        )
    
    # Healthcare / Medical
    if any(word in text for word in ['healthcare', 'medical', 'patient', 'hospital', 'clinic', 'doctor', 'appointment', 'prescription', 'health', 'diagnosis', 'treatment']):
        return (
            "healthcare",
            "patient records, appointments, prescriptions, medical history, diagnoses, treatments, billing"
        )
    
    # Education / Learning
    if any(word in text for word in ['education', 'learning', 'course', 'student', 'teacher', 'school', 'university', 'lesson', 'curriculum', 'assignment', 'grade', 'quiz']):
        return (
            "education",
            "courses, students, instructors, assignments, grades, lessons, enrollments, certificates"
        )
    
    # SaaS Dashboard / Analytics
    if any(word in text for word in ['dashboard', 'analytics', 'saas', 'report', 'metric', 'chart', 'graph', 'data visualization', 'kpi', 'insight', 'monitoring']):
        return (
            "SaaS dashboard",
            "dashboards, reports, metrics, charts, data visualization, KPIs, insights, monitoring, alerts"
        )
    
    # Portfolio / Showcase
    if any(word in text for word in ['portfolio', 'showcase', 'gallery', 'exhibition', 'work', 'project', 'case study', 'demo']):
        return (
            "portfolio/showcase",
            "projects, galleries, case studies, demos, work samples, testimonials, contact forms"
        )
    
    # Real Estate
    if any(word in text for word in ['real estate', 'property', 'listing', 'rental', 'buy', 'sell', 'house', 'apartment', 'agent', 'broker']):
        return (
            "real estate",
            "properties, listings, agents, viewings, offers, contracts, mortgages, inspections"
        )
    
    # Food Delivery / Restaurant
    if any(word in text for word in ['food', 'restaurant', 'delivery', 'order', 'menu', 'cuisine', 'dining', 'reservation', 'takeout']):
        return (
            "food delivery/restaurant",
            "menus, orders, deliveries, reservations, reviews, payments, kitchen management, inventory"
        )
    
    # Default
    return (
        "software application",
        "core features, user management, data processing, integrations, notifications"
    )


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

    def _fix_mermaid_syntax(self, mermaid: str) -> str:
        """Fix common Mermaid syntax issues in generated diagrams.
        
        Common issues:
        - Nodes inside subgraphs without node IDs (e.g., ((WebStorefront)) instead of WebStorefront((WebStorefront)))
        - Malformed node shapes like (["text or ((text))
        - Missing spaces between nodes and connections
        - ER diagram syntax errors (attributes with numbers)
        """
        import re
        
        logger.debug(f"[agent3] _fix_mermaid_syntax: Starting fix | input_length={len(mermaid)} chars")
        
        lines = mermaid.split('\n')
        fixed_lines = []
        in_subgraph = False
        node_id_map = {}  # Map of labels to node IDs for connections
        fixes_applied = []
        
        for i, line in enumerate(lines):
            original_line = line
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('%%'):
                fixed_lines.append(line)
                continue
            
            # Track subgraph state
            if stripped.startswith('subgraph'):
                in_subgraph = True
                fixed_lines.append(line)
                continue
            elif stripped == 'end':
                in_subgraph = False
                fixed_lines.append(line)
                continue
            
            # Fix nodes inside subgraphs - CRITICAL: nodes must have node IDs
            if in_subgraph:
                # Pattern 1: ((Label)) without node ID - MUST FIX
                # Example: ((WebStorefront)) -> WebStorefront((WebStorefront))
                circle_match = re.match(r'^\s*\(\(([^)]+)\)\)\s*$', stripped)
                if circle_match:
                    label = circle_match.group(1).strip()
                    node_id = re.sub(r'[^a-zA-Z0-9_]', '_', label)  # Sanitize to valid ID
                    line = f'        {node_id}(({label}))'
                    node_id_map[label] = node_id
                    fixes_applied.append(f"Line {i+1}: Fixed circle node without ID: (({label})) -> {node_id}(({label}))")
                    logger.debug(f"[agent3] _fix_mermaid_syntax: Line {i+1} - Fixed circle node: (({label})) -> {node_id}(({label}))")
                
                # Pattern 2: (["Label"]) without node ID
                stadium_match = re.match(r'^\s*\(\["([^"]+)"\]\)\s*$', stripped)
                if stadium_match:
                    label = stadium_match.group(1).strip()
                    node_id = re.sub(r'[^a-zA-Z0-9_]', '_', label)
                    line = f'        {node_id}(["{label}"])'
                    node_id_map[label] = node_id
                    fixes_applied.append(f"Line {i+1}: Fixed stadium node without ID: ([\"{label}\"]) -> {node_id}([\"{label}\"])")
                    logger.debug(f"[agent3] _fix_mermaid_syntax: Line {i+1} - Fixed stadium node: ([\"{label}\"]) -> {node_id}([\"{label}\"])")
                
                # Pattern 3: [Label] without node ID
                rect_match = re.match(r'^\s*\[([^\]]+)\]\s*$', stripped)
                if rect_match:
                    label = rect_match.group(1).strip()
                    node_id = re.sub(r'[^a-zA-Z0-9_]', '_', label)
                    line = f'        {node_id}[{label}]'
                    node_id_map[label] = node_id
                    fixes_applied.append(f"Line {i+1}: Fixed rectangle node without ID: [{label}] -> {node_id}[{label}]")
                    logger.debug(f"[agent3] _fix_mermaid_syntax: Line {i+1} - Fixed rectangle node: [{label}] -> {node_id}[{label}]")
                
                # Pattern 4: {Label} without node ID
                diamond_match = re.match(r'^\s*\{([^}]+)\}\s*$', stripped)
                if diamond_match:
                    label = diamond_match.group(1).strip()
                    node_id = re.sub(r'[^a-zA-Z0-9_]', '_', label)
                    line = f'        {node_id}{{{label}}}'
                    node_id_map[label] = node_id
                    fixes_applied.append(f"Line {i+1}: Fixed diamond node without ID: {{{label}}} -> {node_id}{{{label}}}")
                    logger.debug(f"[agent3] _fix_mermaid_syntax: Line {i+1} - Fixed diamond node: {{{label}}} -> {node_id}{{{label}}}")
                
                # Pattern 5: [/Label/] without node ID
                parallelogram_match = re.match(r'^\s*\[/([^/]+)/\]\s*$', stripped)
                if parallelogram_match:
                    label = parallelogram_match.group(1).strip()
                    node_id = re.sub(r'[^a-zA-Z0-9_]', '_', label)
                    line = f'        {node_id}[/{label}/]'
                    node_id_map[label] = node_id
                    fixes_applied.append(f"Line {i+1}: Fixed parallelogram node without ID: [/{label}/] -> {node_id}[/{label}/]")
                    logger.debug(f"[agent3] _fix_mermaid_syntax: Line {i+1} - Fixed parallelogram node: [/{label}/] -> {node_id}[/{label}/]")
                
                # Pattern 6: [(Label)] without node ID (cylinder)
                cylinder_match = re.match(r'^\s*\[\(([^)]+)\)\]\s*$', stripped)
                if cylinder_match:
                    label = cylinder_match.group(1).strip()
                    node_id = re.sub(r'[^a-zA-Z0-9_]', '_', label)
                    line = f'        {node_id}[({label})]'
                    node_id_map[label] = node_id
                    fixes_applied.append(f"Line {i+1}: Fixed cylinder node without ID: [({label})] -> {node_id}[({label})]")
                    logger.debug(f"[agent3] _fix_mermaid_syntax: Line {i+1} - Fixed cylinder node: [({label})] -> {node_id}[({label})]")
                
                # Check if node appears after subgraph label on same line (invalid syntax)
                if ']' in line and re.search(r'\]\s+[\[\(]', line):
                    parts = re.split(r'\]\s+', line, 1)
                    if len(parts) > 1:
                        fixed_lines.append(parts[0] + ']')
                        line = '        ' + parts[1].strip()
                        fixes_applied.append(f"Line {i+1}: Split node from subgraph label")
            
            # Fix connections that use shape syntax instead of node IDs
            # Example: ((WebStorefront)) --> should be WebStorefront -->
            if '-->' in line or '->' in line or '==>' in line:
                for label, node_id in node_id_map.items():
                    # Replace shape syntax with node ID in connections
                    line = re.sub(rf'\(\({re.escape(label)}\)\)', node_id, line)
                    line = re.sub(rf'\(\["{re.escape(label)}"\]\)', node_id, line)
                    line = re.sub(rf'\[{re.escape(label)}\]', node_id, line)
                    line = re.sub(rf'\{{{re.escape(label)}\}}', node_id, line)
                    line = re.sub(rf'\[/{re.escape(label)}/\]', node_id, line)
                    line = re.sub(rf'\[\({re.escape(label)}\)\]', node_id, line)
            
            # Fix ER diagram syntax - attributes cannot have numbers directly after them
            # Pattern: attribute_name1 -> attribute_name_1 or attribute_name
            if 'erDiagram' in mermaid or 'entityRelationshipDiagram' in mermaid:
                # Fix attribute definitions: field_name1 -> field_name_1
                # But preserve if it's already valid (field_name_1)
                line = re.sub(r'(\w+)(\d+)(\s)', r'\1_\2\3', line)
                # Fix in relationships: field_name1 -> field_name_1
                line = re.sub(r'(\w+)(\d+)(\s*FK|\s*PK|\s*"|\s*$)', r'\1_\2\3', line)
                # Fix attribute definitions that have numbers: "uuid order_id FK" -> "uuid order_id_FK"
                # Mermaid ER diagrams require spaces between attribute parts
                line = re.sub(r'(\w+)\s+(\w+)(\d+)(\s|$)', r'\1 \2_\3\4', line)
                # Fix: "uuid order_id1" -> "uuid order_id_1"
                line = re.sub(r'(\w+)\s+(\w+)(\d+)(\s|$)', r'\1 \2_\3\4', line)
            
            # Ensure proper spacing around arrows
            line = re.sub(r'(\w+)(->|-->|==>|-.->)(\w+)', r'\1 \2 \3', line)
            
            fixed_lines.append(line)
        
        fixed_mermaid = '\n'.join(fixed_lines)
        
        # Validate node references in connections
        # Extract all defined node IDs
        node_ids = set()
        node_id_patterns = [
            r'^(\w+)\s*\(\(',           # nodeId((
            r'^(\w+)\s*\(\[',            # nodeId(["
            r'^(\w+)\s*\[',              # nodeId[
            r'^(\w+)\s*\{',              # nodeId{
            r'^(\w+)\s*\[\/',            # nodeId[/.../]
            r'^(\w+)\s*\[\(',            # nodeId[(
        ]
        
        for line in fixed_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('%%') or stripped.startswith('subgraph') or stripped == 'end':
                continue
            
            # Extract node ID from various patterns
            for pattern in node_id_patterns:
                match = re.match(pattern, stripped)
                if match:
                    node_ids.add(match.group(1))
                    break
        
        # Validate connections - remove connections to non-existent nodes
        validated_lines = []
        for i, line in enumerate(fixed_lines):
            stripped = line.strip()
            
            # Check if this is a connection line
            # Pattern: NodeA --> NodeB
            # Pattern: NodeA -->|label| NodeB
            # Pattern: NodeA -->|label NodeB (incomplete label)
            connection_match = re.match(r'^(\w+)\s*(-->|->|==>|-\.->)(\|[^|]*\|)?\s*(\w+)?', stripped)
            if connection_match or '-->' in stripped or '->' in stripped or '==>' in stripped or '-.->' in stripped:
                # Extract source and destination more carefully
                source_node = None
                dest_node = None
                arrow_type = None
                label_part = None
                
                if connection_match:
                    source_node = connection_match.group(1)
                    arrow_type = connection_match.group(2)
                    label_part = connection_match.group(3)
                    dest_node = connection_match.group(4)
                else:
                    # Fallback: try to extract manually
                    arrow_match = re.search(r'(-->|->|==>|-\.->)', stripped)
                    if arrow_match:
                        arrow_type = arrow_match.group(1)
                        parts = stripped.split(arrow_type)
                        if len(parts) >= 1:
                            source_part = parts[0].strip()
                            source_match = re.search(r'(\w+)\s*$', source_part)
                            if source_match:
                                source_node = source_match.group(1)
                        if len(parts) >= 2:
                            dest_part = parts[1].strip()
                            # Remove label if present: |label|
                            dest_part_clean = re.sub(r'^\|[^|]*\|\s*', '', dest_part)
                            dest_match = re.match(r'^(\w+)', dest_part_clean)
                            if dest_match:
                                dest_node = dest_match.group(1)
                
                if not source_node:
                    validated_lines.append(line)
                    continue
                
                # Check if source node exists
                if source_node not in node_ids:
                    logger.warning(f"[agent3] _fix_mermaid_syntax: Removing connection from undefined node: {source_node} on line {i+1}")
                    validated_lines.append(f"%% Removed invalid connection: {stripped}")
                    fixes_applied.append(f"Line {i+1}: Removed connection from undefined node: {source_node}")
                    continue
                
                # Check for incomplete connections (missing destination)
                if arrow_type:
                    # Cases: "NodeA -->", "NodeA -->|label|", "NodeA -->|label" (incomplete label)
                    has_incomplete_label = label_part and not label_part.endswith('|')
                    ends_with_arrow = stripped.endswith(arrow_type) or stripped.endswith(arrow_type + '|')
                    has_label_but_no_dest = label_part and not dest_node
                    
                    if ends_with_arrow or has_incomplete_label or has_label_but_no_dest:
                        logger.warning(f"[agent3] _fix_mermaid_syntax: Removing incomplete connection on line {i+1}: {stripped[:50]}")
                        validated_lines.append(f"%% Removed incomplete connection: {stripped}")
                        fixes_applied.append(f"Line {i+1}: Removed incomplete connection")
                        continue
                
                # Check if destination node exists
                if dest_node and dest_node not in node_ids:
                    logger.warning(f"[agent3] _fix_mermaid_syntax: Removing connection to undefined node: {dest_node} on line {i+1}")
                    validated_lines.append(f"%% Removed invalid connection: {stripped}")
                    fixes_applied.append(f"Line {i+1}: Removed connection to undefined node: {dest_node}")
                    continue
            
            validated_lines.append(line)
        
        fixed_mermaid = '\n'.join(validated_lines)
        
        # Log fixes applied
        if fixes_applied:
            logger.info(f"[agent3] _fix_mermaid_syntax: Applied {len(fixes_applied)} fixes:")
            for fix in fixes_applied[:10]:  # Log first 10 fixes
                logger.debug(f"[agent3] _fix_mermaid_syntax: {fix}")
            if len(fixes_applied) > 10:
                logger.debug(f"[agent3] _fix_mermaid_syntax: ... and {len(fixes_applied) - 10} more fixes")
        else:
            logger.debug(f"[agent3] _fix_mermaid_syntax: No fixes needed")
        
        logger.debug(f"[agent3] _fix_mermaid_syntax: Complete | output_length={len(fixed_mermaid)} chars")
        return fixed_mermaid

    def _validate_mermaid_syntax(self, mermaid: str) -> dict:
        """Validate Mermaid diagram syntax and check for truncation issues.
        
        Returns:
            dict with keys:
                - valid: bool - Whether diagram is valid
                - errors: list - List of error messages
                - warnings: list - List of warning messages
                - incomplete_lines: list - Lines that appear incomplete
                - truncation_point: int - Line number where truncation detected (-1 if none)
        """
        import re
        
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'incomplete_lines': [],
            'truncation_point': -1,
        }
        
        if not mermaid or not mermaid.strip():
            result['valid'] = False
            result['errors'].append('Diagram is empty')
            return result
        
        lines = mermaid.split('\n')
        in_subgraph = False
        subgraph_stack = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('%%'):
                continue
            
            # Track subgraph state
            if stripped.startswith('subgraph'):
                in_subgraph = True
                subgraph_stack.append(i)
            elif stripped == 'end':
                if in_subgraph:
                    if subgraph_stack:
                        subgraph_stack.pop()
                        if not subgraph_stack:
                            in_subgraph = False
                else:
                    result['warnings'].append(f"Line {i}: 'end' without matching 'subgraph'")
            
            # Check for incomplete arrows (most common truncation issue)
            # Pattern: nodeId -->|label| (missing destination)
            # Pattern: nodeId --> (missing destination)
            # Pattern: nodeId -->|label (missing closing | and destination)
            incomplete_arrow_patterns = [
                r'\w+\s*-->\s*\|[^|]*$',  # -->|label without closing |
                r'\w+\s*-->\s*\|[^|]*\|\s*$',  # -->|label| without destination
                r'\w+\s*-->\s*$',  # --> without destination (at end of line)
                r'\w+\s*->\s*$',  # -> without destination
                r'\w+\s*==>\s*$',  # ==> without destination
                r'\w+\s*-\.->\s*$',  # -.-> without destination
            ]
            
            for pattern in incomplete_arrow_patterns:
                if re.search(pattern, stripped):
                    result['valid'] = False
                    result['errors'].append(f"Line {i}: Incomplete arrow connection (truncated) - '{stripped[:50]}...'")
                    result['incomplete_lines'].append(i)
                    if result['truncation_point'] == -1:
                        result['truncation_point'] = i
                    break
            
            # Check for incomplete node definitions at end of file
            if i == len(lines) and stripped:
                # Last line should not be an incomplete connection
                if any(stripped.endswith(arrow) for arrow in ['-->', '->', '==>', '-.->', '-->|']):
                    result['valid'] = False
                    result['errors'].append(f"Line {i}: Diagram ends with incomplete connection")
                    result['incomplete_lines'].append(i)
                    if result['truncation_point'] == -1:
                        result['truncation_point'] = i
        
        # Check for unclosed subgraphs
        if subgraph_stack:
            result['valid'] = False
            result['errors'].append(f"Unclosed subgraph(s) starting at line(s): {subgraph_stack}")
            result['warnings'].append(f"Subgraph stack has {len(subgraph_stack)} unclosed subgraph(s)")
        
        # Check if diagram ends abruptly (last non-empty line is incomplete)
        if lines:
            last_non_empty = None
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() and not lines[i].strip().startswith('%%'):
                    last_non_empty = (i + 1, lines[i].strip())
                    break
            
            if last_non_empty:
                line_num, last_line = last_non_empty
                # If last line is a connection without label and seems cut off
                if '-->' in last_line and len(last_line.split()) < 3:
                    result['valid'] = False
                    result['errors'].append(f"Line {line_num}: Diagram may be truncated - last line appears incomplete: '{last_line}'")
                    if result['truncation_point'] == -1:
                        result['truncation_point'] = line_num
        
        logger.debug(f"[agent3] _validate_mermaid_syntax: valid={result['valid']}, errors={len(result['errors'])}, warnings={len(result['warnings'])}")
        if result['errors']:
            logger.warning(f"[agent3] _validate_mermaid_syntax: Found {len(result['errors'])} errors")
            for error in result['errors']:
                logger.warning(f"[agent3] _validate_mermaid_syntax: {error}")
        
        return result

    def _complete_truncated_diagram(self, mermaid: str, validation_result: dict) -> str:
        """Attempt to fix/complete a truncated diagram by removing incomplete lines.
        
        Args:
            mermaid: The truncated Mermaid diagram
            validation_result: Result from _validate_mermaid_syntax
            
        Returns:
            Fixed diagram with incomplete lines removed
        """
        if validation_result['truncation_point'] == -1:
            return mermaid
        
        lines = mermaid.split('\n')
        truncation_line = validation_result['truncation_point']
        
        logger.warning(f"[agent3] _complete_truncated_diagram: Removing lines from {truncation_line} onwards (incomplete)")
        
        # Remove incomplete lines
        fixed_lines = lines[:truncation_line - 1]
        
        # Ensure subgraphs are closed
        subgraph_count = sum(1 for line in fixed_lines if line.strip().startswith('subgraph'))
        end_count = sum(1 for line in fixed_lines if line.strip() == 'end')
        
        # Add missing 'end' statements
        missing_ends = subgraph_count - end_count
        if missing_ends > 0:
            logger.warning(f"[agent3] _complete_truncated_diagram: Adding {missing_ends} missing 'end' statement(s)")
            for _ in range(missing_ends):
                fixed_lines.append('end')
        
        fixed_mermaid = '\n'.join(fixed_lines).strip()
        logger.info(f"[agent3] _complete_truncated_diagram: Removed {len(lines) - len(fixed_lines)} incomplete line(s)")
        
        return fixed_mermaid

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
        logger.info(f"[agent3] Starting Mermaid diagram generation | model={self.model} | type={diagram_type} | features={len(features)} | stories={len(stories)} | prompt_length={len(original_prompt)}")
        
        # STEP 1: Initialize StyleConfigGenerator and generate full configuration
        logger.debug("[agent3] STEP 1: Initializing StyleConfigGenerator")
        style_generator = StyleConfigGenerator(original_prompt, project_title)
        full_config = style_generator.generate_full_config(features, stories)
        
        # Extract components
        style_config_dict = {
            "theme": full_config["theme"],
            "nodeShape": "rect",  # Default
            "primaryColor": full_config["colors"]["primary"],
            "secondaryColor": full_config["colors"]["secondary"],
            "accentColor": full_config["colors"]["tertiary"],
            "backgroundColor": "#ffffff",
            "arrowStyle": "solid",
            "fontSize": "16px",
            "fontFamily": "Arial, sans-serif",
            "domain": full_config["domain"],
        }
        complexity_info = full_config["complexity"]
        init_directive = full_config["init_directive"]
        
        logger.info(
            f"[agent3] Style config generated | domain={full_config['domain']} | theme={full_config['theme']} | "
            f"primaryColor={full_config['colors']['primary']} | complexity_score={complexity_info['complexity_score']} | "
            f"recommended_type={complexity_info['recommended_type']}"
        )
        logger.debug(f"[agent3] Init directive generated | length={len(init_directive)} chars")
        
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

        # Include original prompt context with emphasis
        prompt_context = ""
        if original_prompt and original_prompt.strip():
            prompt_context = f"\n\n=== ORIGINAL CUSTOMER REQUIREMENTS ===\n{original_prompt.strip()}\n=== END REQUIREMENTS ===\n\n"
            logger.debug(f"[agent3] Original prompt context included | length={len(prompt_context)} chars")
        
        # STEP 3: Build prompts with style, complexity, and shape guidance
        logger.debug("[agent3] STEP 3: Building prompts with style and complexity guidance")
        
        # Initialize NodeShapeSelector with complexity score
        shape_selector = NodeShapeSelector(
            complexity_score=complexity_info["complexity_score"],
            prompt=original_prompt
        )
        logger.debug(f"[agent3] NodeShapeSelector initialized | complexity={complexity_info['complexity_score']}")
        
        # Get shape instructions from NodeShapeSelector
        shape_instructions = shape_selector.build_shape_instructions(complexity_info)
        logger.debug(f"[agent3] Shape instructions generated | length={len(shape_instructions)} chars")
        
        # Get shape mapping summary for debugging
        shape_mapping = shape_selector.get_shape_mapping_summary()
        logger.debug(f"[agent3] Shape mapping summary | {len(shape_mapping)} node types mapped")
        
        # Get diagram type guidance based on complexity
        diagram_guidance = get_diagram_type_guidance(diagram_type, complexity_info)
        
        # Build style guidance string
        style_guidance = f"""
STYLE REQUIREMENTS:
- Theme: {style_config_dict['theme']}
- Primary Color: {style_config_dict['primaryColor']}
- Secondary Color: {style_config_dict['secondaryColor']}
- Accent Color: {style_config_dict['accentColor']}
- Font: {style_config_dict['fontFamily']} at {style_config_dict['fontSize']}
- Domain: {style_config_dict['domain']}

Note: Style will be automatically injected via %%init%% directive. Focus on diagram structure and content.
"""
        
        # Create type-specific prompts
        if diagram_type.lower() == "lld":
            system_prompt = (
                "You are Agent-3, an AI software architect specializing in Low Level Design (LLD). "
                "Generate detailed Mermaid diagrams showing component interactions, class structures, "
                "API endpoints, service layers, and data flow at an implementation level. "
                "Use appropriate Mermaid syntax like classDiagram, sequenceDiagram, or detailed flowcharts. "
                "Apply shape variation logic consistently based on node function."
            )
            user_prompt = (
                f"Project: {project_title or 'Untitled Project'}\n"
                f"{prompt_context}"
                f"Features from Agent1:\n" + "\n".join(feature_details) + "\n\n"
                f"User Stories from Agent2:\n{story_outline or 'None'}\n\n"
                f"{diagram_guidance}\n"
                f"{shape_instructions}\n"
                f"{style_guidance}\n"
                "Create a LOW LEVEL DESIGN (LLD) Mermaid diagram showing:\n"
                "- Component/class/module interactions\n"
                "- API endpoints and service layers\n"
                "- Data flow between components\n"
                "- Database interactions\n"
                "- Use classDiagram, sequenceDiagram, or detailed flowchart syntax\n"
                "- Apply appropriate shapes based on node type and architectural layer\n"
                "- Use the shape mapping provided in the instructions above\n\n"
                "CRITICAL SYNTAX REQUIREMENTS:\n"
                "- All node connections MUST be complete: NodeA --> NodeB (NEVER: NodeA --> without destination)\n"
                "- All subgraph blocks MUST be closed with 'end'\n"
                "- All arrows must have both source and destination: NodeId1 --> NodeId2\n"
                "- For nodes inside subgraphs, always use: NodeId((Label)) format, not just ((Label))\n"
                "- Ensure the diagram is complete - never cut off mid-line or mid-connection\n\n"
                "Output ONLY valid Mermaid code, no explanations. Do NOT include %%init%% directives (they will be added automatically)."
            )
        elif diagram_type.lower() == "database":
            system_prompt = (
                "You are Agent-3, an AI database architect. Generate Mermaid ER diagrams (entityRelationshipDiagram) "
                "or database schema diagrams showing tables, relationships, keys, and data models based on features and stories."
            )
            user_prompt = (
                f"Project: {project_title or 'Untitled Project'}\n"
                f"{prompt_context}"
                f"Features from Agent1:\n" + "\n".join(feature_details) + "\n\n"
                f"User Stories from Agent2:\n{story_outline or 'None'}\n\n"
                f"{style_guidance}\n"
                "Create a DATABASE DESIGN Mermaid diagram showing:\n"
                "- Entity-Relationship Diagram (ERD) with tables\n"
                "- Primary keys, foreign keys, and relationships\n"
                "- Data entities and their attributes\n"
                "- Relationships (one-to-one, one-to-many, many-to-many)\n"
                "- Use entityRelationshipDiagram syntax in Mermaid\n\n"
                "CRITICAL SYNTAX REQUIREMENTS:\n"
                "- All relationships MUST be complete: Entity1 ||--o{ Entity2 (NEVER: Entity1 ||--o{ without destination)\n"
                "- All attribute names must be valid (no numbers directly after names: use order_id_1 not order_id1)\n"
                "- Ensure the diagram is complete - never cut off mid-line or mid-relationship\n\n"
                "Output ONLY valid Mermaid code, no explanations. Do NOT include %%init%% directives (they will be added automatically)."
            )
        else:  # Default to HLD
            system_prompt = (
                "You are Agent-3, an AI solution architect specializing in High Level Design (HLD). "
                "Generate Mermaid diagrams showing system architecture, high-level components, "
                "and business flow at a conceptual level. Apply shape variation logic consistently."
            )
            recommended_type = complexity_info.get("recommended_type", "flowchart TD")
            user_prompt = (
                f"Project: {project_title or 'Untitled Project'}\n"
                f"{prompt_context}"
                f"Features from Agent1:\n" + "\n".join(feature_details) + "\n\n"
                f"User Stories from Agent2:\n{story_outline or 'None'}\n\n"
                f"{diagram_guidance}\n"
                f"{shape_instructions}\n"
                f"{style_guidance}\n"
                "Create a HIGH LEVEL DESIGN (HLD) Mermaid diagram showing:\n"
                "- System architecture and major components\n"
                "- Business process flow from features to stories\n"
                "- High-level interactions between system modules\n"
                "- User journey through features\n"
                f"- Use {recommended_type} syntax (or appropriate variant)\n"
                "- Apply appropriate shapes based on node type and architectural layer\n"
                "- Use the shape mapping provided in the instructions above\n"
                "- Controllers/APIs: ([ControllerName]), Services: [ServiceName], Decisions: {{DecisionName}}, Databases: [(DatabaseName)], External: [/ExternalName/], UI: ((UIName))\n\n"
                "CRITICAL SYNTAX REQUIREMENTS:\n"
                "- All node connections MUST be complete: NodeA --> NodeB (NEVER: NodeA --> without destination)\n"
                "- All subgraph blocks MUST be closed with 'end'\n"
                "- All arrows must have both source and destination: NodeId1 --> NodeId2\n"
                "- For nodes inside subgraphs, always use: NodeId((Label)) format, not just ((Label))\n"
                "- Ensure the diagram is complete - never cut off mid-line or mid-connection\n\n"
                "Output ONLY valid Mermaid code, no explanations. Do NOT include %%init%% directives (they will be added automatically)."
            )
        
        logger.debug(f"[agent3] Prompts built | system_prompt_length={len(system_prompt)} | user_prompt_length={len(user_prompt)}")

        # STEP 4: Generate diagram with sufficient token limit to prevent truncation
        initial_max_tokens = 8000  # Increased from 1500 to prevent truncation
        max_tokens = initial_max_tokens
        max_retries = 2
        retry_count = 0
        mermaid = None
        
        while retry_count <= max_retries:
            try:
                logger.info(f"[agent3] Attempting API call (attempt {retry_count + 1}/{max_retries + 1}) | model={self.model} | max_tokens={max_tokens} | temperature=0.3")
                logger.debug(f"[agent3] System prompt length: {len(system_prompt)} chars")
                logger.debug(f"[agent3] User prompt length: {len(user_prompt)} chars")
                
                response = await client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=0.3,  # Lower temperature for faster, more focused responses
                    system=system_prompt,
                    messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
                )
                
                usage = getattr(response, "usage", None)
                if usage:
                    logger.info(f"[agent3] API call successful | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens} | max_output={max_tokens}")
                    # Check if we hit the token limit (indicates potential truncation)
                    if usage.output_tokens >= max_tokens * 0.95:  # Used 95%+ of tokens
                        logger.warning(f"[agent3] Output may be truncated - used {usage.output_tokens}/{max_tokens} tokens ({usage.output_tokens/max_tokens*100:.1f}%)")
                else:
                    logger.info("[agent3] API call successful")
                
                # Extract and clean Mermaid diagram
                logger.debug("[agent3] STEP 4: Extracting Mermaid diagram from response")
                mermaid = extract_text(response).strip()
                logger.debug(f"[agent3] Raw response extracted | length={len(mermaid)} chars")
                
                if not mermaid:
                    raise ValueError("Empty response from API")
                
                break  # Success, exit retry loop
                
            except APIError as exc:
                error_type = getattr(exc, 'type', 'unknown')
                error_status = getattr(exc, 'status_code', None)
                
                # If it's a token limit error, increase and retry
                if error_type == 'rate_limit_error' or 'token' in str(exc).lower():
                    retry_count += 1
                    if retry_count <= max_retries:
                        max_tokens = int(max_tokens * 1.5)  # Increase by 50%
                        logger.warning(f"[agent3] Token limit error, retrying with max_tokens={max_tokens}")
                        continue
                
                logger.error(f"[agent3] APIError - Type: {error_type}, Status: {error_status}, Message: {str(exc)}", exc_info=True)
                raise RuntimeError(f"Agent-3 failed to generate diagram: {exc}") from exc
            
            except Exception as exc:
                logger.error(f"[agent3] Unexpected error during API call: {exc}", exc_info=True)
                if retry_count < max_retries:
                    retry_count += 1
                    logger.warning(f"[agent3] Retrying after error (attempt {retry_count}/{max_retries})")
                    continue
                raise
        
        if not mermaid:
            raise RuntimeError("Failed to generate diagram after all retries")
        
        # Clean up mermaid code - remove markdown fences if present
        if mermaid.startswith("```"):
            lines = mermaid.split("\n")
            if lines[0].startswith("```mermaid"):
                mermaid = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
                logger.debug("[agent3] Removed ```mermaid code fence")
            elif lines[0].strip() == "```":
                mermaid = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
                logger.debug("[agent3] Removed generic code fence")
        mermaid = mermaid.strip()
        
        # Fix common Mermaid syntax issues in generated diagrams
        mermaid = self._fix_mermaid_syntax(mermaid)
        
        # STEP 4.5: Validate diagram and handle truncation
        logger.debug("[agent3] STEP 4.5: Validating Mermaid diagram syntax")
        validation_result = self._validate_mermaid_syntax(mermaid)
        
        if not validation_result['valid']:
            logger.warning(f"[agent3] Diagram validation failed with {len(validation_result['errors'])} error(s)")
            
            # Attempt to fix truncated diagram
            if validation_result['truncation_point'] > 0:
                logger.warning(f"[agent3] Detected truncation at line {validation_result['truncation_point']}, attempting to complete diagram")
                mermaid = self._complete_truncated_diagram(mermaid, validation_result)
                
                # Re-validate after fix
                validation_result = self._validate_mermaid_syntax(mermaid)
                
                if not validation_result['valid']:
                    logger.error(f"[agent3] Diagram still invalid after completion attempt. Errors: {validation_result['errors']}")
                    # Log all errors for debugging
                    for error in validation_result['errors']:
                        logger.error(f"[agent3] Validation error: {error}")
                    
                    # Log truncation point for debugging
                    logger.error(f"[agent3] Diagram truncated at line {validation_result['truncation_point']}")
                    logger.error(f"[agent3] Proceeding with fixed diagram (incomplete lines removed). Users may see truncated content.")
                else:
                    logger.info(f"[agent3] Successfully fixed truncated diagram")
            else:
                # Non-truncation errors - log but continue
                for error in validation_result['errors']:
                    logger.error(f"[agent3] Validation error: {error}")
        else:
            logger.debug("[agent3] Diagram validation passed")
        
        # Log any warnings even if valid
        if validation_result['warnings']:
            for warning in validation_result['warnings']:
                logger.warning(f"[agent3] Validation warning: {warning}")
        
        # STEP 5: Apply style configuration to mermaid source using init directive
        logger.debug("[agent3] STEP 5: Applying style configuration to Mermaid diagram")
        
        # Parse the mermaid to find diagram type and separate it from the rest
        # First, remove any existing init directives and classDef statements
        lines = mermaid.split('\n')
        clean_lines = []
        for line in lines:
            stripped = line.strip()
            # Skip init directives and classDef (we'll add our own in the right place)
            if "%%{init:" not in line and "%%{ init:" not in line and not stripped.startswith("classDef"):
                clean_lines.append(line)
        
        mermaid_clean = '\n'.join(clean_lines)
        
        # Find the diagram type line (must come first in valid Mermaid)
        diagram_type_line = None
        diagram_type_idx = -1
        detected_diagram_type = None
        valid_prefixes = ["graph", "classDiagram", "sequenceDiagram", "erDiagram", "entityRelationshipDiagram", "flowchart", "stateDiagram"]
        
        for i, line in enumerate(clean_lines):
            stripped = line.strip()
            for prefix in valid_prefixes:
                if stripped.startswith(prefix):
                    diagram_type_line = line
                    diagram_type_idx = i
                    detected_diagram_type = prefix
                    break
            if diagram_type_line:
                break
        
        # If no diagram type found, prepend recommended type
        if diagram_type_idx == -1:
            logger.warning(f"[agent3] Mermaid diagram doesn't contain valid type, prepending recommended type: {complexity_info.get('recommended_type', 'flowchart TD')}")
            recommended = complexity_info.get("recommended_type", "flowchart TD")
            diagram_type_line = recommended
            diagram_type_idx = -1  # Will be inserted at position 0
        else:
            logger.debug(f"[agent3] Valid diagram type detected: {diagram_type_line[:50]}")
        
        # Get the body (everything except diagram type line)
        body_lines = []
        for i, line in enumerate(clean_lines):
            if i != diagram_type_idx:
                body_lines.append(line)
        
        # Build the styled diagram in correct order:
        # 1. Diagram type (required first)
        # 2. Init directive (can come after diagram type)
        # 3. ClassDef statements (must come after diagram type)
        # 4. Rest of diagram
        styled_parts = []
        
        # 1. Diagram type first (required by Mermaid)
        styled_parts.append(diagram_type_line)
        
        # 2. Init directive
        styled_parts.append(init_directive)
        styled_parts.append('')  # Blank line for readability
        
        # 3. ClassDef styling (only for diagram types that support it)
        # classDef is only supported for: flowchart, graph
        # NOT supported for: classDiagram, erDiagram, sequenceDiagram, stateDiagram
        body_text = '\n'.join(body_lines)
        supports_classdef = detected_diagram_type and detected_diagram_type.lower() in ["flowchart", "graph"]
        
        if supports_classdef and "classDef" not in body_text:
            # Mermaid classDef syntax uses : (colon) for property assignments
            logger.debug(f"[agent3] Adding classDef statements for {detected_diagram_type} diagram type")
            style_lines = [
                f"classDef primaryNode fill:{style_config_dict['primaryColor']},stroke:{style_config_dict['primaryColor']},stroke-width:2px,color:#fff",
                f"classDef secondaryNode fill:{style_config_dict['secondaryColor']},stroke:{style_config_dict['secondaryColor']},stroke-width:2px,color:#fff",
                f"classDef accentNode fill:{style_config_dict['accentColor']},stroke:{style_config_dict['accentColor']},stroke-width:2px,color:#fff",
            ]
            styled_parts.append('\n'.join(style_lines))
            styled_parts.append('')  # Blank line before diagram body
        elif detected_diagram_type and not supports_classdef:
            logger.debug(f"[agent3] Skipping classDef for {detected_diagram_type} diagram type (not supported)")
        
        # 4. Rest of diagram
        styled_parts.append('\n'.join(body_lines))
        
        styled_mermaid = '\n'.join(styled_parts).strip()
        
        logger.info(
            f"[agent3] Mermaid diagram generation complete | "
            f"original_length={len(mermaid)} chars | styled_length={len(styled_mermaid)} chars | "
            f"domain={full_config['domain']} | theme={full_config['theme']} | "
            f"complexity_score={complexity_info['complexity_score']} | diagram_type={complexity_info['recommended_type']}"
        )
        
        # Debug: Log first few lines of final diagram
        first_lines = "\n".join(styled_mermaid.split("\n")[:5])
        logger.debug(f"[agent3] Final diagram preview (first 5 lines):\n{first_lines}")
        
        return styled_mermaid


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
        response = await client.messages.create(
            model=model,
            max_tokens=800,
            temperature=0.3,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )
        usage = getattr(response, "usage", None)
        if usage:
            logger.info(f"[agent3] generate_diagram_for_project API call successful | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}")
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
    
    # Generate style configuration from prompt (consistent across all diagrams for this project)
    style_generator = StyleConfigGenerator(project_description, project_id)
    full_config = style_generator.generate_full_config(features, stories)
    style_config = {
        "domain": full_config["domain"],
        "theme": full_config["theme"],
        "primaryColor": full_config["colors"]["primary"],
        "secondaryColor": full_config["colors"]["secondary"],
        "accentColor": full_config["colors"]["tertiary"],
        "backgroundColor": "#ffffff",
        "arrowStyle": "solid",
        "fontSize": "16px",
        "fontFamily": "Arial, sans-serif",
        "nodeShape": "rect",
    }

    # Extract feature titles for explicit use in diagrams
    feature_titles = [
        feature.get('feature_text') or feature.get('title') or f'Feature {idx}'
        for idx, feature in enumerate(features, start=1)
    ]
    
    feature_details = "\n".join(
        f"{idx}. {feature.get('feature_text') or feature.get('title') or 'Feature'}"
        for idx, feature in enumerate(features, start=1)
    )

    story_lines = "\n".join(
        f"{idx}. {story.get('story_text') or 'As a user, I want ...'}"
        for idx, story in enumerate(stories, start=1)
    )

    # Infer domain from project description/title using helper function
    logger.debug(f"[agent3] Inferring project domain from title: '{project_title}' | description length: {len(project_description)}")
    project_domain, domain_hints = infer_project_domain(project_title, project_description)
    logger.info(f"[agent3] Inferred project domain: {project_domain} | hints: {domain_hints}")
    logger.debug(f"[agent3] Feature count: {len(features)} | Story count: {len(stories)}")
    logger.debug(f"[agent3] Feature titles: {feature_titles[:5]}")

    system_prompt = (
        "You are Agent-3, a senior software architect specializing in creating domain-specific, "
        "visually rich architecture diagrams. Your diagrams must be uniquely tailored to each project, "
        "using project-specific terminology, feature names, and domain concepts. "
        "NEVER reuse generic templates or node names across different projects.\n\n"
        "CRITICAL REQUIREMENTS FOR UNIQUENESS:\n"
        "1. Each diagram MUST reflect the SPECIFIC project title, description, and features provided\n"
        "2. Use EXACT feature names and terminology from the project (do not generalize)\n"
        "3. Create domain-specific component names based on the project's actual features\n"
        "4. Vary diagram structure, node relationships, and flow patterns for each unique project\n"
        "5. Include project-specific entities, services, and data models that match the domain\n"
        "6. NEVER use placeholder names like 'UserService', 'DataService' - use project-specific names\n"
        "7. The diagram structure should be different for different projects even if they share similar domains"
    )

    # Create a unique project fingerprint for debugging and ensuring uniqueness
    project_fingerprint = f"{project_title}|{len(project_description)}|{len(features)}|{len(stories)}"
    logger.info(f"[agent3] Generating designs for project | fingerprint={project_fingerprint} | title={project_title} | domain={project_domain}")
    logger.debug(f"[agent3] Project description (first 200 chars): {project_description[:200]}")
    logger.debug(f"[agent3] Feature count: {len(features)} | Story count: {len(stories)}")
    logger.debug(f"[agent3] Feature titles: {feature_titles[:10]}")
    
    user_prompt = (
        f"PROJECT CONTEXT (UNIQUE IDENTIFIER: {project_fingerprint}):\n"
        f"Project Title: {project_title}\n"
        f"Project Description: {project_description}\n\n"
        f"DOMAIN DETECTION:\n"
        f"This project is detected as a {project_domain} application. "
        f"Design the architecture components and database entities that make sense for this SPECIFIC project, not generic ones.\n"
        f"For {project_domain} applications, typical components include: {domain_hints}.\n"
        f"However, you MUST create components specific to THIS project's features, not generic {project_domain} components.\n\n"
        f"FEATURES (use these EXACT feature names and terminology in your diagrams - DO NOT generalize):\n"
        f"{feature_details or 'None provided'}\n\n"
        f"USER STORIES:\n"
        f"{story_lines or 'None provided'}\n\n"
        f"CRITICAL UNIQUENESS REQUIREMENTS:\n"
        f"1. This diagram is for project '{project_title}' - it MUST be different from any other project\n"
        f"2. Use the EXACT feature names listed above: {', '.join(feature_titles[:5])}\n"
        f"3. Create component/service names that reflect these specific features (e.g., if features mention 'Payment', create 'PaymentService', not 'GenericService')\n"
        f"4. The diagram structure, node relationships, and flow MUST reflect THIS project's unique requirements\n"
        f"5. Database entities MUST be based on the actual features and stories provided, not generic schemas\n"
        f"6. If this is a {project_domain} project, create {project_domain}-specific components, but make them unique to THIS project\n\n"
        f"REQUIREMENTS:\n"
        f"Generate THREE distinct, domain-specific Mermaid diagrams. Each diagram must be uniquely tailored "
        f"to this specific project ({project_title}) and its {project_domain} domain.\n\n"
        f"Make this diagram structurally different and domain-specific. Do NOT reuse generic node names "
        f"or a fixed template from previous designs. Each project should produce DIFFERENT diagrams.\n\n"
        f"1) HIGH-LEVEL DESIGN (HLD):\n"
        f"   - MUST use flowchart LR (or TB) with subgraphs grouping components\n"
        f"   - MUST include subgraphs like 'Frontend', 'Backend', 'Data Layer', 'AI/Agents'\n"
        f"   - MUST use project-specific service names based on features:\n"
        f"     * For e-commerce: ProductCatalogService, CartService, PaymentGateway, OrderService\n"
        f"     * For banking: AccountsService, TransactionsService, KYCService, LedgerService\n"
        f"     * For this project ({project_domain}): Create domain-appropriate service names based on: {', '.join(feature_titles[:5])}\n"
        f"   - MUST include Mermaid styling with classDef and class assignments:\n"
        f"     classDef user fill:#fce4ec,stroke:#ec407a,stroke-width:2px;\n"
        f"     classDef frontend fill:#e3f2fd,stroke:#1e88e5,stroke-width:2px;\n"
        f"     classDef backend fill:#e8f5e9,stroke:#43a047,stroke-width:2px;\n"
        f"     classDef db fill:#fff3e0,stroke:#fb8c00,stroke-width:2px;\n"
        f"     classDef ai fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px;\n"
        f"   - Use rounded corners for main components: ([ComponentName])\n"
        f"   - Use different shapes: ((Circle)) for external services, [(Database)] for data stores\n\n"
        f"2) LOW-LEVEL DESIGN (LLD):\n"
        f"   - MUST go one level deeper than HLD, showing key internal modules, services, or endpoints\n"
        f"   - MUST use at least one subgraph and one classDef style block\n"
        f"   - MUST show detailed component interactions with project-specific names\n"
        f"   - Use classDiagram, sequenceDiagram, or detailed flowchart syntax\n"
        f"   - Include API endpoints, service layers, and data flow specific to this project\n"
        f"   - Apply the same classDef styling as HLD for consistency\n\n"
        f"3) DATABASE DESIGN (DBD):\n"
        f"   - MUST use erDiagram syntax\n"
        f"   - MUST create entities specific to this project, NOT generic USERS, PROJECTS\n"
        f"   - Base entities on the features: {', '.join(feature_titles[:5])}\n"
        f"   - Include clear relationships (one-to-one, one-to-many, many-to-many)\n"
        f"   - Show primary keys, foreign keys, and attributes relevant to the domain\n\n"
        f"OUTPUT FORMAT:\n"
        f"Return ONLY valid JSON with NO markdown fences (no ```json or ```):\n"
        f"{{\n"
        f'  "hld_mermaid": "<Mermaid code>",\n'
        f'  "lld_mermaid": "<Mermaid code>",\n'
        f'  "dbd_mermaid": "<Mermaid erDiagram code>"\n'
        f"}}\n"
        f"Do NOT wrap in ``` fences. Do NOT add any extra keys or explanations. "
        f"Each mermaid field must contain complete, valid Mermaid syntax ready to render."
    )

    # Use debug model if available, otherwise default
    model = os.getenv("CLAUDE_MODEL_DEBUG") or os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)
    logger.info(f"[agent3] generate_designs_for_project | model={model} | project={project_title} | fingerprint={project_fingerprint}")
    logger.info(f"[agent3] API parameters | temperature=0.8 | top_p=0.95 | max_tokens=4000")
    
    try:
        # Use system and user prompts separately for better instruction following
        # Higher temperature (0.8) for more creative, diverse diagram generation
        # top_p (0.95) allows more diverse token selection while maintaining quality
        logger.debug(f"[agent3] System prompt length: {len(system_prompt)} chars")
        logger.debug(f"[agent3] User prompt length: {len(user_prompt)} chars")
        logger.debug(f"[agent3] User prompt preview (first 500 chars): {user_prompt[:500]}")
        logger.debug(f"[agent3] User prompt preview (last 500 chars): {user_prompt[-500:] if len(user_prompt) > 500 else user_prompt}")
        
        import time
        api_start_time = time.time()
        
        response = await client.messages.create(
            model=model,
            max_tokens=4000,  # High enough to return full Mermaid code for all three diagrams
            temperature=0.8,  # Increased from 0.3 for more creative and varied outputs
            top_p=0.95,  # Nucleus sampling: consider tokens with cumulative probability up to 95%
            system=system_prompt,
            messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
        )
        
        api_elapsed = time.time() - api_start_time
        usage = getattr(response, "usage", None)
        if usage:
            logger.info(f"[agent3] API call successful | elapsed={api_elapsed:.2f}s | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens} | total={usage.input_tokens + usage.output_tokens}")
            logger.debug(f"[agent3] Token usage breakdown: input={usage.input_tokens}, output={usage.output_tokens}")
        else:
            logger.info(f"[agent3] API call successful | elapsed={api_elapsed:.2f}s")
    except anthropic.APIError as exc:
        error_type = getattr(exc, 'type', 'unknown')
        error_status = getattr(exc, 'status_code', None)
        logger.error(f"[agent3] generate_designs_for_project APIError - Type: {error_type}, Status: {error_status}, Message: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Claude API error while generating designs"
        ) from exc

    # Extract response text using helper function
    logger.debug("[agent3] Extracting response text from Claude API response")
    try:
        response_text = extract_text(response)
        logger.debug(f"[agent3] Extracted response text: {len(response_text)} chars")
        logger.debug(f"[agent3] Response preview (first 300 chars): {response_text[:300]}")
        logger.debug(f"[agent3] Response preview (last 200 chars): {response_text[-200:] if len(response_text) > 200 else response_text}")
    except RuntimeError as exc:
        logger.error(f"[agent3] Failed to extract text from response: {exc}", exc_info=True)
        logger.debug(f"[agent3] Response object type: {type(response)} | attributes: {dir(response)[:10]}")
        raise HTTPException(
            status_code=500, detail="Failed to extract response from Claude API"
        ) from exc

    # Use coerce_json helper to handle markdown fences and truncation
    logger.debug("[agent3] Parsing JSON from response using coerce_json helper")
    try:
        design_data = coerce_json(response_text)
        logger.debug(f"[agent3] Successfully parsed JSON: type={type(design_data)} | keys={list(design_data.keys()) if isinstance(design_data, dict) else 'N/A'}")
        
        # Log each key's value length for debugging
        if isinstance(design_data, dict):
            for key, value in design_data.items():
                if isinstance(value, str):
                    logger.debug(f"[agent3] JSON key '{key}': {len(value)} chars | preview: {value[:100]}...")
                else:
                    logger.debug(f"[agent3] JSON key '{key}': type={type(value)} | value={str(value)[:100]}")
    except RuntimeError as exc:
        logger.error(f"[agent3] Failed to parse JSON from response: {exc}", exc_info=True)
        logger.debug(f"[agent3] Raw response text that failed (first 500 chars): {response_text[:500]}")
        logger.debug(f"[agent3] Raw response text that failed (last 500 chars): {response_text[-500:] if len(response_text) > 500 else response_text}")
        raise HTTPException(
            status_code=500, detail=f"Claude response could not be parsed as JSON: {str(exc)}"
        ) from exc
    except Exception as exc:
        logger.error(f"[agent3] Unexpected error parsing JSON: {exc}", exc_info=True)
        logger.debug(f"[agent3] Exception type: {type(exc).__name__} | Response text length: {len(response_text)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to parse Claude response: {str(exc)}"
        ) from exc

    # Extract and validate mermaid strings
    logger.debug("[agent3] Extracting mermaid strings from parsed JSON")
    hld_mermaid_raw = design_data.get("hld_mermaid", "")
    lld_mermaid_raw = design_data.get("lld_mermaid", "")
    dbd_mermaid_raw = design_data.get("dbd_mermaid", "")
    
    logger.debug(f"[agent3] Raw mermaid strings - HLD: {len(hld_mermaid_raw)} chars, LLD: {len(lld_mermaid_raw)} chars, DBD: {len(dbd_mermaid_raw)} chars")
    
    # Validate types and strip
    if not isinstance(hld_mermaid_raw, str):
        logger.warning(f"[agent3] HLD mermaid is not a string, type={type(hld_mermaid_raw)}")
        hld_mermaid_raw = ""
    if not isinstance(lld_mermaid_raw, str):
        logger.warning(f"[agent3] LLD mermaid is not a string, type={type(lld_mermaid_raw)}")
        lld_mermaid_raw = ""
    if not isinstance(dbd_mermaid_raw, str):
        logger.warning(f"[agent3] DBD mermaid is not a string, type={type(dbd_mermaid_raw)}")
        dbd_mermaid_raw = ""
    
    hld_mermaid = hld_mermaid_raw.strip()
    lld_mermaid = lld_mermaid_raw.strip()
    dbd_mermaid = dbd_mermaid_raw.strip()
    
    logger.debug(f"[agent3] Stripped mermaid strings - HLD: {len(hld_mermaid)} chars, LLD: {len(lld_mermaid)} chars, DBD: {len(dbd_mermaid)} chars")
    
    # Validate minimum content length
    min_length = 50  # Minimum reasonable length for a valid diagram
    if hld_mermaid and len(hld_mermaid) < min_length:
        logger.warning(f"[agent3] HLD diagram seems too short ({len(hld_mermaid)} chars), may be invalid")
    if lld_mermaid and len(lld_mermaid) < min_length:
        logger.warning(f"[agent3] LLD diagram seems too short ({len(lld_mermaid)} chars), may be invalid")
    if dbd_mermaid and len(dbd_mermaid) < min_length:
        logger.warning(f"[agent3] DBD diagram seems too short ({len(dbd_mermaid)} chars), may be invalid")
    
    # Log preview of each diagram
    if hld_mermaid:
        logger.debug(f"[agent3] HLD preview: {hld_mermaid[:150]}...")
    if lld_mermaid:
        logger.debug(f"[agent3] LLD preview: {lld_mermaid[:150]}...")
    if dbd_mermaid:
        logger.debug(f"[agent3] DBD preview: {dbd_mermaid[:150]}...")
    
    # Validate that we have at least one non-empty diagram
    if not hld_mermaid and not lld_mermaid and not dbd_mermaid:
        logger.error("[agent3] All three diagram types are empty after parsing")
        logger.error(f"[agent3] Design data keys: {list(design_data.keys())}")
        logger.error(f"[agent3] Design data values types: HLD={type(hld_mermaid_raw)}, LLD={type(lld_mermaid_raw)}, DBD={type(dbd_mermaid_raw)}")
        raise HTTPException(
            status_code=500, detail="Claude returned empty diagrams. All three diagram types (HLD, LLD, DBD) are empty."
        )
    
    # Log which diagrams are present with detailed analysis
    diagrams_present = []
    if hld_mermaid:
        diagrams_present.append(f"HLD ({len(hld_mermaid)} chars)")
        # Log first few lines of each diagram for debugging uniqueness
        hld_first_lines = "\n".join(hld_mermaid.split("\n")[:3])
        logger.debug(f"[agent3] HLD diagram preview (first 3 lines):\n{hld_first_lines}")
    if lld_mermaid:
        diagrams_present.append(f"LLD ({len(lld_mermaid)} chars)")
        lld_first_lines = "\n".join(lld_mermaid.split("\n")[:3])
        logger.debug(f"[agent3] LLD diagram preview (first 3 lines):\n{lld_first_lines}")
    if dbd_mermaid:
        diagrams_present.append(f"DBD ({len(dbd_mermaid)} chars)")
        dbd_first_lines = "\n".join(dbd_mermaid.split("\n")[:3])
        logger.debug(f"[agent3] DBD diagram preview (first 3 lines):\n{dbd_first_lines}")
    
    logger.info(f"[agent3] Successfully extracted diagrams: {', '.join(diagrams_present)}")
    logger.info(f"[agent3] Design generation complete for project '{project_title}' | fingerprint={project_fingerprint}")
    
    # Check for uniqueness indicators (project-specific terms in diagrams)
    project_terms_found = []
    all_diagrams = f"{hld_mermaid} {lld_mermaid} {dbd_mermaid}".lower()
    for term in feature_titles[:5]:
        if term.lower() in all_diagrams:
            project_terms_found.append(term)
    
    if project_terms_found:
        logger.info(f"[agent3] Project-specific terms found in diagrams: {', '.join(project_terms_found[:5])}")
    else:
        logger.warning(f"[agent3] WARNING: No project-specific feature terms found in generated diagrams - diagrams may be too generic")
    
    # Warn if any diagram is missing but don't fail
    if not hld_mermaid:
        logger.warning("[agent3] HLD diagram is empty")
    if not lld_mermaid:
        logger.warning("[agent3] LLD diagram is empty")
    if not dbd_mermaid:
        logger.warning("[agent3] DBD diagram is empty")

    document = {
        "project_id": project_id,
        "hld_mermaid": hld_mermaid,
        "lld_mermaid": lld_mermaid,
        "dbd_mermaid": dbd_mermaid,
        "style_config": style_config,
        "created_at": datetime.datetime.utcnow(),
    }

    logger.debug(f"[agent3] Preparing to insert document with diagram lengths - HLD: {len(hld_mermaid)}, LLD: {len(lld_mermaid)}, DBD: {len(dbd_mermaid)}")
    insert_result = await db["designs"].insert_one(document)
    document["_id"] = str(insert_result.inserted_id)
    logger.info(f"[agent3] Successfully persisted designs to database | document_id={document['_id']}")
    return document

