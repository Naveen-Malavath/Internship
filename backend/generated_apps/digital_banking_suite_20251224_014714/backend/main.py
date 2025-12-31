from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import jwt
import hashlib
import uuid
from decimal import Decimal

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
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# In-memory storage
users_db = {}
accounts_db = {}
transactions_db = {}
sessions_db = {}

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

# Request/Response Models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: str
    address: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class CreateAccount(BaseModel):
    account_type: AccountType
    initial_balance: Decimal = Decimal("0.00")

class TransactionRequest(BaseModel):
    from_account_id: str
    to_account_id: Optional[str] = None
    amount: Decimal
    transaction_type: TransactionType
    description: Optional[str] = None

class User(BaseModel):
    user_id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    address: str
    created_at: datetime

class Account(BaseModel):
    account_id: str
    user_id: str
    account_type: AccountType
    account_number: str
    balance: Decimal
    created_at: datetime
    is_active: bool = True

class Transaction(BaseModel):
    transaction_id: str
    from_account_id: str
    to_account_id: Optional[str] = None
    amount: Decimal
    transaction_type: TransactionType
    status: TransactionStatus
    description: Optional[str] = None
    created_at: datetime

class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class AccountBalance(BaseModel):
    account_id: str
    account_number: str
    account_type: AccountType
    balance: Decimal

class TransactionHistory(BaseModel):
    transactions: List[Transaction]
    total_count: int

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
    return f"ACC{uuid.uuid4().hex[:12].upper()}"

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        
        return users_db[user_id]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/auth/register", response_model=User)
async def register_user(user_data: UserRegistration):
    if any(user["email"] == user_data.email for user in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    user = {
        "user_id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "address": user_data.address,
        "created_at": datetime.utcnow()
    }
    
    users_db[user_id] = user
    
    return User(**{k: v for k, v in user.items() if k != "password"})

@app.post("/auth/login", response_model=AuthToken)
async def login_user(credentials: UserLogin):
    user = next((u for u in users_db.values() if u["email"] == credentials.email), None)
    
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["user_id"]})
    sessions_db[user["user_id"]] = {
        "token": access_token,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=1)
    }
    
    return AuthToken(access_token=access_token)

@app.post("/accounts", response_model=Account)
async def create_account(account_data: CreateAccount, current_user: dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    account_number = generate_account_number()
    
    account = {
        "account_id": account_id,
        "user_id": current_user["user_id"],
        "account_type": account_data.account_type,
        "account_number": account_number,
        "balance": account_data.initial_balance,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    accounts_db[account_id] = account
    return Account(**account)

@app.get("/accounts", response_model=List[Account])
async def get_user_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [
        Account(**account) for account in accounts_db.values() 
        if account["user_id"] == current_user["user_id"] and account["is_active"]
    ]
    return user_accounts

@app.get("/accounts/{account_id}/balance", response_model=AccountBalance)
async def get_account_balance(account_id: str, current_user: dict = Depends(get_current_user)):
    account = accounts_db.get(account_id)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return AccountBalance(
        account_id=account["account_id"],
        account_number=account["account_number"],
        account_type=account["account_type"],
        balance=account["balance"]
    )

@app.post("/transactions", response_model=Transaction)
async def create_transaction(transaction_data: TransactionRequest, current_user: dict = Depends(get_current_user)):
    from_account = accounts_db.get(transaction_data.from_account_id)
    
    if not from_account or from_account["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=404, detail="From account not found or access denied")
    
    if transaction_data.transaction_type == TransactionType.TRANSFER:
        if not transaction_data.to_account_id:
            raise HTTPException(status_code=400, detail="To account required for transfer")
        
        to_account = accounts_db.get(transaction_data.to_account_id)
        if not to_account:
            raise HTTPException(status_code=404, detail="To account not found")
    
    if transaction_data.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER, TransactionType.PAYMENT]:
        if from_account["balance"] < transaction_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
    
    transaction_id = str(uuid.uuid4())
    
    transaction = {
        "transaction_id": transaction_id,
        "from_account_id": transaction_data.from_account_id,
        "to_account_id": transaction_data.to_account_id,
        "amount": transaction_data.amount,
        "transaction_type": transaction_data.transaction_type,
        "status": TransactionStatus.COMPLETED,
        "description": transaction_data.description,
        "created_at": datetime.utcnow()
    }
    
    # Update balances
    if transaction_data.transaction_type == TransactionType.DEPOSIT:
        accounts_db[transaction_data.from_account_id]["balance"] += transaction_data.amount
    elif transaction_data.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.PAYMENT]:
        accounts_db[transaction_data.from_account_id]["balance"] -= transaction_data.amount
    elif transaction_data.transaction_type == TransactionType.TRANSFER:
        accounts_db[transaction_data.from_account_id]["balance"] -= transaction_data.amount
        accounts_db[transaction_data.to_account_id]["balance"] += transaction_data.amount
    
    transactions_db[transaction_id] = transaction
    return Transaction(**transaction)

@app.get("/accounts/{account_id}/transactions", response_model=TransactionHistory)
async def get_transaction_history(
    account_id: str, 
    limit: int = 50, 
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    account = accounts_db.get(account_id)
    
    if not account or account["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=404, detail="Account not found or access denied")
    
    account_transactions = [
        Transaction(**txn) for txn in transactions_db.values()
        if txn["from_account_id"] == account_id or txn.get("to_account_id") == account_id
    ]
    
    account_transactions.sort(key=lambda x: x.created_at, reverse=True)
    
    total_count = len(account_transactions)
    paginated_transactions = account_transactions[offset:offset + limit]
    
    return TransactionHistory(
        transactions=paginated_transactions,
        total_count=total_count
    )

@app.get("/user/profile", response_model=User)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    return User(**{k: v for k, v in current_user.items() if k != "password"})