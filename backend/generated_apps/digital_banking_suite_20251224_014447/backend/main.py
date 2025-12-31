from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
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
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# In-memory storage
users_db: Dict[str, Dict] = {}
accounts_db: Dict[str, Dict] = {}
transactions_db: Dict[str, Dict] = {}
sessions_db: Dict[str, Dict] = {}

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
class UserRegistration(BaseModel):
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

class Account(BaseModel):
    id: str
    user_id: str
    account_type: AccountType
    balance: Decimal
    account_number: str
    created_at: datetime

class Transaction(BaseModel):
    id: str
    from_account_id: Optional[str]
    to_account_id: Optional[str]
    amount: Decimal
    transaction_type: TransactionType
    status: TransactionStatus
    description: str
    created_at: datetime

class TransactionCreate(BaseModel):
    from_account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    amount: Decimal
    transaction_type: TransactionType
    description: str

class AccountCreate(BaseModel):
    account_type: AccountType
    initial_balance: Decimal = Decimal('0.00')

class PaymentRequest(BaseModel):
    from_account_id: str
    to_account_number: str
    amount: Decimal
    description: str

class AuthToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# Utility functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_account_number() -> str:
    return f"ACC{str(uuid.uuid4().int)[:10]}"

# Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/auth/register", response_model=User)
async def register(user_data: UserRegistration):
    if user_data.email in [u["email"] for u in users_db.values()]:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow()
    }
    users_db[user_id] = user
    
    # Create default checking account
    account_id = str(uuid.uuid4())
    account = {
        "id": account_id,
        "user_id": user_id,
        "account_type": AccountType.CHECKING,
        "balance": Decimal('0.00'),
        "account_number": generate_account_number(),
        "created_at": datetime.utcnow()
    }
    accounts_db[account_id] = account
    
    return User(**{k: v for k, v in user.items() if k != 'password_hash'})

@app.post("/auth/login", response_model=AuthToken)
async def login(user_data: UserLogin):
    user = None
    for u in users_db.values():
        if u["email"] == user_data.email:
            user = u
            break
    
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["id"]})
    sessions_db[user["id"]] = {"token": access_token, "created_at": datetime.utcnow()}
    
    return AuthToken(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600
    )

@app.get("/accounts", response_model=List[Account])
async def get_accounts(current_user: str = Depends(get_current_user)):
    user_accounts = [
        Account(**account) for account in accounts_db.values() 
        if account["user_id"] == current_user
    ]
    return user_accounts

@app.post("/accounts", response_model=Account)
async def create_account(
    account_data: AccountCreate,
    current_user: str = Depends(get_current_user)
):
    account_id = str(uuid.uuid4())
    account = {
        "id": account_id,
        "user_id": current_user,
        "account_type": account_data.account_type,
        "balance": account_data.initial_balance,
        "account_number": generate_account_number(),
        "created_at": datetime.utcnow()
    }
    accounts_db[account_id] = account
    return Account(**account)

@app.get("/accounts/{account_id}/transactions", response_model=List[Transaction])
async def get_account_transactions(
    account_id: str,
    current_user: str = Depends(get_current_user)
):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts_db[account_id]
    if account["user_id"] != current_user:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account_transactions = [
        Transaction(**txn) for txn in transactions_db.values()
        if txn["from_account_id"] == account_id or txn["to_account_id"] == account_id
    ]
    return sorted(account_transactions, key=lambda x: x.created_at, reverse=True)

@app.post("/transactions", response_model=Transaction)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: str = Depends(get_current_user)
):
    transaction_id = str(uuid.uuid4())
    
    # Validate accounts belong to user
    if transaction_data.from_account_id:
        from_account = accounts_db.get(transaction_data.from_account_id)
        if not from_account or from_account["user_id"] != current_user:
            raise HTTPException(status_code=403, detail="Invalid from account")
        
        # Check sufficient balance for withdrawals/transfers
        if transaction_data.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER]:
            if from_account["balance"] < transaction_data.amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")
    
    if transaction_data.to_account_id:
        to_account = accounts_db.get(transaction_data.to_account_id)
        if not to_account:
            raise HTTPException(status_code=404, detail="To account not found")
    
    # Create transaction
    transaction = {
        "id": transaction_id,
        "from_account_id": transaction_data.from_account_id,
        "to_account_id": transaction_data.to_account_id,
        "amount": transaction_data.amount,
        "transaction_type": transaction_data.transaction_type,
        "status": TransactionStatus.COMPLETED,
        "description": transaction_data.description,
        "created_at": datetime.utcnow()
    }
    
    # Update account balances
    if transaction_data.from_account_id:
        accounts_db[transaction_data.from_account_id]["balance"] -= transaction_data.amount
    
    if transaction_data.to_account_id:
        accounts_db[transaction_data.to_account_id]["balance"] += transaction_data.amount
    
    transactions_db[transaction_id] = transaction
    return Transaction(**transaction)

@app.post("/payments", response_model=Transaction)
async def make_payment(
    payment_data: PaymentRequest,
    current_user: str = Depends(get_current_user)
):
    # Validate from account
    from_account = accounts_db.get(payment_data.from_account_id)
    if not from_account or from_account["user_id"] != current_user:
        raise HTTPException(status_code=403, detail="Invalid from account")
    
    # Check sufficient balance
    if from_account["balance"] < payment_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Find to account by account number
    to_account = None
    for account in accounts_db.values():
        if account["account_number"] == payment_data.to_account_number:
            to_account = account
            break
    
    if not to_account:
        raise HTTPException(status_code=404, detail="Recipient account not found")
    
    # Create payment transaction
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "from_account_id": payment_data.from_account_id,
        "to_account_id": to_account["id"],
        "amount": payment_data.amount,
        "transaction_type": TransactionType.PAYMENT,
        "status": TransactionStatus.COMPLETED,
        "description": payment_data.description,
        "created_at": datetime.utcnow()
    }
    
    # Update balances
    accounts_db[payment_data.from_account_id]["balance"] -= payment_data.amount
    accounts_db[to_account["id"]]["balance"] += payment_data.amount
    
    transactions_db[transaction_id] = transaction
    return Transaction(**transaction)

@app.get("/dashboard")
async def get_dashboard(current_user: str = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db.values() if acc["user_id"] == current_user]
    total_balance = sum(acc["balance"] for acc in user_accounts)
    
    recent_transactions = []
    for txn in transactions_db.values():
        if any(acc["id"] in [txn.get("from_account_id"), txn.get("to_account_id")] 
               for acc in user_accounts):
            recent_transactions.append(txn)
    
    recent_transactions = sorted(recent_transactions, 
                               key=lambda x: x["created_at"], 
                               reverse=True)[:10]
    
    return {
        "total_balance": total_balance,
        "accounts_count": len(user_accounts),
        "recent_transactions": recent_transactions,
        "user": {k: v for k, v in users_db[current_user].items() if k != 'password_hash'}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)