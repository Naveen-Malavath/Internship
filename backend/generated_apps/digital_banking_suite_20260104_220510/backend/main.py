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
SECRET_KEY = "banking_secret_key_2024"
ALGORITHM = "HS256"

# Enums
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
    CANCELLED = "cancelled"

# Pydantic Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
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

class AccountCreate(BaseModel):
    account_type: AccountType
    initial_deposit: Decimal = Field(..., ge=0)

class Transaction(BaseModel):
    id: str
    from_account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    transaction_type: TransactionType
    amount: Decimal
    currency: str = "USD"
    description: str
    status: TransactionStatus
    created_at: datetime
    processed_at: Optional[datetime] = None

class TransactionCreate(BaseModel):
    to_account_id: Optional[str] = None
    transaction_type: TransactionType
    amount: Decimal = Field(..., gt=0)
    description: str

class PaymentCreate(BaseModel):
    from_account_id: str
    recipient_account: str
    amount: Decimal = Field(..., gt=0)
    description: str

class TransferCreate(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: Decimal = Field(..., gt=0)
    description: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class APIResponse(BaseModel):
    status: str = "success"
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None

class PaginatedResponse(BaseModel):
    status: str = "success"
    data: List[Any]
    pagination: Dict[str, Any]

# In-memory storage
users_db: Dict[str, Dict] = {}
accounts_db: Dict[str, Dict] = {}
transactions_db: Dict[str, Dict] = {}

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=30)
    payload = {"user_id": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        return users_db[user_id]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_account_number() -> str:
    return str(uuid.uuid4().int)[:12]

# Health check
@app.get("/health")
async def health_check():
    return APIResponse(data={"status": "healthy", "timestamp": datetime.utcnow()})

# Authentication endpoints
@app.post("/api/auth/register", response_model=AuthResponse)
async def register(user_data: UserCreate):
    if any(user["username"] == user_data.username for user in users_db.values()):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if any(user["email"] == user_data.email for user in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    users_db[user_id] = user
    token = create_access_token(user_id)
    
    user_response = User(**{k: v for k, v in user.items() if k != "password"})
    return AuthResponse(access_token=token, token_type="bearer", user=user_response)

@app.post("/api/auth/login", response_model=AuthResponse)
async def login(login_data: UserLogin):
    user = next((u for u in users_db.values() if u["username"] == login_data.username), None)
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user["id"])
    user_response = User(**{k: v for k, v in user.items() if k != "password"})
    return AuthResponse(access_token=token, token_type="bearer", user=user_response)

@app.get("/api/auth/me", response_model=APIResponse)
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    user_response = User(**{k: v for k, v in current_user.items() if k != "password"})
    return APIResponse(data=user_response)

# Account endpoints
@app.post("/api/accounts", response_model=APIResponse)
async def create_account(account_data: AccountCreate, current_user: Dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    account = {
        "id": account_id,
        "user_id": current_user["id"],
        "account_number": generate_account_number(),
        "account_type": account_data.account_type,
        "balance": float(account_data.initial_deposit),
        "currency": "USD",
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    accounts_db[account_id] = account
    
    if account_data.initial_deposit > 0:
        transaction_id = str(uuid.uuid4())
        transaction = {
            "id": transaction_id,
            "from_account_id": None,
            "to_account_id": account_id,
            "transaction_type": TransactionType.DEPOSIT,
            "amount": float(account_data.initial_deposit),
            "currency": "USD",
            "description": "Initial deposit",
            "status": TransactionStatus.COMPLETED,
            "created_at": datetime.utcnow(),
            "processed_at": datetime.utcnow()
        }
        transactions_db[transaction_id] = transaction
    
    return APIResponse(data=Account(**account))

@app.get("/api/accounts", response_model=APIResponse)
async def get_user_accounts(current_user: Dict = Depends(get_current_user)):
    user_accounts = [Account(**acc) for acc in accounts_db.values() if acc["user_id"] == current_user["id"]]
    return APIResponse(data=user_accounts)

@app.get("/api/accounts/{account_id}", response_model=APIResponse)
async def get_account(account_id: str, current_user: Dict = Depends(get_current_user)):
    account = accounts_db.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return APIResponse(data=Account(**account))

# Transaction endpoints
@app.post("/api/transactions", response_model=APIResponse)
async def create_transaction(transaction_data: TransactionCreate, current_user: Dict = Depends(get_current_user)):
    if transaction_data.transaction_type == TransactionType.TRANSFER and not transaction_data.to_account_id:
        raise HTTPException(status_code=400, detail="to_account_id required for transfers")
    
    user_accounts = [acc_id for acc_id, acc in accounts_db.items() if acc["user_id"] == current_user["id"]]
    if not user_accounts:
        raise HTTPException(status_code=400, detail="No accounts found")
    
    from_account_id = user_accounts[0]  # Use first account as default
    from_account = accounts_db[from_account_id]
    
    if transaction_data.transaction_type == TransactionType.WITHDRAWAL:
        if from_account["balance"] < float(transaction_data.amount):
            raise HTTPException(status_code=400, detail="Insufficient funds")
        accounts_db[from_account_id]["balance"] -= float(transaction_data.amount)
    elif transaction_data.transaction_type == TransactionType.DEPOSIT:
        accounts_db[from_account_id]["balance"] += float(transaction_data.amount)
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "from_account_id": from_account_id if transaction_data.transaction_type != TransactionType.DEPOSIT else None,
        "to_account_id": transaction_data.to_account_id if transaction_data.transaction_type == TransactionType.TRANSFER else from_account_id,
        "transaction_type": transaction_data.transaction_type,
        "amount": float(transaction_data.amount),
        "currency": "USD",
        "description": transaction_data.description,
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "processed_at": datetime.utcnow()
    }
    
    transactions_db[transaction_id] = transaction
    return APIResponse(data=Transaction(**transaction))

@app.get("/api/transactions", response_model=PaginatedResponse)
async def get_transactions(
    page: int = 1, 
    limit: int = 10, 
    current_user: Dict = Depends(get_current_user)
):
    user_account_ids = [acc_id for acc_id, acc in accounts_db.items() if acc["user_id"] == current_user["id"]]
    user_transactions = [
        Transaction(**txn) for txn in transactions_db.values() 
        if txn["from_account_id"] in user_account_ids or txn["to_account_id"] in user_account_ids
    ]
    
    start = (page - 1) * limit
    end = start + limit
    paginated_transactions = user_transactions[start:end]
    
    pagination = {
        "page": page,
        "limit": limit,
        "total": len(user_transactions),
        "pages": (len(user_transactions) + limit - 1) // limit
    }
    
    return PaginatedResponse(data=paginated_transactions, pagination=pagination)

# Payment endpoints
@app.post("/api/payments", response_model=APIResponse)
async def process_payment(payment_data: PaymentCreate, current_user: Dict = Depends(get_current_user)):
    from_account = accounts_db.get(payment_data.from_account_id)
    if not from_account:
        raise HTTPException(status_code=404, detail="Source account not found")
    
    if from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if from_account["balance"] < float(payment_data.amount):
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Deduct from source account
    accounts_db[payment_data.from_account_id]["balance"] -= float(payment_data.amount)
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "from_account_id": payment_data.from_account_id,
        "to_account_id": None,
        "transaction_type": TransactionType.PAYMENT,
        "amount": float(payment_data.amount),
        "currency": "USD",
        "description": f"Payment to {payment_data.recipient_account}: {payment_data.description}",
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "processed_at": datetime.utcnow()
    }
    
    transactions_db[transaction_id] = transaction
    return APIResponse(data=Transaction(**transaction), message="Payment processed successfully")

@app.post("/api/transfers", response_model=APIResponse)
async def process_transfer(transfer_data: TransferCreate, current_user: Dict = Depends(get_current_user)):
    from_account = accounts_db.get(transfer_data.from_account_id)
    to_account = accounts_db.get(transfer_data.to_account_id)
    
    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if from_account["balance"] < float(transfer_data.amount):
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Process transfer
    accounts_db[transfer_data.from_account_id]["balance"] -= float(transfer_data.amount)
    accounts_db[transfer_data.to_account_id]["balance"] += float(transfer_data.amount)
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "from_account_id": transfer_data.from_account_id,
        "to_account_id": transfer_data.to_account_id,
        "transaction_type": TransactionType.TRANSFER,
        "amount": float(transfer_data.amount),
        "currency": "USD",
        "description": transfer_data.description,
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "processed_at": datetime.utcnow()
    }
    
    transactions_db[transaction_id] = transaction
    return APIResponse(data=Transaction(**transaction), message="Transfer completed successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)