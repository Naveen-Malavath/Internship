from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import hashlib
import uuid
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
SECRET_KEY = "banking_secret_key_2024"
ALGORITHM = "HS256"

# In-memory storage
users_db = {}
accounts_db = {}
transactions_db = {}
sessions_db = {}

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
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: str
    created_at: datetime
    is_active: bool

class AccountCreate(BaseModel):
    account_type: AccountType
    initial_balance: float = 0.0

class Account(BaseModel):
    id: str
    user_id: str
    account_type: AccountType
    account_number: str
    balance: float
    created_at: datetime
    is_active: bool

class TransactionCreate(BaseModel):
    from_account_id: str
    to_account_id: Optional[str] = None
    amount: float
    transaction_type: TransactionType
    description: Optional[str] = None

class Transaction(BaseModel):
    id: str
    from_account_id: str
    to_account_id: Optional[str] = None
    amount: float
    transaction_type: TransactionType
    status: TransactionStatus
    description: Optional[str] = None
    created_at: datetime

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class BalanceResponse(BaseModel):
    account_id: str
    balance: float
    account_type: str

# Utility functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def generate_account_number() -> str:
    return f"ACC{uuid.uuid4().hex[:8].upper()}"

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        
        return users_db[user_id]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/auth/register", response_model=AuthResponse)
async def register(user_data: UserCreate):
    if any(u["email"] == user_data.email for u in users_db.values()):
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
    
    users_db[user_id] = user
    
    access_token = create_access_token(data={"sub": user_id})
    
    user_response = User(**{k: v for k, v in user.items() if k != "password"})
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@app.post("/auth/login", response_model=AuthResponse)
async def login(login_data: UserLogin):
    user = next((u for u in users_db.values() if u["email"] == login_data.email), None)
    
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["id"]})
    
    user_response = User(**{k: v for k, v in user.items() if k != "password"})
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@app.post("/accounts", response_model=Account)
async def create_account(account_data: AccountCreate, current_user: dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    account_number = generate_account_number()
    
    account = {
        "id": account_id,
        "user_id": current_user["id"],
        "account_type": account_data.account_type.value,
        "account_number": account_number,
        "balance": account_data.initial_balance,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    accounts_db[account_id] = account
    
    return Account(**account)

@app.get("/accounts", response_model=List[Account])
async def get_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [
        Account(**account) for account in accounts_db.values()
        if account["user_id"] == current_user["id"]
    ]
    return user_accounts

@app.get("/accounts/{account_id}/balance", response_model=BalanceResponse)
async def get_account_balance(account_id: str, current_user: dict = Depends(get_current_user)):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts_db[account_id]
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return BalanceResponse(
        account_id=account_id,
        balance=account["balance"],
        account_type=account["account_type"]
    )

@app.post("/transactions", response_model=Transaction)
async def create_transaction(transaction_data: TransactionCreate, current_user: dict = Depends(get_current_user)):
    # Validate from account
    if transaction_data.from_account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="From account not found")
    
    from_account = accounts_db[transaction_data.from_account_id]
    
    if from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied to from account")
    
    # Validate to account if transfer
    if transaction_data.transaction_type == TransactionType.TRANSFER:
        if not transaction_data.to_account_id or transaction_data.to_account_id not in accounts_db:
            raise HTTPException(status_code=404, detail="To account not found")
    
    # Check sufficient balance for withdrawals and transfers
    if transaction_data.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER, TransactionType.PAYMENT]:
        if from_account["balance"] < transaction_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Create transaction
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "from_account_id": transaction_data.from_account_id,
        "to_account_id": transaction_data.to_account_id,
        "amount": transaction_data.amount,
        "transaction_type": transaction_data.transaction_type.value,
        "status": TransactionStatus.PENDING.value,
        "description": transaction_data.description,
        "created_at": datetime.utcnow()
    }
    
    # Process transaction
    try:
        if transaction_data.transaction_type == TransactionType.DEPOSIT:
            accounts_db[transaction_data.from_account_id]["balance"] += transaction_data.amount
        elif transaction_data.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.PAYMENT]:
            accounts_db[transaction_data.from_account_id]["balance"] -= transaction_data.amount
        elif transaction_data.transaction_type == TransactionType.TRANSFER:
            accounts_db[transaction_data.from_account_id]["balance"] -= transaction_data.amount
            accounts_db[transaction_data.to_account_id]["balance"] += transaction_data.amount
        
        transaction["status"] = TransactionStatus.COMPLETED.value
        
    except Exception:
        transaction["status"] = TransactionStatus.FAILED.value
    
    transactions_db[transaction_id] = transaction
    
    return Transaction(**transaction)

@app.get("/transactions", response_model=List[Transaction])
async def get_transactions(current_user: dict = Depends(get_current_user)):
    user_account_ids = [
        account["id"] for account in accounts_db.values()
        if account["user_id"] == current_user["id"]
    ]
    
    user_transactions = [
        Transaction(**transaction) for transaction in transactions_db.values()
        if transaction["from_account_id"] in user_account_ids or
           (transaction["to_account_id"] and transaction["to_account_id"] in user_account_ids)
    ]
    
    return sorted(user_transactions, key=lambda x: x.created_at, reverse=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)