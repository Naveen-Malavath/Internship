from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    """SQLAlchemy declarative base with common columns."""

    def get_id(self) -> str:
        """Get the primary key value."""
        return getattr(self, "id", None)


class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

