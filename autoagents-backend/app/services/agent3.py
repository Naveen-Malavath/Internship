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

    async def _extract_entities(
        self,
        features: List[Dict],
        stories: List[Dict],
        original_prompt: str,
        project_title: str,
    ) -> List[Dict[str, Any]]:
        """Extract business entities from features for database design.
        
        Analyzes features and stories to identify:
        - Primary entities (core business objects like User, Product, Order)
        - Secondary entities (supporting objects like Address, Payment, Review)
        - Junction entities for M:M relationships (OrderItem, UserRole)
        
        Returns:
            List of entity dictionaries with name, type, description, and feature/story sources
        """
        logger.info(f"[agent3] 🔍 Extracting entities from {len(features)} features and {len(stories)} stories")
        
        try:
            client = get_claude_client()
        except RuntimeError as exc:
            logger.error(f"[agent3] Failed to get Claude client for entity extraction: {exc}")
            raise
        
        # Format features with IDs for entity extraction and linking
        feature_list = "\n".join(
            f"[F{idx}] {f.get('feature_text') or f.get('title') or 'Feature'}"
            for idx, f in enumerate(features, 1)
        )
        
        # Format stories with IDs for context and linking
        story_list = "\n".join(
            f"[S{idx}] {s.get('story_text') or s.get('user_story') or 'Story'}"
            for idx, s in enumerate(stories[:15], 1)  # Limit to avoid token overflow
        )
        
        system_prompt = (
            "You are a database architect expert. Analyze the given features and user stories to identify "
            "all business entities that need database tables. Be thorough - extract ALL nouns that represent "
            "persistent data objects. ALSO track which features/stories mention each entity."
        )
        
        user_prompt = f"""Project: {project_title}

Original Requirements:
{original_prompt[:1500] if original_prompt else 'Not provided'}

Features to analyze (with IDs):
{feature_list}

User Stories context (with IDs):
{story_list or 'None provided'}

Extract ALL business entities (nouns) that need database tables. Categorize them and LINK to source features/stories:
- **primary**: Core business entities (User, Product, Order, etc.)
- **secondary**: Supporting entities (Address, Category, Review, etc.)
- **junction**: Many-to-many relationship tables (OrderItem, UserRole, ProductCategory)

Return ONLY valid JSON in this exact format:
{{
    "entities": [
        {{"name": "USER", "type": "primary", "description": "Stores user account information", "sources": ["F1", "F2", "S1"]}},
        {{"name": "PRODUCT", "type": "primary", "description": "Product catalog items", "sources": ["F3", "S2"]}},
        {{"name": "ORDER", "type": "primary", "description": "Customer orders", "sources": ["F4", "F5", "S3"]}},
        {{"name": "ORDER_ITEM", "type": "junction", "description": "Links orders to products with quantity", "sources": ["F4"]}},
        {{"name": "CATEGORY", "type": "secondary", "description": "Product categories", "sources": ["F3"]}}
    ]
}}

Rules:
- Entity names MUST be UPPERCASE with underscores (e.g., USER, ORDER_ITEM)
- Include "sources" array with feature IDs (F1, F2...) and story IDs (S1, S2...) that mention this entity
- Include at least USER entity for authentication
- Include audit-related entities if features mention tracking/history
- Include junction tables for many-to-many relationships
- Be comprehensive - extract ALL relevant entities from features"""

        try:
            response = await client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
            )
            
            response_text = extract_text(response).strip()
            logger.debug(f"[agent3] Entity extraction response: {response_text[:500]}...")
            
            # Parse JSON response
            # Remove markdown code fences if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            
            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                entities = data.get("entities", [])
                
                logger.info(f"[agent3] ✅ Extracted {len(entities)} entities: {[e.get('name') for e in entities]}")
                return entities
            else:
                logger.warning("[agent3] Could not find JSON in entity extraction response")
                return []
                
        except (json.JSONDecodeError, APIError) as exc:
            logger.error(f"[agent3] Entity extraction failed: {exc}")
            return []

    async def _generate_entity_fields(
        self,
        entity: Dict[str, Any],
        all_entities: List[Dict[str, Any]],
        domain_context: str,
    ) -> str:
        """Generate database fields for a specific entity.
        
        Args:
            entity: Entity dictionary with name, type, description
            all_entities: All entities for FK reference
            domain_context: Project domain for context-aware field generation
            
        Returns:
            Mermaid erDiagram entity block string
        """
        entity_name = entity.get("name", "ENTITY")
        entity_type = entity.get("type", "primary")
        entity_desc = entity.get("description", "")
        
        logger.debug(f"[agent3] Generating fields for entity: {entity_name} ({entity_type})")
        
        try:
            client = get_claude_client()
        except RuntimeError as exc:
            logger.error(f"[agent3] Failed to get Claude client for field generation: {exc}")
            raise
        
        # List other entities for FK references
        other_entities = [e.get("name") for e in all_entities if e.get("name") != entity_name]
        
        system_prompt = (
            "You are a database architect. Generate appropriate database fields for the given entity. "
            "Output ONLY the Mermaid erDiagram entity block syntax, nothing else."
        )
        
        user_prompt = f"""Generate database fields for the entity "{entity_name}" in a {domain_context} application.

Entity Description: {entity_desc}
Entity Type: {entity_type}

Related entities that may need FK references: {', '.join(other_entities)}

Generate the Mermaid erDiagram entity block with:
1. Primary key: uuid id PK
2. Business-specific fields based on entity type and description
3. Foreign keys (FK) to related entities where appropriate
4. Audit fields: timestamp created_at, timestamp updated_at

Use these data types:
- uuid for IDs and foreign keys
- varchar for short text (names, emails, status - max 255 chars)
- text for long content (descriptions, notes)
- int for counts/quantities
- float for prices/amounts  
- boolean for flags (is_active, is_verified)
- timestamp for dates/times
- json for complex nested data

Constraints: PK (Primary Key), FK (Foreign Key), UK (Unique Key)

Output ONLY valid Mermaid syntax like:
{entity_name} {{
    uuid id PK
    varchar field_name
    uuid related_entity_id FK
    timestamp created_at
    timestamp updated_at
}}

No explanations, just the entity block."""

        try:
            response = await client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
            )
            
            field_block = extract_text(response).strip()
            
            # Clean up the response
            if field_block.startswith("```"):
                lines = field_block.split("\n")
                field_block = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            
            # Ensure the block has proper structure
            field_block = field_block.strip()
            if not field_block.startswith(entity_name):
                # Try to find the entity block in the response
                pattern = rf'{entity_name}\s*\{{'
                match = re.search(pattern, field_block)
                if match:
                    start = match.start()
                    # Find matching closing brace
                    brace_count = 0
                    end = start
                    for i, char in enumerate(field_block[start:]):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end = start + i + 1
                                break
                    field_block = field_block[start:end]
            
            logger.debug(f"[agent3] Generated fields for {entity_name}: {field_block[:200]}...")
            return field_block
            
        except APIError as exc:
            logger.error(f"[agent3] Field generation failed for {entity_name}: {exc}")
            # Return minimal valid entity block
            return f"""{entity_name} {{
    uuid id PK
    timestamp created_at
    timestamp updated_at
}}"""

    def _infer_relationships(
        self,
        entities: List[Dict[str, Any]],
    ) -> List[str]:
        """Infer relationships between entities based on entity types and names.
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            List of Mermaid relationship strings
        """
        logger.info(f"[agent3] 🔗 Inferring relationships for {len(entities)} entities")
        
        relationships = []
        entity_names = [e.get("name", "") for e in entities]
        
        # Common relationship patterns
        # USER typically has one-to-many with most entities
        if "USER" in entity_names:
            for entity in entities:
                name = entity.get("name", "")
                entity_type = entity.get("type", "")
                
                if name == "USER":
                    continue
                    
                # User typically creates/owns orders, posts, reviews, etc.
                if name in ["ORDER", "REVIEW", "COMMENT", "POST", "BOOKING", "APPOINTMENT", "CART"]:
                    relationships.append(f"USER ||--o{{ {name} : places")
                elif name == "ADDRESS":
                    relationships.append(f"USER ||--o{{ ADDRESS : has")
                elif name == "PAYMENT":
                    relationships.append(f"USER ||--o{{ PAYMENT : makes")
                elif name == "PROFILE":
                    relationships.append(f"USER ||--|| PROFILE : has")
                elif name == "NOTIFICATION":
                    relationships.append(f"USER ||--o{{ NOTIFICATION : receives")
        
        # Order-related relationships
        if "ORDER" in entity_names:
            if "ORDER_ITEM" in entity_names:
                relationships.append("ORDER ||--o{ ORDER_ITEM : contains")
            if "PAYMENT" in entity_names:
                relationships.append("ORDER ||--o{ PAYMENT : requires")
            if "SHIPPING" in entity_names or "SHIPMENT" in entity_names:
                ship_name = "SHIPPING" if "SHIPPING" in entity_names else "SHIPMENT"
                relationships.append(f"ORDER ||--|| {ship_name} : has")
        
        # Product-related relationships  
        if "PRODUCT" in entity_names:
            if "ORDER_ITEM" in entity_names:
                relationships.append("PRODUCT ||--o{ ORDER_ITEM : included_in")
            if "CATEGORY" in entity_names:
                relationships.append("CATEGORY ||--o{ PRODUCT : categorizes")
            if "REVIEW" in entity_names:
                relationships.append("PRODUCT ||--o{ REVIEW : has")
            if "INVENTORY" in entity_names:
                relationships.append("PRODUCT ||--|| INVENTORY : tracked_by")
            if "PRODUCT_IMAGE" in entity_names:
                relationships.append("PRODUCT ||--o{ PRODUCT_IMAGE : has")
        
        # Category hierarchies
        if "CATEGORY" in entity_names:
            # Self-referencing for parent/child categories is implied
            pass
        
        # Junction table relationships
        for entity in entities:
            if entity.get("type") == "junction":
                name = entity.get("name", "")
                desc = entity.get("description", "").lower()
                
                # Try to infer what entities it connects
                if "user" in desc and "role" in desc:
                    if "ROLE" in entity_names:
                        relationships.append(f"USER ||--o{{ {name} : has")
                        relationships.append(f"ROLE ||--o{{ {name} : assigned_to")
                elif "product" in desc and "category" in desc:
                    if "CATEGORY" in entity_names:
                        relationships.append(f"PRODUCT }}o--o{{ CATEGORY : belongs_to")
        
        # Appointment/Booking systems
        if "APPOINTMENT" in entity_names or "BOOKING" in entity_names:
            appt_name = "APPOINTMENT" if "APPOINTMENT" in entity_names else "BOOKING"
            if "DOCTOR" in entity_names:
                relationships.append(f"DOCTOR ||--o{{ {appt_name} : schedules")
            if "PATIENT" in entity_names:
                relationships.append(f"PATIENT ||--o{{ {appt_name} : books")
            if "SERVICE" in entity_names:
                relationships.append(f"SERVICE ||--o{{ {appt_name} : booked_for")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_relationships = []
        for rel in relationships:
            if rel not in seen:
                seen.add(rel)
                unique_relationships.append(rel)
        
        logger.info(f"[agent3] ✅ Inferred {len(unique_relationships)} relationships")
        return unique_relationships

    async def _generate_database_diagram_multistep(
        self,
        project_title: str,
        features: List[Dict],
        stories: List[Dict],
        original_prompt: str,
    ) -> str:
        """Generate database erDiagram using multi-step approach.
        
        1. Extract entities from features/stories
        2. Generate fields for each entity
        3. Infer relationships between entities
        4. Assemble complete erDiagram
        
        Returns:
            Complete Mermaid erDiagram source code
        """
        logger.info("[agent3] 🏗️ Starting multi-step database diagram generation")
        
        # Step 1: Extract entities
        entities = await self._extract_entities(
            features=features,
            stories=stories,
            original_prompt=original_prompt,
            project_title=project_title,
        )
        
        if not entities:
            logger.warning("[agent3] No entities extracted, using AI-generated approach")
            # If extraction fails, let the single-prompt approach handle it
            raise RuntimeError("Entity extraction returned no entities")
        
        # Determine domain from original prompt
        domain_context = self._detect_domain(original_prompt, features)
        logger.info(f"[agent3] 🎯 Detected domain: {domain_context}")
        
        # Step 2: Generate fields for each entity
        entity_blocks = []
        for entity in entities:
            try:
                field_block = await self._generate_entity_fields(
                    entity=entity,
                    all_entities=entities,
                    domain_context=domain_context,
                )
                if field_block:
                    entity_blocks.append(field_block)
            except Exception as exc:
                logger.warning(f"[agent3] Failed to generate fields for {entity.get('name')}: {exc}")
                # Create minimal block for this entity
                entity_name = entity.get("name", "ENTITY")
                entity_blocks.append(f"""{entity_name} {{
    uuid id PK
    timestamp created_at
    timestamp updated_at
}}""")
        
        # Step 3: Infer relationships
        relationships = self._infer_relationships(entities)
        
        # Step 4: Assemble the complete erDiagram
        diagram_parts = ["erDiagram"]
        
        # Add relationships first (Mermaid convention)
        if relationships:
            diagram_parts.append("")
            diagram_parts.extend([f"    {rel}" for rel in relationships])
        
        # Add entity blocks
        diagram_parts.append("")
        for block in entity_blocks:
            # Ensure proper indentation
            lines = block.strip().split("\n")
            indented_block = "\n".join(f"    {line}" if i > 0 else f"    {line}" for i, line in enumerate(lines))
            diagram_parts.append(indented_block)
            diagram_parts.append("")
        
        mermaid = "\n".join(diagram_parts)
        
        logger.info(f"[agent3] ✅ Multi-step database diagram complete | entities={len(entities)} | relationships={len(relationships)}")
        return mermaid

    def _detect_domain(self, original_prompt: str, features: List[Dict]) -> str:
        """Detect the application domain from prompt and features."""
        prompt_lower = (original_prompt or "").lower()
        feature_text = " ".join(
            (f.get("feature_text") or f.get("title") or "").lower()
            for f in features
        )
        combined = prompt_lower + " " + feature_text
        
        # Domain detection patterns
        if any(word in combined for word in ["e-commerce", "shopping", "cart", "product", "checkout", "store"]):
            return "e-commerce"
        elif any(word in combined for word in ["healthcare", "medical", "patient", "doctor", "hospital", "clinic"]):
            return "healthcare"
        elif any(word in combined for word in ["banking", "finance", "payment", "transaction", "account", "transfer"]):
            return "finance/banking"
        elif any(word in combined for word in ["education", "learning", "course", "student", "teacher", "school"]):
            return "education"
        elif any(word in combined for word in ["social", "post", "friend", "follow", "message", "chat"]):
            return "social media"
        elif any(word in combined for word in ["booking", "reservation", "hotel", "travel", "flight"]):
            return "booking/reservation"
        elif any(word in combined for word in ["inventory", "warehouse", "stock", "supply"]):
            return "inventory management"
        elif any(word in combined for word in ["crm", "customer", "lead", "sales", "pipeline"]):
            return "CRM"
        elif any(word in combined for word in ["project", "task", "team", "sprint", "agile"]):
            return "project management"
        else:
            return "general business application"

    def _generate_hld_fallback(self, features: List[Dict], project_title: str, original_prompt: str = "") -> str:
        """Generate HLD flowchart with proper architecture layers."""
        logger.info("[agent3] 🏗️ Generating HLD fallback diagram")
        
        # Extract key components from features
        components = []
        for f in features[:6]:
            text = (f.get('feature_text') or f.get('title') or '').lower()
            for word in ['user', 'product', 'order', 'cart', 'payment', 'inventory', 
                        'notification', 'search', 'report', 'admin', 'booking', 'customer']:
                if word in text and word.capitalize() not in components:
                    components.append(word.capitalize())
                    break
        
        if not components:
            components = ['User', 'Product', 'Order']
        components = components[:5]
        
        lines = ['graph TB']
        
        # Client Layer - use unique IDs to avoid conflicts
        lines.append('    subgraph CL[Client Layer]')
        lines.append('        C1[Web Browser]')
        lines.append('        C2[Mobile App]')
        lines.append('        C3[Admin Portal]')
        lines.append('    end')
        
        # API Layer
        lines.append('    subgraph AL[API Layer]')
        lines.append('        A1[API Gateway]')
        lines.append('        A2[Load Balancer]')
        lines.append('    end')
        
        # Service Layer
        lines.append('    subgraph SL[Service Layer]')
        lines.append('        S0[Auth Service]')
        for i, comp in enumerate(components):
            lines.append(f'        S{i+1}[{comp} Service]')
        lines.append('    end')
        
        # Data Layer
        lines.append('    subgraph DL[Data Layer]')
        lines.append('        D1[(MongoDB)]')
        lines.append('        D2[(Redis)]')
        lines.append('        D3[(Storage)]')
        lines.append('    end')
        
        # External Layer
        lines.append('    subgraph EL[External Services]')
        lines.append('        E1[Email]')
        lines.append('        E2[Payment]')
        lines.append('        E3[AI/ML]')
        lines.append('    end')
        
        # Connections from clients to API
        lines.append('    C1 --> A1')
        lines.append('    C2 --> A1')
        lines.append('    C3 --> A1')
        lines.append('    A1 --> A2')
        
        # API to Services
        lines.append('    A2 --> S0')
        for i in range(len(components)):
            lines.append(f'    A2 --> S{i+1}')
        
        # Services to Data
        lines.append('    S0 --> D1')
        lines.append('    S0 --> D2')
        for i in range(len(components)):
            lines.append(f'    S{i+1} --> D1')
            lines.append(f'    S{i+1} --> D2')
        
        # Services to External
        lines.append('    S0 --> E1')
        if len(components) >= 3:
            lines.append('    S3 --> E2')
        lines.append('    A1 --> E3')
        
        mermaid = '\n'.join(lines)
        logger.info(f"[agent3] ✅ Generated HLD with {len(components)} services")
        return mermaid

    def _generate_lld_fallback(self, features: List[Dict], project_title: str) -> str:
        """Generate detailed LLD classDiagram with multiple layers."""
        logger.info("[agent3] 🏗️ Generating LLD fallback diagram")
        
        # Extract entity names from features
        entities = []
        for f in features[:6]:
            text = (f.get('feature_text') or f.get('title') or '').lower()
            for word in ['user', 'product', 'order', 'cart', 'payment', 'customer', 
                        'category', 'review', 'inventory', 'notification', 'booking']:
                if word in text and word.capitalize() not in entities:
                    entities.append(word.capitalize())
                    break
        
        if not entities:
            entities = ['User', 'Product', 'Order']
        entities = entities[:4]
        
        lines = ['classDiagram']
        lines.append('    %% Controller Layer')
        
        for entity in entities:
            lines.append(f'    class {entity}Controller')
            lines.append(f'    {entity}Controller : -{entity.lower()}Service {entity}Service')
            lines.append(f'    {entity}Controller : +getAll() List')
            lines.append(f'    {entity}Controller : +getById(id) {entity}')
            lines.append(f'    {entity}Controller : +create(dto) {entity}')
            lines.append(f'    {entity}Controller : +update(id dto) {entity}')
            lines.append(f'    {entity}Controller : +delete(id) void')
            lines.append('')
        
        lines.append('    %% Service Layer')
        for entity in entities:
            lines.append(f'    class {entity}Service')
            lines.append(f'    {entity}Service : -{entity.lower()}Repo {entity}Repository')
            lines.append(f'    {entity}Service : -validator Validator')
            lines.append(f'    {entity}Service : -logger Logger')
            lines.append(f'    {entity}Service : +findAll() List')
            lines.append(f'    {entity}Service : +findById(id) {entity}')
            lines.append(f'    {entity}Service : +create(data) {entity}')
            lines.append(f'    {entity}Service : +update(id data) {entity}')
            lines.append(f'    {entity}Service : +delete(id) boolean')
            lines.append(f'    {entity}Service : +validate(data) boolean')
            lines.append('')
        
        lines.append('    %% Repository Layer')
        for entity in entities:
            lines.append(f'    class {entity}Repository')
            lines.append(f'    {entity}Repository : -database Database')
            lines.append(f'    {entity}Repository : -collection string')
            lines.append(f'    {entity}Repository : +save(entity) {entity}')
            lines.append(f'    {entity}Repository : +findById(id) {entity}')
            lines.append(f'    {entity}Repository : +findAll() List')
            lines.append(f'    {entity}Repository : +update(id entity) {entity}')
            lines.append(f'    {entity}Repository : +deleteById(id) boolean')
            lines.append(f'    {entity}Repository : +exists(id) boolean')
            lines.append('')
        
        lines.append('    %% Model/Entity Layer')
        for entity in entities:
            lines.append(f'    class {entity}')
            lines.append(f'    {entity} : -id string')
            lines.append(f'    {entity} : -name string')
            lines.append(f'    {entity} : -description string')
            lines.append(f'    {entity} : -status string')
            lines.append(f'    {entity} : -isActive boolean')
            lines.append(f'    {entity} : -createdAt DateTime')
            lines.append(f'    {entity} : -updatedAt DateTime')
            lines.append(f'    {entity} : +toJSON() object')
            lines.append(f'    {entity} : +validate() boolean')
            lines.append('')
        
        lines.append('    %% DTO Layer')
        for entity in entities:
            lines.append(f'    class {entity}DTO')
            lines.append(f'    {entity}DTO : +name string')
            lines.append(f'    {entity}DTO : +description string')
            lines.append(f'    {entity}DTO : +status string')
            lines.append('')
        
        lines.append('    %% Shared Components')
        lines.append('    class Database')
        lines.append('    Database : -connectionString string')
        lines.append('    Database : +connect() void')
        lines.append('    Database : +disconnect() void')
        lines.append('    Database : +getCollection(name) Collection')
        lines.append('')
        lines.append('    class Validator')
        lines.append('    Validator : +validate(data schema) boolean')
        lines.append('    Validator : +sanitize(data) object')
        lines.append('')
        lines.append('    class Logger')
        lines.append('    Logger : +info(msg) void')
        lines.append('    Logger : +error(msg) void')
        lines.append('    Logger : +debug(msg) void')
        lines.append('')
        
        lines.append('    %% Relationships')
        for entity in entities:
            lines.append(f'    {entity}Controller --> {entity}Service : uses')
            lines.append(f'    {entity}Service --> {entity}Repository : uses')
            lines.append(f'    {entity}Service --> Validator : uses')
            lines.append(f'    {entity}Service --> Logger : uses')
            lines.append(f'    {entity}Repository --> Database : uses')
            lines.append(f'    {entity}Repository --> {entity} : manages')
            lines.append(f'    {entity}Controller ..> {entity}DTO : receives')
        
        mermaid = '\n'.join(lines)
        logger.info(f"[agent3] ✅ Generated LLD with {len(entities)} entities")
        return mermaid

    def _generate_dbd_fallback(self, features: List[Dict], project_title: str) -> str:
        """Generate DBD erDiagram with detailed entities and relationships."""
        logger.info("[agent3] 🏗️ Generating DBD fallback diagram")
        
        # Detect entities from features
        detected = set()
        for f in features[:10]:
            text = (f.get('feature_text') or f.get('title') or '').lower()
            if 'user' in text or 'login' in text or 'auth' in text:
                detected.add('USERS')
            if 'product' in text or 'catalog' in text:
                detected.add('PRODUCTS')
            if 'order' in text or 'purchase' in text:
                detected.add('ORDERS')
            if 'cart' in text or 'basket' in text:
                detected.add('CARTS')
            if 'payment' in text or 'pay' in text:
                detected.add('PAYMENTS')
            if 'category' in text:
                detected.add('CATEGORIES')
            if 'review' in text or 'rating' in text:
                detected.add('REVIEWS')
            if 'address' in text or 'shipping' in text:
                detected.add('ADDRESSES')
            if 'inventory' in text or 'stock' in text:
                detected.add('INVENTORY')
        
        # Always include core entities
        detected.add('USERS')
        if 'ORDERS' in detected:
            detected.add('ORDER_ITEMS')
        if 'CARTS' in detected:
            detected.add('CART_ITEMS')
        
        # Build diagram - use ||--|| format (no curly braces in relationships)
        lines = ['erDiagram']
        lines.append('    %% Relationships')
        
        # User relationships
        if 'ORDERS' in detected:
            lines.append('    USERS ||--o| ORDERS : places')
        if 'CARTS' in detected:
            lines.append('    USERS ||--|| CARTS : owns')
        if 'ADDRESSES' in detected:
            lines.append('    USERS ||--o| ADDRESSES : has')
        if 'REVIEWS' in detected:
            lines.append('    USERS ||--o| REVIEWS : writes')
        
        # Product relationships
        if 'CATEGORIES' in detected and 'PRODUCTS' in detected:
            lines.append('    CATEGORIES ||--o| PRODUCTS : contains')
        if 'INVENTORY' in detected and 'PRODUCTS' in detected:
            lines.append('    PRODUCTS ||--|| INVENTORY : has')
        if 'REVIEWS' in detected and 'PRODUCTS' in detected:
            lines.append('    PRODUCTS ||--o| REVIEWS : receives')
        
        # Order relationships
        if 'ORDER_ITEMS' in detected:
            lines.append('    ORDERS ||--o| ORDER_ITEMS : contains')
        if 'PRODUCTS' in detected and 'ORDER_ITEMS' in detected:
            lines.append('    PRODUCTS ||--o| ORDER_ITEMS : in')
        if 'PAYMENTS' in detected:
            lines.append('    ORDERS ||--o| PAYMENTS : has')
        if 'ADDRESSES' in detected and 'ORDERS' in detected:
            lines.append('    ADDRESSES ||--o| ORDERS : ships_to')
        
        # Cart relationships
        if 'CART_ITEMS' in detected:
            lines.append('    CARTS ||--o| CART_ITEMS : contains')
        if 'PRODUCTS' in detected and 'CART_ITEMS' in detected:
            lines.append('    PRODUCTS ||--o| CART_ITEMS : added_to')
        
        lines.append('')
        lines.append('    %% Entity Definitions')
        
        # Entity field definitions
        entity_defs = {
            'USERS': [
                'int id PK',
                'varchar email',
                'varchar username',
                'varchar password_hash',
                'varchar first_name',
                'varchar last_name',
                'varchar phone',
                'varchar role',
                'boolean is_active',
                'datetime created_at',
                'datetime updated_at',
            ],
            'PRODUCTS': [
                'int id PK',
                'int category_id FK',
                'varchar sku',
                'varchar name',
                'text description',
                'decimal price',
                'decimal cost',
                'varchar image_url',
                'boolean is_active',
                'datetime created_at',
                'datetime updated_at',
            ],
            'CATEGORIES': [
                'int id PK',
                'int parent_id FK',
                'varchar name',
                'varchar slug',
                'text description',
                'int sort_order',
                'boolean is_active',
            ],
            'ORDERS': [
                'int id PK',
                'int user_id FK',
                'int address_id FK',
                'varchar order_number',
                'varchar status',
                'decimal subtotal',
                'decimal tax',
                'decimal shipping',
                'decimal total',
                'datetime ordered_at',
                'datetime shipped_at',
            ],
            'ORDER_ITEMS': [
                'int id PK',
                'int order_id FK',
                'int product_id FK',
                'varchar product_name',
                'int quantity',
                'decimal unit_price',
                'decimal subtotal',
            ],
            'CARTS': [
                'int id PK',
                'int user_id FK',
                'decimal subtotal',
                'decimal total',
                'datetime created_at',
                'datetime updated_at',
            ],
            'CART_ITEMS': [
                'int id PK',
                'int cart_id FK',
                'int product_id FK',
                'int quantity',
                'decimal unit_price',
            ],
            'PAYMENTS': [
                'int id PK',
                'int order_id FK',
                'varchar method',
                'varchar transaction_id',
                'decimal amount',
                'varchar status',
                'datetime paid_at',
            ],
            'ADDRESSES': [
                'int id PK',
                'int user_id FK',
                'varchar type',
                'varchar first_name',
                'varchar last_name',
                'varchar street',
                'varchar city',
                'varchar state',
                'varchar postal_code',
                'varchar country',
                'boolean is_default',
            ],
            'REVIEWS': [
                'int id PK',
                'int user_id FK',
                'int product_id FK',
                'int rating',
                'varchar title',
                'text comment',
                'boolean is_approved',
                'datetime created_at',
            ],
            'INVENTORY': [
                'int id PK',
                'int product_id FK',
                'int quantity',
                'int reserved',
                'int reorder_level',
                'datetime last_updated',
            ],
        }
        
        # Output entities in order
        entity_order = ['USERS', 'ADDRESSES', 'CATEGORIES', 'PRODUCTS', 'INVENTORY', 
                       'CARTS', 'CART_ITEMS', 'ORDERS', 'ORDER_ITEMS', 'PAYMENTS', 'REVIEWS']
        
        for entity in entity_order:
            if entity in detected:
                fields = entity_defs.get(entity, ['int id PK', 'varchar name', 'datetime created_at'])
                lines.append(f'    {entity} {{')
                for field in fields:
                    lines.append(f'        {field}')
                lines.append('    }')
        
        mermaid = '\n'.join(lines)
        logger.info(f"[agent3] ✅ Generated DBD with {len(detected)} entities")
        return mermaid

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
        
        # ==========================================================================
        # DIAGRAM GENERATION BY TYPE
        # ==========================================================================
        # All diagram types use reliable fallback generators for consistent output
        # Claude API often produces invalid/malformed diagrams
        # ==========================================================================
        
        if diagram_type.lower() == "lld":
            # LLD: Generate using reliable fallback (Claude often produces empty classes)
            logger.info("[agent3] 🏗️ Generating LLD class diagram with reliable fallback")
            mermaid = self._generate_lld_fallback(features, project_title)
            logger.info("[agent3] ✅ LLD classDiagram generated successfully")
            return mermaid  # Return early - no need for sanitization
            
        elif diagram_type.lower() == "database":
            # DBD: Generate using reliable fallback (Claude often produces unbalanced braces)
            logger.info("[agent3] 🗄️ Generating DBD erDiagram with reliable fallback")
            mermaid = self._generate_dbd_fallback(features, project_title)
            logger.info("[agent3] ✅ DBD erDiagram generated successfully")
            return mermaid  # Return early - no need for sanitization
            
        elif diagram_type.lower() == "hld":
            # HLD: Generate using reliable fallback for consistent system architecture
            logger.info("[agent3] 🏗️ Generating HLD flowchart with reliable fallback")
            mermaid = self._generate_hld_fallback(features, project_title, original_prompt)
            logger.info("[agent3] ✅ HLD flowchart generated successfully")
            return mermaid  # Return early - no need for sanitization
            
        else:  # Unknown type - use HLD as default
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

        # Only make API call for HLD (LLD and DBD use reliable fallback generators)
        if diagram_type.lower() == "hld":
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
        
        # QUALITY CHECK: Validate Claude output before sanitization (for erDiagram and classDiagram)
        if 'erDiagram' in mermaid or 'classDiagram' in mermaid:
            lines_check = mermaid.split('\n')
            entities_with_fields = 0
            empty_entities = 0
            classes_with_members = 0
            empty_classes = 0
            
            in_block = False
            current_block_has_content = False
            is_class_diagram = 'classDiagram' in mermaid
            
            for line in lines_check:
                stripped = line.strip()
                
                if is_class_diagram:
                    # Check for class definition
                    if re.match(r'^class\s+\w+\s*\{', stripped):
                        if in_block and current_block_has_content:
                            classes_with_members += 1
                        elif in_block:
                            empty_classes += 1
                        in_block = True
                        current_block_has_content = False
                    elif stripped == '}':
                        if in_block and current_block_has_content:
                            classes_with_members += 1
                        elif in_block:
                            empty_classes += 1
                        in_block = False
                    elif in_block and re.match(r'^[+\-#~]\w+', stripped):
                        current_block_has_content = True
                else:
                    # Check for entity definition (erDiagram)
                    if re.match(r'^[A-Z_][A-Z_0-9]*\s*\{', stripped):
                        if in_block and current_block_has_content:
                            entities_with_fields += 1
                        elif in_block:
                            empty_entities += 1
                        in_block = True
                        current_block_has_content = False
                    elif stripped == '}':
                        if in_block and current_block_has_content:
                            entities_with_fields += 1
                        elif in_block:
                            empty_entities += 1
                        in_block = False
                    elif in_block and re.match(r'^\s*(uuid|varchar|text|int|float|boolean|datetime|timestamp|json)', stripped):
                        current_block_has_content = True
            
            if is_class_diagram:
                total_classes = classes_with_members + empty_classes
                logger.info(f"[agent3] 🔍 Claude output quality (classDiagram): {classes_with_members}/{total_classes} classes have members, {empty_classes} empty")
                if total_classes > 0 and empty_classes > classes_with_members:
                    logger.warning(f"[agent3] ⚠️ Claude generated mostly EMPTY classes ({empty_classes}/{total_classes})")
                elif empty_classes > 0:
                    logger.info(f"[agent3] ℹ️ Some classes are empty, but this may be intentional")
            else:
                total_entities = entities_with_fields + empty_entities
                logger.info(f"[agent3] 🔍 Claude output quality (erDiagram): {entities_with_fields}/{total_entities} entities have fields, {empty_entities} empty")
                if total_entities > 0 and empty_entities > entities_with_fields:
                    logger.warning(f"[agent3] ⚠️ Claude generated mostly EMPTY entities ({empty_entities}/{total_entities})")
                    logger.warning(f"[agent3] This may indicate an issue with the Claude prompt or response truncation")
                elif empty_entities > 0:
                    logger.info(f"[agent3] ℹ️ Some entities are empty, but this may be fixed by sanitization")
        
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
                    # Use IMPROVED state machine: track if we're currently inside an entity block
                    is_field_line = re.match(r'^\s*(uuid|varchar|text|int|float|boolean|datetime|timestamp|json|bigint|smallint|decimal|double|real|date|time)\s+\w+', line_stripped)
                    
                    if is_field_line:
                        # IMPROVED: Better brace counting that handles indented fields correctly
                        # Track entity state more robustly
                        in_entity = False
                        current_entity = None
                        
                        for i in range(index):
                            prev_line = lines[i].strip()
                            
                            # Check for entity definition (same line with opening brace)
                            entity_match = re.match(r'^([A-Z_][A-Z_0-9]*)\s*\{', prev_line)
                            if entity_match:
                                in_entity = True
                                current_entity = entity_match.group(1)
                                logger.debug(f"[agent3] Line {i+1}: Entered entity '{current_entity}'")
                                continue
                            
                            # Check for entity name (opening brace on next line)
                            if re.match(r'^[A-Z_][A-Z_0-9]*$', prev_line) and not in_entity:
                                # Look ahead to see if next line has opening brace
                                if i + 1 < len(lines) and lines[i + 1].strip() == '{':
                                    in_entity = True
                                    current_entity = prev_line
                                    logger.debug(f"[agent3] Line {i+1}: Entered entity '{current_entity}' (brace on next line)")
                                continue
                            
                            # Check for standalone opening brace after entity name
                            if prev_line == '{' and i > 0 and not in_entity:
                                entity_line = lines[i-1].strip()
                                if re.match(r'^[A-Z_][A-Z_0-9]*$', entity_line):
                                    in_entity = True
                                    current_entity = entity_line
                                    logger.debug(f"[agent3] Line {i+1}: Confirmed entity '{current_entity}' with opening brace")
                                continue
                            
                            # Check for closing brace
                            if prev_line == '}' and in_entity:
                                logger.debug(f"[agent3] Line {i+1}: Exited entity '{current_entity}'")
                                in_entity = False
                                current_entity = None
                        
                        # Log the state when checking this field line
                        logger.debug(f"[agent3] Checking field at line {line_num}: in_entity={in_entity}, current_entity={current_entity}")
                        logger.debug(f"[agent3]   Field: {line_stripped[:60]}")
                        
                        # If we're not in an entity, this field is orphaned - REMOVE IT
                        if not in_entity:
                            logger.warning(f"[agent3] ⚠️ ORPHANED entity field outside entity block at line {line_num}: {line_stripped[:80]}")
                            removed_lines.append((line_num, line_stripped[:100]))
                            continue  # Skip this line completely
                        else:
                            logger.debug(f"[agent3] ✓ Field is inside entity '{current_entity}' - keeping it")
            
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
                        # IMPROVED: Better brace counting that handles class members correctly
                        # Count all braces from the start of the diagram to current line
                        in_class = False
                        brace_count = 0
                        
                        for i in range(index):
                            prev_line = lines[i].strip()
                            
                            # Check if this is a class definition line with opening brace
                            if re.match(r'^class\s+\w+.*\{', prev_line):
                                brace_count += 1
                            
                            # Check for standalone opening brace after class definition
                            elif prev_line == '{' and i > 0:
                                check_prev = lines[i-1].strip()
                                if check_prev.startswith('class '):
                                    brace_count += 1
                            
                            # Check for closing brace (must be standalone)
                            elif prev_line == '}':
                                brace_count -= 1
                                if brace_count < 0:
                                    brace_count = 0  # Prevent negative count
                        
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
            
            # SAFETY CHECK: Count how many fields were removed vs total fields
            if diagram_type_detected == 'er':
                removed_field_count = sum(1 for _, line_text in removed_lines 
                                        if re.match(r'^\s*(uuid|varchar|text|int|float|boolean|datetime|timestamp|json)', line_text))
                total_field_count = sum(1 for line in lines 
                                       if re.match(r'^\s*(uuid|varchar|text|int|float|boolean|datetime|timestamp|json)', line.strip()))
                
                if total_field_count > 0:
                    removal_percentage = (removed_field_count / total_field_count * 100)
                    logger.info(f"[agent3] 📊 Field removal stats: {removed_field_count}/{total_field_count} fields removed ({removal_percentage:.1f}%)")
                    
                    # If we removed too many fields, something is likely wrong with detection logic
                    if removal_percentage > 50:
                        logger.error(f"[agent3] ⚠️ SAFETY WARNING: Removed {removal_percentage:.1f}% of fields - this seems excessive!")
                        logger.error(f"[agent3] This may indicate a bug in orphaned field detection.")
                        logger.error(f"[agent3] Consider reviewing brace counting logic or Claude output quality.")
                        # Still apply removal but log heavily for debugging
                    elif removal_percentage > 25:
                        logger.warning(f"[agent3] ⚠️ Removed {removal_percentage:.1f}% of fields - verify this is correct")
        
        mermaid = '\n'.join(fixed_lines)
        
        # FINAL VALIDATION: Check for common structural issues
        logger.info("[agent3] 🔍 Performing final structural validation")
        
        # For classDiagram: Validate all classes have proper { } structure
        if 'classDiagram' in mermaid:
            lines = mermaid.split('\n')
            in_class_block = False
            brace_depth = 0
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Track class block state
                if re.match(r'^class\s+\w+\s*\{', stripped):
                    in_class_block = True
                    brace_depth += 1
                elif stripped == '}':
                    brace_depth -= 1
                    if brace_depth <= 0:
                        in_class_block = False
                        brace_depth = 0
                
                # Check if line starts with + - # ~ but we're not in a class
                if re.match(r'^[+\-#~]\w', stripped):
                    if not in_class_block:
                        logger.error(f"[agent3] ❌ CRITICAL: Found orphaned member at line {i+1}: {stripped[:50]}")
                        logger.error(f"[agent3]    This should have been caught earlier - check detection logic")
        
        # For erDiagram: Validate all entities have proper { } structure  
        if 'erDiagram' in mermaid:
            lines = mermaid.split('\n')
            in_entity_block = False
            brace_depth = 0
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Track entity block state
                if re.match(r'^[A-Z_][A-Z_0-9]*\s*\{', stripped):
                    in_entity_block = True
                    brace_depth += 1
                elif stripped == '}':
                    brace_depth -= 1
                    if brace_depth <= 0:
                        in_entity_block = False
                        brace_depth = 0
                
                # Check if line looks like a field but we're not in an entity
                if re.match(r'^(uuid|varchar|text|int|float|boolean|datetime|timestamp|json)\s+\w+', stripped):
                    if not in_entity_block:
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
            
            # If all entities are empty, generate a proper fallback
            if has_entities and not has_fields_in_entities:
                logger.warning("[agent3] ⚠️ All entities appear empty - generating proper DBD fallback")
                mermaid = self._generate_dbd_fallback(features, project_title)
                logger.info("[agent3] ✅ DBD fallback generated successfully")
        
        # Fix classDiagram-specific syntax issues (LLD diagrams)
        # This handles the parse error: "Expecting 'PS', 'TAGEND', 'STR', got 'PE'"
        # which occurs when class members are on the same line or have invalid syntax
        if 'classDiagram' in mermaid or diagram_type.lower() == 'lld':
            logger.info("[agent3] 🔧 Fixing classDiagram syntax for LLD")
            class_lines = mermaid.split('\n')
            
            # CRITICAL CHECK: Is this diagram completely malformed (no class definitions at all)?
            has_class_defs = any(re.match(r'^\s*class\s+\w+', line) for line in class_lines)
            has_members = any(re.match(r'^\s*[+\-#~]\w', line.strip()) for line in class_lines)
            
            # Count classes with actual content
            classes_with_content = 0
            in_class = False
            current_class_has_content = False
            for line in class_lines:
                stripped = line.strip()
                if re.match(r'^class\s+\w+\s*\{', stripped):
                    in_class = True
                    current_class_has_content = False
                elif stripped == '}' and in_class:
                    if current_class_has_content:
                        classes_with_content += 1
                    in_class = False
                elif in_class and re.match(r'^[+\-#~]\w', stripped):
                    current_class_has_content = True
            
            # If no classes have content, generate a proper LLD fallback
            if has_class_defs and classes_with_content == 0:
                logger.warning("[agent3] ⚠️ classDiagram has class definitions but NO members inside!")
                logger.info("[agent3] 🔧 Generating proper LLD with class members...")
                
                # Generate a proper LLD based on features
                mermaid = self._generate_lld_fallback(features, project_title)
                class_lines = mermaid.split('\n')
                has_class_defs = True
                has_members = True
            
            if has_members and not has_class_defs:
                logger.warning("[agent3] ⚠️ classDiagram has NO class definitions, only orphaned members")
                logger.warning("[agent3] Continuing with current diagram state (no hardcoded fallback)")
                # Continue with fixing logic to remove orphaned members
            
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
                logger.warning("[agent3] ⚠️ Detected malformed classDiagram with only closing braces")
                logger.warning("[agent3] Continuing with current diagram state (no hardcoded fallback)")
        
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
        
        # CRITICAL FIX: Remove invalid ::: syntax in classDiagram
        # The ::: syntax is ONLY valid in flowcharts, NOT in classDiagrams
        # Pattern: "class ClassName:::styleDefName" should be "class ClassName styleDefName"
        if 'classDiagram' in mermaid or diagram_type.lower() == 'lld':
            lines = mermaid.split('\n')
            fixed_lines = []
            fixed_count = 0
            for line in lines:
                # Match: class ClassName:::styleDefName
                if re.match(r'^\s*class\s+\w+:::[\w]+\s*$', line):
                    # Remove the :::
                    fixed_line = re.sub(r'(\s*class\s+\w+):::([\w]+\s*)$', r'\1 \2', line)
                    fixed_lines.append(fixed_line)
                    fixed_count += 1
                else:
                    fixed_lines.append(line)
            
            if fixed_count > 0:
                logger.info(f"[agent3] 🔧 Fixed {fixed_count} invalid ::: style separators in classDiagram")
                mermaid = '\n'.join(fixed_lines)
        
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
                logger.info("[agent3] 🔧 Attempting advanced brace balancing fix...")
                
                # Advanced fix: Properly track entity blocks and balance braces
                lines = mermaid.split('\n')
                fixed_er = []
                entity_stack = []  # Track open entities
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    
                    # Check for entity start: ENTITY_NAME {
                    entity_start_match = re.match(r'^([A-Z_][A-Z_0-9]*)\s*\{$', stripped)
                    if entity_start_match:
                        entity_name = entity_start_match.group(1)
                        entity_stack.append((entity_name, i))
                        fixed_er.append(line)
                        continue
                    
                    # Check for closing brace
                    if stripped == '}':
                        if entity_stack:
                            entity_stack.pop()
                        fixed_er.append(line)
                        continue
                    
                    # Check for incomplete entity definition (name without brace on next line)
                    if re.match(r'^[A-Z_][A-Z_0-9]*$', stripped) and not entity_stack:
                        # Look ahead to see if next line has opening brace
                        if i + 1 < len(lines) and lines[i + 1].strip() == '{':
                            entity_stack.append((stripped, i))
                            fixed_er.append(stripped + ' {')
                            # Skip the next line (the opening brace)
                            continue
                    
                    # Regular line - add it
                    fixed_er.append(line)
                
                # Close any unclosed entities
                while entity_stack:
                    entity_name, line_num = entity_stack.pop()
                    logger.warning(f"[agent3] 🔧 Adding missing closing brace for entity '{entity_name}' (started at line {line_num+1})")
                    fixed_er.append('}')
                
                mermaid = '\n'.join(fixed_er)
                
                # Re-verify braces
                new_open = mermaid.count('{')
                new_close = mermaid.count('}')
                if new_open == new_close:
                    logger.info(f"[agent3] ✅ Brace balancing successful: {new_open} pairs")
                else:
                    logger.warning(f"[agent3] ⚠️ Braces still unbalanced after fix: {{ {new_open} vs }} {new_close}")
                    logger.info("[agent3] 🔧 Generating DBD fallback due to persistent brace issues")
                    mermaid = self._generate_dbd_fallback(features, project_title)
        
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

