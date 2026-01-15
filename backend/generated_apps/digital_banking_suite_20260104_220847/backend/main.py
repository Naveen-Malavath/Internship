from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import jwt
import bcrypt
import uuid

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
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# In-memory storage
users_db = {}
accounts_db = {}
transactions_db = {}
payments_db = {}

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str
    email: str
    full_name: str
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

class CreateAccount(BaseModel):
    account_type: str
    currency: str = "USD"

class Transaction(BaseModel):
    id: str
    account_id: str
    type: str
    amount: Decimal
    description: str
    timestamp: datetime
    balance_after: Decimal

class CreateTransaction(BaseModel):
    account_id: str
    type: str
    amount: Decimal
    description: str

class Payment(BaseModel):
    id: str
    from_account_id: str
    to_account_number: str
    amount: Decimal
    description: str
    status: str
    created_at: datetime

class CreatePayment(BaseModel):
    from_account_id: str
    to_account_number: str
    amount: Decimal
    description: str

class APIResponse(BaseModel):
    status: str
    message: str = ""
    data: Any = None

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

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
            raise HTTPException(status_code=401, detail="Invalid token")
        return users_db[user_id]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_account_number() -> str:
    return f"ACC{str(uuid.uuid4().int)[:10]}"

# Initialize sample data
sample_user_id = str(uuid.uuid4())
users_db[sample_user_id] = {
    "id": sample_user_id,
    "email": "demo@bank.com",
    "password": hash_password("demo123"),
    "full_name": "Demo User",
    "phone": "+1234567890",
    "created_at": datetime.utcnow()
}

sample_account_id = str(uuid.uuid4())
accounts_db[sample_account_id] = {
    "id": sample_account_id,
    "user_id": sample_user_id,
    "account_number": "ACC1234567890",
    "account_type": "checking",
    "balance": Decimal("5000.00"),
    "currency": "USD",
    "created_at": datetime.utcnow()
}

# Endpoints
@app.get("/health")
async def health_check():
    return APIResponse(status="success", message="Service is healthy")

@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    # Check if user exists
    for user in users_db.values():
        if user["email"] == user_data.email:
            raise HTTPException(status_code=400, detail="User already exists")
    
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow()
    }
    
    access_token = create_access_token(data={"sub": user_id})
    return APIResponse(
        status="success",
        message="User registered successfully",
        data={"access_token": access_token, "token_type": "bearer"}
    )

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    user = None
    for u in users_db.values():
        if u["email"] == user_data.email:
            user = u
            break
    
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["id"]})
    return APIResponse(
        status="success",
        message="Login successful",
        data={"access_token": access_token, "token_type": "bearer"}
    )

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    user_data = {
        "id": current_user["id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "phone": current_user["phone"],
        "created_at": current_user["created_at"]
    }
    return APIResponse(status="success", data=user_data)

@app.get("/api/accounts")
async def get_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [
        account for account in accounts_db.values()
        if account["user_id"] == current_user["id"]
    ]
    return APIResponse(status="success", data=user_accounts)

@app.post("/api/accounts")
async def create_account(account_data: CreateAccount, current_user: dict = Depends(get_current_user)):
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
    
    return APIResponse(
        status="success",
        message="Account created successfully",
        data=account
    )

@app.get("/api/accounts/{account_id}/transactions")
async def get_transactions(account_id: str, current_user: dict = Depends(get_current_user)):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts_db[account_id]
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account_transactions = [
        transaction for transaction in transactions_db.values()
        if transaction["account_id"] == account_id
    ]
    
    return APIResponse(status="success", data=account_transactions)

@app.post("/api/transactions")
async def create_transaction(transaction_data: CreateTransaction, current_user: dict = Depends(get_current_user)):
    account_id = transaction_data.account_id
    
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts_db[account_id]
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update balance
    if transaction_data.type == "debit" and account["balance"] < transaction_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    if transaction_data.type == "credit":
        account["balance"] += transaction_data.amount
    else:
        account["balance"] -= transaction_data.amount
    
    # Create transaction record
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "account_id": account_id,
        "type": transaction_data.type,
        "amount": transaction_data.amount,
        "description": transaction_data.description,
        "timestamp": datetime.utcnow(),
        "balance_after": account["balance"]
    }
    transactions_db[transaction_id] = transaction
    
    return APIResponse(
        status="success",
        message="Transaction created successfully",
        data=transaction
    )

@app.post("/api/payments")
async def create_payment(payment_data: CreatePayment, current_user: dict = Depends(get_current_user)):
    from_account_id = payment_data.from_account_id
    
    if from_account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Source account not found")
    
    from_account = accounts_db[from_account_id]
    if from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if from_account["balance"] < payment_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Find destination account
    to_account = None
    for account in accounts_db.values():
        if account["account_number"] == payment_data.to_account_number:
            to_account = account
            break
    
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    
    # Process payment
    payment_id = str(uuid.uuid4())
    payment = {
        "id": payment_id,
        "from_account_id": from_account_id,
        "to_account_number": payment_data.to_account_number,
        "amount": payment_data.amount,
        "description": payment_data.description,
        "status": "completed",
        "created_at": datetime.utcnow()
    }
    payments_db[payment_id] = payment
    
    # Update balances
    from_account["balance"] -= payment_data.amount
    to_account["balance"] += payment_data.amount
    
    # Create transaction records
    debit_transaction = {
        "id": str(uuid.uuid4()),
        "account_id": from_account_id,
        "type": "debit",
        "amount": payment_data.amount,
        "description": f"Payment to {payment_data.to_account_number}: {payment_data.description}",
        "timestamp": datetime.utcnow(),
        "balance_after": from_account["balance"]
    }
    transactions_db[debit_transaction["id"]] = debit_transaction
    
    credit_transaction = {
        "id": str(uuid.uuid4()),
        "account_id": to_account["id"],
        "type": "credit",
        "amount": payment_data.amount,
        "description": f"Payment from {from_account['account_number']}: {payment_data.description}",
        "timestamp": datetime.utcnow(),
        "balance_after": to_account["balance"]
    }
    transactions_db[credit_transaction["id"]] = credit_transaction
    
    return APIResponse(
        status="success",
        message="Payment processed successfully",
        data=payment
    )

@app.get("/api/payments/{payment_id}")
async def get_payment(payment_id: str, current_user: dict = Depends(get_current_user)):
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment = payments_db[payment_id]
    from_account = accounts_db.get(payment["from_account_id"])
    
    if not from_account or from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return APIResponse(status="success", data=payment)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)