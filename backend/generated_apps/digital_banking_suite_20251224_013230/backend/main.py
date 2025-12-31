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

# In-memory storage
users_db: Dict[str, Dict] = {}
accounts_db: Dict[str, Dict] = {}
transactions_db: Dict[str, Dict] = {}
sessions_db: Dict[str, Dict] = {}

class TransactionType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    TRANSFER = "transfer"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AccountCreate(BaseModel):
    account_type: str = "checking"
    initial_balance: Decimal = Decimal("0.00")

class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: Decimal
    description: Optional[str] = None

class PaymentRequest(BaseModel):
    account_id: str
    amount: Decimal
    recipient: str
    description: Optional[str] = None

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
    account_type: str
    account_number: str
    balance: Decimal
    created_at: datetime
    is_active: bool = True

class Transaction(BaseModel):
    id: str
    account_id: str
    transaction_type: TransactionType
    amount: Decimal
    balance_after: Decimal
    description: str
    status: TransactionStatus
    created_at: datetime
    reference_id: Optional[str] = None

class AuthToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime

# Utility functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {"user_id": user_id, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def generate_account_number() -> str:
    return f"ACC{str(uuid.uuid4().int)[:10]}"

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None or user_id not in users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        return users_db[user_id]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoints
@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(status="healthy", timestamp=datetime.utcnow())

@app.post("/auth/register", response_model=User)
async def register_user(user_data: UserRegistration):
    if user_data.email in [u["email"] for u in users_db.values()]:
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
        "created_at": datetime.utcnow()
    }
    
    users_db[user_id] = user
    
    return User(**{k: v for k, v in user.items() if k != "password"})

@app.post("/auth/login", response_model=AuthToken)
async def login_user(login_data: UserLogin):
    user = next((u for u in users_db.values() if u["email"] == login_data.email), None)
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(user["id"])
    sessions_db[user["id"]] = {"token": access_token, "created_at": datetime.utcnow()}
    
    return AuthToken(access_token=access_token, token_type="bearer", expires_in=3600)

@app.post("/accounts", response_model=Account)
async def create_account(account_data: AccountCreate, current_user: Dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    account_number = generate_account_number()
    
    account = {
        "id": account_id,
        "user_id": current_user["id"],
        "account_type": account_data.account_type,
        "account_number": account_number,
        "balance": account_data.initial_balance,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    accounts_db[account_id] = account
    
    if account_data.initial_balance > 0:
        transaction_id = str(uuid.uuid4())
        transaction = {
            "id": transaction_id,
            "account_id": account_id,
            "transaction_type": TransactionType.CREDIT,
            "amount": account_data.initial_balance,
            "balance_after": account_data.initial_balance,
            "description": "Initial deposit",
            "status": TransactionStatus.COMPLETED,
            "created_at": datetime.utcnow(),
            "reference_id": None
        }
        transactions_db[transaction_id] = transaction
    
    return Account(**account)

@app.get("/accounts", response_model=List[Account])
async def get_accounts(current_user: Dict = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db.values() if acc["user_id"] == current_user["id"]]
    return [Account(**acc) for acc in user_accounts]

@app.get("/accounts/{account_id}/transactions", response_model=List[Transaction])
async def get_account_transactions(account_id: str, current_user: Dict = Depends(get_current_user)):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts_db[account_id]
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account_transactions = [t for t in transactions_db.values() if t["account_id"] == account_id]
    account_transactions.sort(key=lambda x: x["created_at"], reverse=True)
    
    return [Transaction(**t) for t in account_transactions]

@app.post("/transfers", response_model=Transaction)
async def transfer_funds(transfer_data: TransferRequest, current_user: Dict = Depends(get_current_user)):
    from_account = accounts_db.get(transfer_data.from_account_id)
    to_account = accounts_db.get(transfer_data.to_account_id)
    
    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if from_account["balance"] < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    if transfer_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    # Process transfer
    reference_id = str(uuid.uuid4())
    
    # Debit from source account
    from_account["balance"] -= transfer_data.amount
    debit_transaction_id = str(uuid.uuid4())
    debit_transaction = {
        "id": debit_transaction_id,
        "account_id": transfer_data.from_account_id,
        "transaction_type": TransactionType.TRANSFER,
        "amount": -transfer_data.amount,
        "balance_after": from_account["balance"],
        "description": f"Transfer to {to_account['account_number']}: {transfer_data.description or 'Fund transfer'}",
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "reference_id": reference_id
    }
    transactions_db[debit_transaction_id] = debit_transaction
    
    # Credit to destination account
    to_account["balance"] += transfer_data.amount
    credit_transaction_id = str(uuid.uuid4())
    credit_transaction = {
        "id": credit_transaction_id,
        "account_id": transfer_data.to_account_id,
        "transaction_type": TransactionType.TRANSFER,
        "amount": transfer_data.amount,
        "balance_after": to_account["balance"],
        "description": f"Transfer from {from_account['account_number']}: {transfer_data.description or 'Fund transfer'}",
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "reference_id": reference_id
    }
    transactions_db[credit_transaction_id] = credit_transaction
    
    return Transaction(**debit_transaction)

@app.post("/payments", response_model=Transaction)
async def make_payment(payment_data: PaymentRequest, current_user: Dict = Depends(get_current_user)):
    account = accounts_db.get(payment_data.account_id)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if account["balance"] < payment_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    if payment_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    # Process payment
    account["balance"] -= payment_data.amount
    transaction_id = str(uuid.uuid4())
    
    transaction = {
        "id": transaction_id,
        "account_id": payment_data.account_id,
        "transaction_type": TransactionType.DEBIT,
        "amount": -payment_data.amount,
        "balance_after": account["balance"],
        "description": f"Payment to {payment_data.recipient}: {payment_data.description or 'Payment'}",
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "reference_id": None
    }
    
    transactions_db[transaction_id] = transaction
    
    return Transaction(**transaction)

@app.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard(current_user: Dict = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db.values() if acc["user_id"] == current_user["id"]]
    total_balance = sum(acc["balance"] for acc in user_accounts)
    
    recent_transactions = []
    for acc in user_accounts:
        acc_transactions = [t for t in transactions_db.values() if t["account_id"] == acc["id"]]
        recent_transactions.extend(acc_transactions)
    
    recent_transactions.sort(key=lambda x: x["created_at"], reverse=True)
    recent_transactions = recent_transactions[:10]
    
    return {
        "user": {k: v for k, v in current_user.items() if k != "password"},
        "total_balance": total_balance,
        "accounts_count": len(user_accounts),
        "recent_transactions": [Transaction(**t) for t in recent_transactions]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)