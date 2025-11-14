"""Pydantic model for Feature documents."""

from datetime import datetime

from pydantic import BaseModel


class FeatureModel(BaseModel):
    """Represents a generated feature."""

    id: str | None = None
    project_id: str
    feature_text: str
    order_index: int
    created_at: datetime

