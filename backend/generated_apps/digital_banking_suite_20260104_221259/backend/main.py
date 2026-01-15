from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
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

# Enums
class AccountType(str, Enum):
    SAVINGS = "savings"
    CHECKING = "checking"
    BUSINESS = "business"

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

# Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    created_at: datetime

class Account(BaseModel):
    id: str
    user_id: str
    account_number: str
    account_type: AccountType
    balance: Decimal
    created_at: datetime

class AccountCreate(BaseModel):
    account_type: AccountType

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
    from_account_id: Optional[str]
    to_account_id: Optional[str]
    amount: Decimal = Field(gt=0)
    transaction_type: TransactionType
    description: str

class Transfer(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: Decimal = Field(gt=0)
    description: str = "Transfer"

class Payment(BaseModel):
    account_id: str
    amount: Decimal = Field(gt=0)
    recipient: str
    description: str

class APIResponse(BaseModel):
    data: Any
    message: str
    status_code: int

# In-memory storage
users_db: Dict[str, Dict] = {}
accounts_db: Dict[str, Dict] = {}
transactions_db: Dict[str, Dict] = {}
user_sessions: Dict[str, str] = {}

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None or user_id not in users_db:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return users_db[user_id]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

def generate_account_number() -> str:
    return f"ACC{str(uuid.uuid4().hex[:12]).upper()}"

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Authentication endpoints
@app.post("/api/auth/register", response_model=APIResponse)
async def register(user_data: UserRegister):
    if any(u["email"] == user_data.email for u in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow()
    }
    users_db[user_id] = user
    
    # Create default savings account
    account_id = str(uuid.uuid4())
    account = {
        "id": account_id,
        "user_id": user_id,
        "account_number": generate_account_number(),
        "account_type": AccountType.SAVINGS,
        "balance": Decimal("0.00"),
        "created_at": datetime.utcnow()
    }
    accounts_db[account_id] = account
    
    user_response = User(**{k: v for k, v in user.items() if k != "password"})
    return APIResponse(data=user_response, message="User registered successfully", status_code=201)

@app.post("/api/auth/login", response_model=APIResponse)
async def login(login_data: UserLogin):
    user = next((u for u in users_db.values() if u["email"] == login_data.email), None)
    if not user or user["password"] != hash_password(login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["id"]})
    user_sessions[user["id"]] = access_token
    
    return APIResponse(
        data={"access_token": access_token, "token_type": "bearer"},
        message="Login successful",
        status_code=200
    )

@app.post("/api/auth/logout", response_model=APIResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    user_sessions.pop(current_user["id"], None)
    return APIResponse(data={}, message="Logout successful", status_code=200)

@app.get("/api/auth/me", response_model=APIResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    user_data = User(**{k: v for k, v in current_user.items() if k != "password"})
    return APIResponse(data=user_data, message="User info retrieved", status_code=200)

# Account endpoints
@app.get("/api/accounts", response_model=APIResponse)
async def get_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [Account(**acc) for acc in accounts_db.values() if acc["user_id"] == current_user["id"]]
    return APIResponse(data=user_accounts, message="Accounts retrieved", status_code=200)

@app.post("/api/accounts", response_model=APIResponse)
async def create_account(account_data: AccountCreate, current_user: dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    account = {
        "id": account_id,
        "user_id": current_user["id"],
        "account_number": generate_account_number(),
        "account_type": account_data.account_type,
        "balance": Decimal("0.00"),
        "created_at": datetime.utcnow()
    }
    accounts_db[account_id] = account
    
    account_response = Account(**account)
    return APIResponse(data=account_response, message="Account created successfully", status_code=201)

@app.get("/api/accounts/{account_id}", response_model=APIResponse)
async def get_account(account_id: str, current_user: dict = Depends(get_current_user)):
    account = accounts_db.get(account_id)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account_data = Account(**account)
    return APIResponse(data=account_data, message="Account retrieved", status_code=200)

# Transaction endpoints
@app.get("/api/transactions", response_model=APIResponse)
async def get_transactions(account_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    user_account_ids = [acc["id"] for acc in accounts_db.values() if acc["user_id"] == current_user["id"]]
    
    transactions = []
    for txn in transactions_db.values():
        if account_id:
            if txn.get("from_account_id") == account_id or txn.get("to_account_id") == account_id:
                transactions.append(Transaction(**txn))
        else:
            if (txn.get("from_account_id") in user_account_ids or 
                txn.get("to_account_id") in user_account_ids):
                transactions.append(Transaction(**txn))
    
    return APIResponse(data=transactions, message="Transactions retrieved", status_code=200)

@app.post("/api/transactions/deposit", response_model=APIResponse)
async def deposit_funds(transaction_data: TransactionCreate, current_user: dict = Depends(get_current_user)):
    if not transaction_data.to_account_id:
        raise HTTPException(status_code=400, detail="To account ID required for deposit")
    
    account = accounts_db.get(transaction_data.to_account_id)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "from_account_id": None,
        "to_account_id": transaction_data.to_account_id,
        "amount": transaction_data.amount,
        "transaction_type": TransactionType.DEPOSIT,
        "status": TransactionStatus.COMPLETED,
        "description": transaction_data.description,
        "created_at": datetime.utcnow()
    }
    transactions_db[transaction_id] = transaction
    
    # Update account balance
    accounts_db[transaction_data.to_account_id]["balance"] += transaction_data.amount
    
    transaction_response = Transaction(**transaction)
    return APIResponse(data=transaction_response, message="Deposit successful", status_code=201)

@app.post("/api/transactions/transfer", response_model=APIResponse)
async def transfer_funds(transfer_data: Transfer, current_user: dict = Depends(get_current_user)):
    from_account = accounts_db.get(transfer_data.from_account_id)
    to_account = accounts_db.get(transfer_data.to_account_id)
    
    if not from_account or from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="From account not found")
    
    if not to_account:
        raise HTTPException(status_code=404, detail="To account not found")
    
    if from_account["balance"] < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "from_account_id": transfer_data.from_account_id,
        "to_account_id": transfer_data.to_account_id,
        "amount": transfer_data.amount,
        "transaction_type": TransactionType.TRANSFER,
        "status": TransactionStatus.COMPLETED,
        "description": transfer_data.description,
        "created_at": datetime.utcnow()
    }
    transactions_db[transaction_id] = transaction
    
    # Update balances
    accounts_db[transfer_data.from_account_id]["balance"] -= transfer_data.amount
    accounts_db[transfer_data.to_account_id]["balance"] += transfer_data.amount
    
    transaction_response = Transaction(**transaction)
    return APIResponse(data=transaction_response, message="Transfer successful", status_code=201)

@app.post("/api/payments/process", response_model=APIResponse)
async def process_payment(payment_data: Payment, current_user: dict = Depends(get_current_user)):
    account = accounts_db.get(payment_data.account_id)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["balance"] < payment_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "from_account_id": payment_data.account_id,
        "to_account_id": None,
        "amount": payment_data.amount,
        "transaction_type": TransactionType.PAYMENT,
        "status": TransactionStatus.COMPLETED,
        "description": f"Payment to {payment_data.recipient}: {payment_data.description}",
        "created_at": datetime.utcnow()
    }
    transactions_db[transaction_id] = transaction
    
    # Update account balance
    accounts_db[payment_data.account_id]["balance"] -= payment_data.amount
    
    transaction_response = Transaction(**transaction)
    return APIResponse(data=transaction_response, message="Payment processed successfully", status_code=201)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)