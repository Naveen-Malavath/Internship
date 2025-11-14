"""Pydantic model for Diagram documents."""

from datetime import datetime

from pydantic import BaseModel


class DiagramModel(BaseModel):
    """Represents a generated Mermaid diagram."""

    id: str | None = None
    project_id: str
    diagram_type: str
    mermaid_source: str
    created_at: datetime

