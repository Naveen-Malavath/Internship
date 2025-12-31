from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import jwt
import hashlib
import uuid
from enum import Enum

app = FastAPI(title="Digital Banking Suite", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-change-in-production"

# Data Storage
users_db = {}
accounts_db = {}
transactions_db = {}
transfers_db = {}

# Models
class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
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

class UserRegister(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    created_at: datetime

class Account(BaseModel):
    id: str
    user_id: str
    account_type: AccountType
    account_number: str
    balance: Decimal
    currency: str = "USD"
    created_at: datetime
    is_active: bool = True

class AccountCreate(BaseModel):
    account_type: AccountType
    initial_deposit: Optional[Decimal] = Decimal("0.00")

class Transaction(BaseModel):
    id: str
    account_id: str
    transaction_type: TransactionType
    amount: Decimal
    description: str
    status: TransactionStatus
    created_at: datetime
    reference_id: Optional[str] = None

class TransactionCreate(BaseModel):
    account_id: str
    transaction_type: TransactionType
    amount: Decimal
    description: str

class Transfer(BaseModel):
    id: str
    from_account_id: str
    to_account_id: str
    amount: Decimal
    description: Optional[str] = None
    status: TransactionStatus
    created_at: datetime

class TransferCreate(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: Decimal
    description: Optional[str] = None

class PaymentCreate(BaseModel):
    account_id: str
    amount: Decimal
    recipient: str
    description: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime

# Utility Functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    user_id = decode_token(credentials.credentials)
    if user_id not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    return users_db[user_id]

def generate_account_number() -> str:
    return f"ACC{uuid.uuid4().hex[:10].upper()}"

# Authentication Endpoints
@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    if any(u.email == user_data.email for u in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        created_at=datetime.utcnow()
    )
    
    users_db[user_id] = {
        **user.dict(),
        "password": hash_password(user_data.password)
    }
    
    token = create_access_token(user_id)
    return TokenResponse(access_token=token)

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = next((u for u in users_db.values() if u["email"] == credentials.email), None)
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user["id"])
    return TokenResponse(access_token=token)

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return User(**{k: v for k, v in current_user.items() if k != "password"})

# Account Management Endpoints
@app.get("/api/accounts", response_model=List[Account])
async def get_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [
        Account(**account) for account in accounts_db.values() 
        if account["user_id"] == current_user["id"]
    ]
    return user_accounts

@app.post("/api/accounts", response_model=Account)
async def create_account(
    account_data: AccountCreate,
    current_user: dict = Depends(get_current_user)
):
    account_id = str(uuid.uuid4())
    account = Account(
        id=account_id,
        user_id=current_user["id"],
        account_type=account_data.account_type,
        account_number=generate_account_number(),
        balance=account_data.initial_deposit,
        created_at=datetime.utcnow()
    )
    
    accounts_db[account_id] = account.dict()
    
    if account_data.initial_deposit > 0:
        transaction_id = str(uuid.uuid4())
        transaction = Transaction(
            id=transaction_id,
            account_id=account_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=account_data.initial_deposit,
            description="Initial deposit",
            status=TransactionStatus.COMPLETED,
            created_at=datetime.utcnow()
        )
        transactions_db[transaction_id] = transaction.dict()
    
    return account

@app.get("/api/accounts/{account_id}", response_model=Account)
async def get_account(account_id: str, current_user: dict = Depends(get_current_user)):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts_db[account_id]
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Account(**account)

# Transaction Endpoints
@app.get("/api/accounts/{account_id}/transactions", response_model=List[Transaction])
async def get_transactions(account_id: str, current_user: dict = Depends(get_current_user)):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts_db[account_id]
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account_transactions = [
        Transaction(**tx) for tx in transactions_db.values()
        if tx["account_id"] == account_id
    ]
    return sorted(account_transactions, key=lambda x: x.created_at, reverse=True)

@app.post("/api/transactions", response_model=Transaction)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: dict = Depends(get_current_user)
):
    if transaction_data.account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts_db[transaction_data.account_id]
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if transaction_data.transaction_type == TransactionType.WITHDRAWAL:
        if account["balance"] < transaction_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        account["balance"] -= transaction_data.amount
    elif transaction_data.transaction_type == TransactionType.DEPOSIT:
        account["balance"] += transaction_data.amount
    
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        id=transaction_id,
        account_id=transaction_data.account_id,
        transaction_type=transaction_data.transaction_type,
        amount=transaction_data.amount,
        description=transaction_data.description,
        status=TransactionStatus.COMPLETED,
        created_at=datetime.utcnow()
    )
    
    transactions_db[transaction_id] = transaction.dict()
    accounts_db[transaction_data.account_id] = account
    
    return transaction

# Transfer Endpoints
@app.post("/api/transfers", response_model=Transfer)
async def create_transfer(
    transfer_data: TransferCreate,
    current_user: dict = Depends(get_current_user)
):
    if transfer_data.from_account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Source account not found")
    if transfer_data.to_account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Destination account not found")
    
    from_account = accounts_db[transfer_data.from_account_id]
    to_account = accounts_db[transfer_data.to_account_id]
    
    if from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if from_account["balance"] < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Process transfer
    from_account["balance"] -= transfer_data.amount
    to_account["balance"] += transfer_data.amount
    
    transfer_id = str(uuid.uuid4())
    transfer = Transfer(
        id=transfer_id,
        from_account_id=transfer_data.from_account_id,
        to_account_id=transfer_data.to_account_id,
        amount=transfer_data.amount,
        description=transfer_data.description,
        status=TransactionStatus.COMPLETED,
        created_at=datetime.utcnow()
    )
    
    transfers_db[transfer_id] = transfer.dict()
    accounts_db[transfer_data.from_account_id] = from_account
    accounts_db[transfer_data.to_account_id] = to_account
    
    # Create transaction records
    for account_id, tx_type, description in [
        (transfer_data.from_account_id, TransactionType.TRANSFER, f"Transfer to {to_account['account_number']}"),
        (transfer_data.to_account_id, TransactionType.TRANSFER, f"Transfer from {from_account['account_number']}")
    ]:
        tx_id = str(uuid.uuid4())
        transaction = Transaction(
            id=tx_id,
            account_id=account_id,
            transaction_type=tx_type,
            amount=transfer_data.amount,
            description=description,
            status=TransactionStatus.COMPLETED,
            created_at=datetime.utcnow(),
            reference_id=transfer_id
        )
        transactions_db[tx_id] = transaction.dict()
    
    return transfer

# Payment Endpoints
@app.post("/api/payments", response_model=Transaction)
async def process_payment(
    payment_data: PaymentCreate,
    current_user: dict = Depends(get_current_user)
):
    if payment_data.account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts_db[payment_data.account_id]
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if account["balance"] < payment_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    account["balance"] -= payment_data.amount
    
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        id=transaction_id,
        account_id=payment_data.account_id,
        transaction_type=TransactionType.PAYMENT,
        amount=payment_data.amount,
        description=f"Payment to {payment_data.recipient}: {payment_data.description or 'Payment'}",
        status=TransactionStatus.COMPLETED,
        created_at=datetime.utcnow()
    )
    
    transactions_db[transaction_id] = transaction.dict()
    accounts_db[payment_data.account_id] = account
    
    return transaction

# Health Check
@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)