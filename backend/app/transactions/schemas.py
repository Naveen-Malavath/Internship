from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional


class TransactionBase(BaseModel):
    """Base transaction schema."""

    account_id: str = Field(..., min_length=1, description="Account ID")
    amount: Decimal = Field(..., description="Transaction amount")


class TransactionCreate(TransactionBase):
    """Transaction creation schema."""

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "account_id": "acc-123",
            "amount": "100.50"
        }
    })


class TransactionResponse(TransactionBase):
    """Transaction response schema."""

    id: str = Field(..., description="Transaction ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "txn-123",
                "account_id": "acc-123",
                "amount": "100.50",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    )

