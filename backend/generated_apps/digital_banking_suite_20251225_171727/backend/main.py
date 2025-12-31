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

SECRET_KEY = "banking_secret_key_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# Enums
class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
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
    CANCELLED = "cancelled"

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: str
    created_at: datetime

class AccountCreate(BaseModel):
    account_type: AccountType
    initial_balance: Decimal = Decimal('0.00')

class AccountResponse(BaseModel):
    id: str
    account_number: str
    account_type: AccountType
    balance: Decimal
    user_id: str
    created_at: datetime
    is_active: bool

class TransferRequest(BaseModel):
    from_account_id: str
    to_account_number: str
    amount: Decimal
    description: Optional[str] = None

class PaymentRequest(BaseModel):
    account_id: str
    recipient_name: str
    recipient_account: str
    amount: Decimal
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    account_id: str
    transaction_type: TransactionType
    amount: Decimal
    balance_after: Decimal
    description: str
    status: TransactionStatus
    created_at: datetime
    reference_number: str

class AnalyticsResponse(BaseModel):
    total_balance: Decimal
    total_transactions: int
    monthly_spending: Decimal
    top_categories: List[Dict[str, Any]]
    account_summary: List[Dict[str, Any]]

# In-memory storage
users_db: Dict[str, Dict] = {}
accounts_db: Dict[str, Dict] = {}
transactions_db: Dict[str, Dict] = {}
sessions_db: Dict[str, str] = {}

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        return users_db[user_id]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_account_number() -> str:
    return f"ACC{str(uuid.uuid4().int)[:10]}"

def generate_reference_number() -> str:
    return f"REF{str(uuid.uuid4().int)[:12]}"

# Initialize sample data
def init_sample_data():
    # Sample user
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        "id": user_id,
        "email": "john.doe@example.com",
        "password": hash_password("password123"),
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "created_at": datetime.utcnow()
    }
    
    # Sample accounts
    checking_account_id = str(uuid.uuid4())
    savings_account_id = str(uuid.uuid4())
    
    accounts_db[checking_account_id] = {
        "id": checking_account_id,
        "account_number": "ACC1234567890",
        "account_type": AccountType.CHECKING,
        "balance": Decimal('5000.00'),
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    accounts_db[savings_account_id] = {
        "id": savings_account_id,
        "account_number": "ACC0987654321",
        "account_type": AccountType.SAVINGS,
        "balance": Decimal('15000.00'),
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    # Sample transactions
    for i in range(5):
        transaction_id = str(uuid.uuid4())
        transactions_db[transaction_id] = {
            "id": transaction_id,
            "account_id": checking_account_id,
            "transaction_type": TransactionType.DEPOSIT,
            "amount": Decimal('1000.00'),
            "balance_after": Decimal('5000.00'),
            "description": f"Sample deposit {i+1}",
            "status": TransactionStatus.COMPLETED,
            "created_at": datetime.utcnow() - timedelta(days=i),
            "reference_number": generate_reference_number()
        }

init_sample_data()

# Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    # Check if user exists
    for user in users_db.values():
        if user["email"] == user_data.email:
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
    
    return UserResponse(**{k: v for k, v in user.items() if k != "password"})

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    user = None
    for u in users_db.values():
        if u["email"] == credentials.email:
            user = u
            break
    
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["id"]})
    sessions_db[access_token] = user["id"]
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    return {"message": "Successfully logged out"}

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(**{k: v for k, v in current_user.items() if k != "password"})

@app.get("/api/accounts", response_model=List[AccountResponse])
async def get_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [
        AccountResponse(**account) 
        for account in accounts_db.values() 
        if account["user_id"] == current_user["id"]
    ]
    return user_accounts

@app.post("/api/accounts", response_model=AccountResponse)
async def create_account(account_data: AccountCreate, current_user: dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    account = {
        "id": account_id,
        "account_number": generate_account_number(),
        "account_type": account_data.account_type,
        "balance": account_data.initial_balance,
        "user_id": current_user["id"],
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    accounts_db[account_id] = account
    
    return AccountResponse(**account)

@app.post("/api/transfers", response_model=TransactionResponse)
async def create_transfer(transfer: TransferRequest, current_user: dict = Depends(get_current_user)):
    # Verify from account belongs to user
    from_account = accounts_db.get(transfer.from_account_id)
    if not from_account or from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Find to account
    to_account = None
    for account in accounts_db.values():
        if account["account_number"] == transfer.to_account_number:
            to_account = account
            break
    
    if not to_account:
        raise HTTPException(status_code=404, detail="Recipient account not found")
    
    # Check balance
    if from_account["balance"] < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Process transfer
    from_account["balance"] -= transfer.amount
    to_account["balance"] += transfer.amount
    
    # Create transaction records
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "account_id": transfer.from_account_id,
        "transaction_type": TransactionType.TRANSFER,
        "amount": -transfer.amount,
        "balance_after": from_account["balance"],
        "description": transfer.description or f"Transfer to {transfer.to_account_number}",
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "reference_number": generate_reference_number()
    }
    transactions_db[transaction_id] = transaction
    
    return TransactionResponse(**transaction)

@app.post("/api/payments", response_model=TransactionResponse)
async def process_payment(payment: PaymentRequest, current_user: dict = Depends(get_current_user)):
    # Verify account belongs to user
    account = accounts_db.get(payment.account_id)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Check balance
    if account["balance"] < payment.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Process payment
    account["balance"] -= payment.amount
    
    # Create transaction record
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "account_id": payment.account_id,
        "transaction_type": TransactionType.PAYMENT,
        "amount": -payment.amount,
        "balance_after": account["balance"],
        "description": payment.description or f"Payment to {payment.recipient_name}",
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "reference_number": generate_reference_number()
    }
    transactions_db[transaction_id] = transaction
    
    return TransactionResponse(**transaction)

@app.get("/api/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    account_id: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    user_account_ids = {
        account["id"] for account in accounts_db.values() 
        if account["user_id"] == current_user["id"]
    }
    
    transactions = []
    for transaction in transactions_db.values():
        if transaction["account_id"] in user_account_ids:
            if not account_id or transaction["account_id"] == account_id:
                transactions.append(TransactionResponse(**transaction))
    
    # Sort by created_at descending and limit
    transactions.sort(key=lambda x: x.created_at, reverse=True)
    return transactions[:limit]

@app.get("/api/analytics", response_model=AnalyticsResponse)
async def get_analytics(current_user: dict = Depends(get_current_user)):
    user_accounts = [
        account for account in accounts_db.values() 
        if account["user_id"] == current_user["id"]
    ]
    
    user_account_ids = {account["id"] for account in user_accounts}
    user_transactions = [
        transaction for transaction in transactions_db.values()
        if transaction["account_id"] in user_account_ids
    ]
    
    total_balance = sum(account["balance"] for account in user_accounts)
    total_transactions = len(user_transactions)
    
    # Calculate monthly spending (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_spending = sum(
        abs(transaction["amount"]) for transaction in user_transactions
        if transaction["created_at"] >= thirty_days_ago and transaction["amount"] < 0
    )
    
    # Account summary
    account_summary = [
        {
            "account_type": account["account_type"],
            "balance": float(account["balance"]),
            "account_number": account["account_number"][-4:]  # Last 4 digits
        }
        for account in user_accounts
    ]
    
    return AnalyticsResponse(
        total_balance=total_balance,
        total_transactions=total_transactions,
        monthly_spending=monthly_spending,
        top_categories=[
            {"category": "Transfers", "amount": float(monthly_spending * Decimal('0.6'))},
            {"category": "Payments", "amount": float(monthly_spending * Decimal('0.4'))}
        ],
        account_summary=account_summary
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)