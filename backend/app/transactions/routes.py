from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.deps import get_db
from app.accounts.models import Account
from app.transactions.models import Transaction
from app.transactions.schemas import TransactionCreate, TransactionResponse
from typing import List
import uuid

router = APIRouter()


@router.get("/{account_id}/transactions", response_model=List[TransactionResponse], status_code=status.HTTP_200_OK)
async def list_account_transactions(
    account_id: str,
    db: AsyncSession = Depends(get_db),
) -> List[TransactionResponse]:
    """
    Get all transactions for a specific account.
    
    Args:
        account_id: The account ID.
        db: Database session.
        
    Returns:
        List of transactions for the account.
        
    Raises:
        HTTPException: If account not found.
    """
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found",
        )
    
    txn_result = await db.execute(
        select(Transaction).where(Transaction.account_id == account_id)
    )
    transactions = txn_result.scalars().all()
    
    return [TransactionResponse.model_validate(txn) for txn in transactions]


@router.post("/{account_id}/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    account_id: str,
    transaction_create: TransactionCreate,
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    """
    Create a new transaction for an account.
    
    Args:
        account_id: The account ID.
        transaction_create: Transaction creation data.
        db: Database session.
        
    Returns:
        The created transaction.
        
    Raises:
        HTTPException: If account not found.
    """
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found",
        )
    
    transaction = Transaction(
        id=str(uuid.uuid4()),
        account_id=account_id,
        amount=transaction_create.amount,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return TransactionResponse.model_validate(transaction)


@router.get("/{account_id}/transactions/{transaction_id}", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
async def get_transaction(
    account_id: str,
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    """
    Get a specific transaction.
    
    Args:
        account_id: The account ID.
        transaction_id: The transaction ID.
        db: Database session.
        
    Returns:
        The requested transaction.
        
    Raises:
        HTTPException: If account or transaction not found.
    """
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found",
        )
    
    txn_result = await db.execute(
        select(Transaction).where(
            (Transaction.id == transaction_id) & (Transaction.account_id == account_id)
        )
    )
    transaction = txn_result.scalar_one_or_none()
    
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )
    
    return TransactionResponse.model_validate(transaction)

