from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
import uuid
from datetime import datetime
from app.db.base import Base, TimestampMixin


class Transaction(Base, TimestampMixin):
    """Transaction model."""

    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("accounts.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="transactions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, account_id={self.account_id}, amount={self.amount})>"

