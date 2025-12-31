from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import uuid
from decimal import Decimal
import json

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
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# In-memory storage
users_db: Dict[str, Dict] = {}
accounts_db: Dict[str, Dict] = {}
transactions_db: Dict[str, Dict] = {}
sessions_db: Dict[str, Dict] = {}

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

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
    account_number: str
    account_type: str
    balance: Decimal
    currency: str
    created_at: datetime

class AccountCreate(BaseModel):
    account_type: str = Field(..., regex="^(checking|savings|credit)$")
    currency: str = Field(default="USD", regex="^(USD|EUR|GBP)$")

class Transaction(BaseModel):
    id: str
    account_id: str
    amount: Decimal
    transaction_type: str
    description: str
    recipient_account: Optional[str] = None
    created_at: datetime
    status: str

class TransactionCreate(BaseModel):
    account_id: str
    amount: Decimal = Field(..., gt=0)
    transaction_type: str = Field(..., regex="^(transfer|deposit|withdrawal)$")
    description: str
    recipient_account: Optional[str] = None

class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: Decimal = Field(..., gt=0)
    description: str

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = users_db.get(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_account_number() -> str:
    return f"ACC{uuid.uuid4().hex[:10].upper()}"

# Endpoints
@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        services={
            "auth": "operational",
            "accounts": "operational",
            "transactions": "operational"
        }
    )

@app.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    if user_data.email in [u["email"] for u in users_db.values()]:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow()
    }
    
    access_token = create_access_token(data={"sub": user_id})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = None
    for u in users_db.values():
        if u["email"] == credentials.email:
            user = u
            break
    
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["id"]})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    return User(
        id=current_user["id"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        phone=current_user["phone"],
        created_at=current_user["created_at"]
    )

@app.post("/accounts", response_model=Account)
async def create_account(account_data: AccountCreate, current_user: Dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    account = {
        "id": account_id,
        "user_id": current_user["id"],
        "account_number": generate_account_number(),
        "account_type": account_data.account_type,
        "balance": Decimal("0.00"),
        "currency": account_data.currency,
        "created_at": datetime.utcnow()
    }
    accounts_db[account_id] = account
    return Account(**account)

@app.get("/accounts", response_model=List[Account])
async def get_user_accounts(current_user: Dict = Depends(get_current_user)):
    user_accounts = [
        Account(**account) for account in accounts_db.values()
        if account["user_id"] == current_user["id"]
    ]
    return user_accounts

@app.get("/accounts/{account_id}", response_model=Account)
async def get_account(account_id: str, current_user: Dict = Depends(get_current_user)):
    account = accounts_db.get(account_id)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    return Account(**account)

@app.post("/transactions", response_model=Transaction)
async def create_transaction(transaction_data: TransactionCreate, current_user: Dict = Depends(get_current_user)):
    account = accounts_db.get(transaction_data.account_id)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    transaction_id = str(uuid.uuid4())
    
    # Process transaction based on type
    if transaction_data.transaction_type == "deposit":
        account["balance"] += transaction_data.amount
        status = "completed"
    elif transaction_data.transaction_type == "withdrawal":
        if account["balance"] < transaction_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        account["balance"] -= transaction_data.amount
        status = "completed"
    elif transaction_data.transaction_type == "transfer":
        if not transaction_data.recipient_account:
            raise HTTPException(status_code=400, detail="Recipient account required for transfers")
        recipient = accounts_db.get(transaction_data.recipient_account)
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient account not found")
        if account["balance"] < transaction_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        account["balance"] -= transaction_data.amount
        recipient["balance"] += transaction_data.amount
        status = "completed"
    
    transaction = {
        "id": transaction_id,
        "account_id": transaction_data.account_id,
        "amount": transaction_data.amount,
        "transaction_type": transaction_data.transaction_type,
        "description": transaction_data.description,
        "recipient_account": transaction_data.recipient_account,
        "created_at": datetime.utcnow(),
        "status": status
    }
    transactions_db[transaction_id] = transaction
    return Transaction(**transaction)

@app.post("/transfer", response_model=Transaction)
async def transfer_funds(transfer_data: TransferRequest, current_user: Dict = Depends(get_current_user)):
    from_account = accounts_db.get(transfer_data.from_account)
    to_account = accounts_db.get(transfer_data.to_account)
    
    if not from_account or from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Source account not found")
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    if from_account["balance"] < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    transaction_id = str(uuid.uuid4())
    
    # Execute transfer
    from_account["balance"] -= transfer_data.amount
    to_account["balance"] += transfer_data.amount
    
    transaction = {
        "id": transaction_id,
        "account_id": transfer_data.from_account,
        "amount": transfer_data.amount,
        "transaction_type": "transfer",
        "description": transfer_data.description,
        "recipient_account": transfer_data.to_account,
        "created_at": datetime.utcnow(),
        "status": "completed"
    }
    transactions_db[transaction_id] = transaction
    return Transaction(**transaction)

@app.get("/transactions/{account_id}", response_model=List[Transaction])
async def get_account_transactions(account_id: str, current_user: Dict = Depends(get_current_user)):
    account = accounts_db.get(account_id)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account_transactions = [
        Transaction(**transaction) for transaction in transactions_db.values()
        if transaction["account_id"] == account_id or transaction.get("recipient_account") == account_id
    ]
    return sorted(account_transactions, key=lambda x: x.created_at, reverse=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)