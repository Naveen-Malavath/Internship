"""Pydantic model for Story documents."""

from datetime import datetime
from typing import List

from pydantic import BaseModel


class StoryModel(BaseModel):
    """Represents a generated user story."""

    id: str | None = None
    feature_id: str
    story_text: str
    acceptance_criteria: List[str]
    created_at: datetime

