"""Pydantic model for Diagram documents."""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class DiagramModel(BaseModel):
    """Represents a generated Mermaid diagram."""

    id: str | None = None
    project_id: str
    diagram_type: str
    mermaid_source: str
    created_at: datetime
    style_config: Optional[Dict] = None  # Mermaid style configuration

