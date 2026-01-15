from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import jwt
import hashlib
from enum import Enum

app = FastAPI(title="Digital Banking Suite", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# Enums
class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"

# Models
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
    is_active: bool = True

class Account(BaseModel):
    id: str
    user_id: str
    account_number: str
    account_type: AccountType
    balance: Decimal
    currency: str = "USD"
    created_at: datetime
    is_active: bool = True

class Transaction(BaseModel):
    id: str
    account_id: str
    type: TransactionType
    amount: Decimal
    description: str
    status: TransactionStatus
    created_at: datetime
    from_account: Optional[str] = None
    to_account: Optional[str] = None

class TransactionCreate(BaseModel):
    account_id: str
    type: TransactionType
    amount: Decimal
    description: str
    to_account: Optional[str] = None

class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: Decimal
    description: str

class PaymentRequest(BaseModel):
    account_id: str
    amount: Decimal
    recipient: str
    description: str

class AnalyticsResponse(BaseModel):
    total_balance: Decimal
    total_transactions: int
    monthly_spending: Decimal
    account_summary: List[Dict[str, Any]]
    recent_transactions: List[Transaction]

# In-memory storage
users: Dict[str, Dict] = {}
accounts: Dict[str, Dict] = {}
transactions: Dict[str, Dict] = {}
user_sessions: Dict[str, str] = {}

# Utility functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None or user_id not in users:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_account_number() -> str:
    return f"ACC{str(uuid.uuid4().int)[:10]}"

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Authentication endpoints
@app.post("/api/auth/register", status_code=201)
async def register(user_data: UserRegister):
    if any(u["email"] == user_data.email for u in users.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    user = {
        "id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    users[user_id] = user
    
    # Create default checking account
    account_id = str(uuid.uuid4())
    account = {
        "id": account_id,
        "user_id": user_id,
        "account_number": generate_account_number(),
        "account_type": AccountType.CHECKING,
        "balance": Decimal("1000.00"),
        "currency": "USD",
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    accounts[account_id] = account
    
    token = create_access_token(user_id)
    
    return {
        "message": "User registered successfully",
        "user": User(**{k: v for k, v in user.items() if k != "password"}),
        "token": token
    }

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    user = next((u for u in users.values() if u["email"] == credentials.email), None)
    
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user["is_active"]:
        raise HTTPException(status_code=401, detail="Account deactivated")
    
    token = create_access_token(user["id"])
    user_sessions[user["id"]] = token
    
    return {
        "message": "Login successful",
        "token": token,
        "user": User(**{k: v for k, v in user.items() if k != "password"})
    }

@app.post("/api/auth/logout")
async def logout(current_user: str = Depends(get_current_user)):
    user_sessions.pop(current_user, None)
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    user = users[current_user]
    return User(**{k: v for k, v in user.items() if k != "password"})

# Account endpoints
@app.get("/api/accounts", response_model=List[Account])
async def get_accounts(current_user: str = Depends(get_current_user)):
    user_accounts = [
        Account(**account) for account in accounts.values() 
        if account["user_id"] == current_user and account["is_active"]
    ]
    return user_accounts

@app.get("/api/accounts/{account_id}", response_model=Account)
async def get_account(account_id: str, current_user: str = Depends(get_current_user)):
    account = accounts.get(account_id)
    if not account or account["user_id"] != current_user:
        raise HTTPException(status_code=404, detail="Account not found")
    return Account(**account)

# Transaction endpoints
@app.get("/api/transactions", response_model=List[Transaction])
async def get_transactions(account_id: Optional[str] = None, current_user: str = Depends(get_current_user)):
    user_account_ids = [
        acc_id for acc_id, acc in accounts.items() 
        if acc["user_id"] == current_user
    ]
    
    filtered_transactions = []
    for transaction in transactions.values():
        if account_id and transaction["account_id"] != account_id:
            continue
        if transaction["account_id"] in user_account_ids:
            filtered_transactions.append(Transaction(**transaction))
    
    return sorted(filtered_transactions, key=lambda x: x.created_at, reverse=True)

@app.post("/api/transactions", response_model=Transaction, status_code=201)
async def create_transaction(transaction_data: TransactionCreate, current_user: str = Depends(get_current_user)):
    account = accounts.get(transaction_data.account_id)
    if not account or account["user_id"] != current_user:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if transaction_data.type == TransactionType.WITHDRAWAL and account["balance"] < transaction_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "account_id": transaction_data.account_id,
        "type": transaction_data.type,
        "amount": transaction_data.amount,
        "description": transaction_data.description,
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "from_account": None,
        "to_account": transaction_data.to_account
    }
    
    # Update account balance
    if transaction_data.type == TransactionType.DEPOSIT:
        accounts[transaction_data.account_id]["balance"] += transaction_data.amount
    elif transaction_data.type == TransactionType.WITHDRAWAL:
        accounts[transaction_data.account_id]["balance"] -= transaction_data.amount
    
    transactions[transaction_id] = transaction
    return Transaction(**transaction)

# Transfer endpoint
@app.post("/api/transfers", response_model=Transaction, status_code=201)
async def create_transfer(transfer_data: TransferRequest, current_user: str = Depends(get_current_user)):
    from_account = accounts.get(transfer_data.from_account)
    to_account = accounts.get(transfer_data.to_account)
    
    if not from_account or from_account["user_id"] != current_user:
        raise HTTPException(status_code=404, detail="Source account not found")
    
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    
    if from_account["balance"] < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "account_id": transfer_data.from_account,
        "type": TransactionType.TRANSFER,
        "amount": transfer_data.amount,
        "description": transfer_data.description,
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "from_account": transfer_data.from_account,
        "to_account": transfer_data.to_account
    }
    
    # Update balances
    accounts[transfer_data.from_account]["balance"] -= transfer_data.amount
    accounts[transfer_data.to_account]["balance"] += transfer_data.amount
    
    transactions[transaction_id] = transaction
    return Transaction(**transaction)

# Payment endpoint
@app.post("/api/payments", response_model=Transaction, status_code=201)
async def create_payment(payment_data: PaymentRequest, current_user: str = Depends(get_current_user)):
    account = accounts.get(payment_data.account_id)
    if not account or account["user_id"] != current_user:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["balance"] < payment_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "account_id": payment_data.account_id,
        "type": TransactionType.PAYMENT,
        "amount": payment_data.amount,
        "description": f"Payment to {payment_data.recipient}: {payment_data.description}",
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "from_account": payment_data.account_id,
        "to_account": None
    }
    
    # Update account balance
    accounts[payment_data.account_id]["balance"] -= payment_data.amount
    
    transactions[transaction_id] = transaction
    return Transaction(**transaction)

# Analytics endpoint
@app.get("/api/analytics", response_model=AnalyticsResponse)
async def get_analytics(current_user: str = Depends(get_current_user)):
    user_account_ids = [
        acc_id for acc_id, acc in accounts.items() 
        if acc["user_id"] == current_user
    ]
    
    user_accounts = [accounts[acc_id] for acc_id in user_account_ids]
    user_transactions = [
        Transaction(**trans) for trans in transactions.values()
        if trans["account_id"] in user_account_ids
    ]
    
    total_balance = sum(acc["balance"] for acc in user_accounts)
    
    # Calculate monthly spending (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_spending = sum(
        trans.amount for trans in user_transactions
        if trans.created_at >= thirty_days_ago and 
        trans.type in [TransactionType.WITHDRAWAL, TransactionType.PAYMENT, TransactionType.TRANSFER]
    )
    
    account_summary = [
        {
            "account_id": acc["id"],
            "account_type": acc["account_type"],
            "balance": acc["balance"],
            "account_number": acc["account_number"]
        }
        for acc in user_accounts
    ]
    
    recent_transactions = sorted(user_transactions, key=lambda x: x.created_at, reverse=True)[:10]
    
    return AnalyticsResponse(
        total_balance=total_balance,
        total_transactions=len(user_transactions),
        monthly_spending=monthly_spending,
        account_summary=account_summary,
        recent_transactions=recent_transactions
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)