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
import random
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

class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: str
    created_at: datetime

class AccountCreate(BaseModel):
    account_type: AccountType
    initial_balance: Decimal = Decimal("0.00")

class AccountResponse(BaseModel):
    id: str
    user_id: str
    account_type: AccountType
    balance: Decimal
    account_number: str
    created_at: datetime
    is_active: bool

class TransactionCreate(BaseModel):
    account_id: str
    transaction_type: TransactionType
    amount: Decimal
    description: Optional[str] = None
    recipient_account_id: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    account_id: str
    transaction_type: TransactionType
    amount: Decimal
    balance_after: Decimal
    description: Optional[str]
    recipient_account_id: Optional[str]
    created_at: datetime
    status: str

class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: Decimal
    description: Optional[str] = None

class PaymentRequest(BaseModel):
    account_id: str
    payee: str
    amount: Decimal
    description: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime

# Utility functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check if session exists
        if user_id not in sessions_db:
            raise HTTPException(status_code=401, detail="Session expired")
            
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
            
        return users_db[user_id]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_account_number() -> str:
    return str(random.randint(1000000000, 9999999999))

# Health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow()
    )

# Authentication endpoints
@app.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    # Check if user already exists
    for user in users_db.values():
        if user["email"] == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    user = {
        "id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow()
    }
    
    users_db[user_id] = user
    sessions_db[user_id] = {"created_at": datetime.utcnow()}
    
    access_token = create_access_token(data={"sub": user_id})
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        phone=user["phone"],
        created_at=user["created_at"]
    )
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@app.post("/auth/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin):
    user = None
    for u in users_db.values():
        if u["email"] == login_data.email:
            user = u
            break
    
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    sessions_db[user["id"]] = {"created_at": datetime.utcnow()}
    access_token = create_access_token(data={"sub": user["id"]})
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        phone=user["phone"],
        created_at=user["created_at"]
    )
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

# Account management endpoints
@app.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(account_data: AccountCreate, current_user: dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    account_number = generate_account_number()
    
    account = {
        "id": account_id,
        "user_id": current_user["id"],
        "account_type": account_data.account_type,
        "balance": account_data.initial_balance,
        "account_number": account_number,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    accounts_db[account_id] = account
    
    return AccountResponse(**account)

@app.get("/accounts", response_model=List[AccountResponse])
async def get_user_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [
        AccountResponse(**account) 
        for account in accounts_db.values() 
        if account["user_id"] == current_user["id"]
    ]
    return user_accounts

@app.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str, current_user: dict = Depends(get_current_user)):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts_db[account_id]
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return AccountResponse(**account)

# Transaction endpoints
@app.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction_data: TransactionCreate, current_user: dict = Depends(get_current_user)):
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
    transaction = {
        "id": transaction_id,
        "account_id": transaction_data.account_id,
        "transaction_type": transaction_data.transaction_type,
        "amount": transaction_data.amount,
        "balance_after": account["balance"],
        "description": transaction_data.description,
        "recipient_account_id": transaction_data.recipient_account_id,
        "created_at": datetime.utcnow(),
        "status": "completed"
    }
    
    transactions_db[transaction_id] = transaction
    
    return TransactionResponse(**transaction)

@app.post("/transactions/transfer", response_model=Dict[str, Any])
async def transfer_funds(transfer_data: TransferRequest, current_user: dict = Depends(get_current_user)):
    # Validate accounts
    if transfer_data.from_account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Source account not found")
    if transfer_data.to_account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Destination account not found")
    
    from_account = accounts_db[transfer_data.from_account_id]
    to_account = accounts_db[transfer_data.to_account_id]
    
    # Check ownership of source account
    if from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check sufficient funds
    if from_account["balance"] < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Execute transfer
    from_account["balance"] -= transfer_data.amount
    to_account["balance"] += transfer_data.amount
    
    # Create transaction records
    transfer_id = str(uuid.uuid4())
    debit_transaction = {
        "id": str(uuid.uuid4()),
        "account_id": transfer_data.from_account_id,
        "transaction_type": TransactionType.TRANSFER,
        "amount": -transfer_data.amount,
        "balance_after": from_account["balance"],
        "description": f"Transfer to {to_account['account_number']} - {transfer_data.description or ''}",
        "recipient_account_id": transfer_data.to_account_id,
        "created_at": datetime.utcnow(),
        "status": "completed"
    }
    
    credit_transaction = {
        "id": str(uuid.uuid4()),
        "account_id": transfer_data.to_account_id,
        "transaction_type": TransactionType.TRANSFER,
        "amount": transfer_data.amount,
        "balance_after": to_account["balance"],
        "description": f"Transfer from {from_account['account_number']} - {transfer_data.description or ''}",
        "recipient_account_id": transfer_data.from_account_id,
        "created_at": datetime.utcnow(),
        "status": "completed"
    }
    
    transactions_db[debit_transaction["id"]] = debit_transaction
    transactions_db[credit_transaction["id"]] = credit_transaction
    
    return {
        "transfer_id": transfer_id,
        "status": "completed",
        "amount": transfer_data.amount,
        "from_account": transfer_data.from_account_id,
        "to_account": transfer_data.to_account_id,
        "timestamp": datetime.utcnow()
    }

@app.get("/accounts/{account_id}/transactions", response_model=List[TransactionResponse])
async def get_account_transactions(account_id: str, current_user: dict = Depends(get_current_user)):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts_db[account_id]
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account_transactions = [
        TransactionResponse(**transaction)
        for transaction in transactions_db.values()
        if transaction["account_id"] == account_id
    ]
    
    return sorted(account_transactions, key=lambda x: x.created_at, reverse=True)

@app.post("/payments", response_model=Dict[str, Any])
async def make_payment(payment_data: PaymentRequest, current_user: dict = Depends(get_current_user)):
    if payment_data.account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts_db[payment_data.account_id]
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if account["balance"] < payment_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Process payment
    account["balance"] -= payment_data.amount
    
    payment_id = str(uuid.uuid4())
    transaction = {
        "id": str(uuid.uuid4()),
        "account_id": payment_data.account_id,
        "transaction_type": TransactionType.PAYMENT,
        "amount": -payment_data.amount,
        "balance_after": account["balance"],
        "description": f"Payment to {payment_data.payee} - {payment_data.description or ''}",
        "recipient_account_id": None,
        "created_at": datetime.utcnow(),
        "status": "completed"
    }
    
    transactions_db[transaction["id"]] = transaction
    
    return {
        "payment_id": payment_id,
        "status": "completed",
        "amount": payment_data.amount,
        "payee": payment_data.payee,
        "account_id": payment_data.account_id,
        "timestamp": datetime.utcnow()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)