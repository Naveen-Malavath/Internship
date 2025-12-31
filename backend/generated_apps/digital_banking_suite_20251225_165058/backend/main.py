from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import uuid

app = FastAPI(
    title="Digital Banking Suite",
    description="Secure, personalised banking experience with account management, payments, and analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AccountType(str, Enum):
    SAVINGS = "savings"
    CHECKING = "checking"
    CREDIT = "credit"

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class AccountCreate(BaseModel):
    account_type: AccountType
    initial_balance: Decimal = Field(ge=0, decimal_places=2)
    account_name: str = Field(min_length=1, max_length=100)

class AccountResponse(BaseModel):
    account_id: str
    user_id: str
    account_type: AccountType
    balance: Decimal
    account_name: str
    created_at: datetime
    is_active: bool

class AccountUpdate(BaseModel):
    account_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None

class UserCreate(BaseModel):
    email: str = Field(regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    full_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=10, max_length=15)
    date_of_birth: date

class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    phone: str
    date_of_birth: date
    created_at: datetime
    is_active: bool

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    is_active: Optional[bool] = None

class TransactionCreate(BaseModel):
    from_account_id: str
    to_account_id: Optional[str] = None
    transaction_type: TransactionType
    amount: Decimal = Field(gt=0, decimal_places=2)
    description: Optional[str] = Field(None, max_length=200)

class TransactionResponse(BaseModel):
    transaction_id: str
    from_account_id: str
    to_account_id: Optional[str]
    transaction_type: TransactionType
    amount: Decimal
    description: Optional[str]
    status: TransactionStatus
    created_at: datetime

class PaymentCreate(BaseModel):
    from_account_id: str
    recipient_name: str = Field(min_length=1, max_length=100)
    recipient_account: str = Field(min_length=1, max_length=50)
    amount: Decimal = Field(gt=0, decimal_places=2)
    reference: Optional[str] = Field(None, max_length=100)

class PaymentResponse(BaseModel):
    payment_id: str
    from_account_id: str
    recipient_name: str
    recipient_account: str
    amount: Decimal
    reference: Optional[str]
    status: TransactionStatus
    created_at: datetime

class AnalyticsResponse(BaseModel):
    total_accounts: int
    total_users: int
    total_balance: Decimal
    total_transactions: int
    transactions_by_type: Dict[str, int]
    monthly_transaction_volume: Decimal

# In-memory storage
users_db: Dict[str, dict] = {}
accounts_db: Dict[str, dict] = {}
transactions_db: Dict[str, dict] = {}
payments_db: Dict[str, dict] = {}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    user_id = str(uuid.uuid4())
    user_data = {
        "user_id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "date_of_birth": user.date_of_birth,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    # Check if email already exists
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    users_db[user_id] = user_data
    return UserResponse(**user_data)

@app.get("/users", response_model=List[UserResponse])
async def get_users():
    return [UserResponse(**user) for user in users_db.values()]

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(**users_db[user_id])

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_data = users_db[user_id]
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        user_data[field] = value
    
    return UserResponse(**user_data)

@app.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(account: AccountCreate, user_id: str):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    account_id = str(uuid.uuid4())
    account_data = {
        "account_id": account_id,
        "user_id": user_id,
        "account_type": account.account_type,
        "balance": account.initial_balance,
        "account_name": account.account_name,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    accounts_db[account_id] = account_data
    return AccountResponse(**account_data)

@app.get("/accounts", response_model=List[AccountResponse])
async def get_accounts(user_id: Optional[str] = None):
    if user_id:
        user_accounts = [acc for acc in accounts_db.values() if acc["user_id"] == user_id]
        return [AccountResponse(**account) for account in user_accounts]
    return [AccountResponse(**account) for account in accounts_db.values()]

@app.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str):
    if account_id not in accounts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return AccountResponse(**accounts_db[account_id])

@app.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(account_id: str, account_update: AccountUpdate):
    if account_id not in accounts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    account_data = accounts_db[account_id]
    update_data = account_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        account_data[field] = value
    
    return AccountResponse(**account_data)

@app.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction: TransactionCreate):
    if transaction.from_account_id not in accounts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="From account not found"
        )
    
    from_account = accounts_db[transaction.from_account_id]
    
    if transaction.to_account_id and transaction.to_account_id not in accounts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="To account not found"
        )
    
    # Check sufficient balance for withdrawals and transfers
    if transaction.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER]:
        if from_account["balance"] < transaction.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
    
    transaction_id = str(uuid.uuid4())
    transaction_data = {
        "transaction_id": transaction_id,
        "from_account_id": transaction.from_account_id,
        "to_account_id": transaction.to_account_id,
        "transaction_type": transaction.transaction_type,
        "amount": transaction.amount,
        "description": transaction.description,
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow()
    }
    
    # Update account balances
    if transaction.transaction_type == TransactionType.DEPOSIT:
        from_account["balance"] += transaction.amount
    elif transaction.transaction_type == TransactionType.WITHDRAWAL:
        from_account["balance"] -= transaction.amount
    elif transaction.transaction_type == TransactionType.TRANSFER:
        from_account["balance"] -= transaction.amount
        to_account = accounts_db[transaction.to_account_id]
        to_account["balance"] += transaction.amount
    
    transactions_db[transaction_id] = transaction_data
    return TransactionResponse(**transaction_data)

@app.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(account_id: Optional[str] = None):
    if account_id:
        account_transactions = [
            txn for txn in transactions_db.values() 
            if txn["from_account_id"] == account_id or txn["to_account_id"] == account_id
        ]
        return [TransactionResponse(**transaction) for transaction in account_transactions]
    return [TransactionResponse(**transaction) for transaction in transactions_db.values()]

@app.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payment: PaymentCreate):
    if payment.from_account_id not in accounts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    from_account = accounts_db[payment.from_account_id]
    
    if from_account["balance"] < payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    payment_id = str(uuid.uuid4())
    payment_data = {
        "payment_id": payment_id,
        "from_account_id": payment.from_account_id,
        "recipient_name": payment.recipient_name,
        "recipient_account": payment.recipient_account,
        "amount": payment.amount,
        "reference": payment.reference,
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow()
    }
    
    # Update account balance
    from_account["balance"] -= payment.amount
    
    payments_db[payment_id] = payment_data
    return PaymentResponse(**payment_data)

@app.get("/payments", response_model=List[PaymentResponse])
async def get_payments(account_id: Optional[str] = None):
    if account_id:
        account_payments = [
            payment for payment in payments_db.values() 
            if payment["from_account_id"] == account_id
        ]
        return [PaymentResponse(**payment) for payment in account_payments]
    return [PaymentResponse(**payment) for payment in payments_db.values()]

@app.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    total_balance = sum(Decimal(str(account["balance"])) for account in accounts_db.values())
    
    transactions_by_type = {}
    monthly_volume = Decimal('0')
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    for transaction in transactions_db.values():
        txn_type = transaction["transaction_type"]
        transactions_by_type[txn_type] = transactions_by_type.get(txn_type, 0) + 1
        
        if transaction["created_at"] >= current_month:
            monthly_volume += transaction["amount"]
    
    for payment in payments_db.values():
        if payment["created_at"] >= current_month:
            monthly_volume += payment["amount"]
    
    return AnalyticsResponse(
        total_accounts=len(accounts_db),
        total_users=len(users_db),
        total_balance=total_balance,
        total_transactions=len(transactions_db) + len(payments_db),
        transactions_by_type=transactions_by_type,
        monthly_transaction_volume=monthly_volume
    )