from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import jwt
from passlib.context import CryptContext

# Initialize FastAPI app
app = FastAPI(title="Digital Banking Suite", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# In-memory storage
users_db = {}
accounts_db = {}
transactions_db = {}
payments_db = {}
sessions_db = {}

# Pydantic Models
class UserRegister(BaseModel):
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
    email: EmailStr
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

class CreateAccount(BaseModel):
    account_type: str
    currency: str = "USD"

class Transaction(BaseModel):
    id: str
    account_id: str
    type: str
    amount: Decimal
    description: str
    recipient_account: Optional[str] = None
    status: str
    created_at: datetime

class CreateTransaction(BaseModel):
    account_id: str
    type: str
    amount: Decimal
    description: str
    recipient_account: Optional[str] = None

class Payment(BaseModel):
    id: str
    from_account: str
    to_account: str
    amount: Decimal
    currency: str
    description: str
    status: str
    created_at: datetime

class CreatePayment(BaseModel):
    from_account: str
    to_account: str
    amount: Decimal
    description: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = users_db.get(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Authentication Endpoints
@app.post("/api/auth/register", response_model=User)
async def register(user_data: UserRegister):
    if user_data.email in [u["email"] for u in users_db.values()]:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    
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
    
    # Create default checking account
    account_id = str(uuid.uuid4())
    account_number = f"ACC{len(accounts_db) + 1:08d}"
    accounts_db[account_id] = {
        "id": account_id,
        "user_id": user_id,
        "account_number": account_number,
        "account_type": "checking",
        "balance": Decimal("0.00"),
        "currency": "USD",
        "created_at": datetime.utcnow()
    }
    
    return User(**{k: v for k, v in user.items() if k != "password"})

@app.post("/api/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    user = None
    for u in users_db.values():
        if u["email"] == login_data.email:
            user = u
            break
    
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    
    sessions_db[user["id"]] = access_token
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    sessions_db.pop(current_user["id"], None)
    return {"message": "Successfully logged out"}

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return User(**{k: v for k, v in current_user.items() if k != "password"})

# Account Management Endpoints
@app.get("/api/accounts", response_model=List[Account])
async def get_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db.values() if acc["user_id"] == current_user["id"]]
    return [Account(**acc) for acc in user_accounts]

@app.post("/api/accounts", response_model=Account)
async def create_account(account_data: CreateAccount, current_user: dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    account_number = f"ACC{len(accounts_db) + 1:08d}"
    
    account = {
        "id": account_id,
        "user_id": current_user["id"],
        "account_number": account_number,
        "account_type": account_data.account_type,
        "balance": Decimal("0.00"),
        "currency": account_data.currency,
        "created_at": datetime.utcnow()
    }
    
    accounts_db[account_id] = account
    return Account(**account)

@app.get("/api/accounts/{account_id}", response_model=Account)
async def get_account(account_id: str, current_user: dict = Depends(get_current_user)):
    account = accounts_db.get(account_id)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    return Account(**account)

# Transaction Endpoints
@app.get("/api/accounts/{account_id}/transactions", response_model=List[Transaction])
async def get_transactions(account_id: str, current_user: dict = Depends(get_current_user)):
    account = accounts_db.get(account_id)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account_transactions = [t for t in transactions_db.values() if t["account_id"] == account_id]
    return [Transaction(**t) for t in account_transactions]

@app.post("/api/transactions", response_model=Transaction)
async def create_transaction(transaction_data: CreateTransaction, current_user: dict = Depends(get_current_user)):
    account = accounts_db.get(transaction_data.account_id)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if transaction_data.type == "withdrawal" and account["balance"] < transaction_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "account_id": transaction_data.account_id,
        "type": transaction_data.type,
        "amount": transaction_data.amount,
        "description": transaction_data.description,
        "recipient_account": transaction_data.recipient_account,
        "status": "completed",
        "created_at": datetime.utcnow()
    }
    
    # Update account balance
    if transaction_data.type == "deposit":
        account["balance"] += transaction_data.amount
    elif transaction_data.type == "withdrawal":
        account["balance"] -= transaction_data.amount
    
    transactions_db[transaction_id] = transaction
    return Transaction(**transaction)

# Payment Endpoints
@app.post("/api/payments", response_model=Payment)
async def create_payment(payment_data: CreatePayment, current_user: dict = Depends(get_current_user)):
    from_account = accounts_db.get(payment_data.from_account)
    to_account = accounts_db.get(payment_data.to_account)
    
    if not from_account or from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Source account not found")
    
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    
    if from_account["balance"] < payment_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    payment_id = str(uuid.uuid4())
    payment = {
        "id": payment_id,
        "from_account": payment_data.from_account,
        "to_account": payment_data.to_account,
        "amount": payment_data.amount,
        "currency": from_account["currency"],
        "description": payment_data.description,
        "status": "completed",
        "created_at": datetime.utcnow()
    }
    
    # Update balances
    from_account["balance"] -= payment_data.amount
    to_account["balance"] += payment_data.amount
    
    # Create transactions for both accounts
    debit_transaction = {
        "id": str(uuid.uuid4()),
        "account_id": payment_data.from_account,
        "type": "payment_sent",
        "amount": payment_data.amount,
        "description": f"Payment to {to_account['account_number']}: {payment_data.description}",
        "recipient_account": payment_data.to_account,
        "status": "completed",
        "created_at": datetime.utcnow()
    }
    
    credit_transaction = {
        "id": str(uuid.uuid4()),
        "account_id": payment_data.to_account,
        "type": "payment_received",
        "amount": payment_data.amount,
        "description": f"Payment from {from_account['account_number']}: {payment_data.description}",
        "recipient_account": payment_data.from_account,
        "status": "completed",
        "created_at": datetime.utcnow()
    }
    
    transactions_db[debit_transaction["id"]] = debit_transaction
    transactions_db[credit_transaction["id"]] = credit_transaction
    payments_db[payment_id] = payment
    
    return Payment(**payment)

@app.get("/api/payments/{payment_id}", response_model=Payment)
async def get_payment(payment_id: str, current_user: dict = Depends(get_current_user)):
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check if user has access to this payment
    from_account = accounts_db.get(payment["from_account"])
    to_account = accounts_db.get(payment["to_account"])
    
    if (not from_account or from_account["user_id"] != current_user["id"]) and \
       (not to_account or to_account["user_id"] != current_user["id"]):
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return Payment(**payment)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)