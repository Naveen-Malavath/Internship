from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import jwt
from passlib.context import CryptContext

app = FastAPI(title="Digital Banking Suite", version="1.0.0")

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
users_db: Dict[str, Dict] = {}
accounts_db: Dict[str, Dict] = {}
transactions_db: List[Dict] = []
payments_db: Dict[str, Dict] = {}

# Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

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
    balance: float
    currency: str
    created_at: datetime

class AccountCreate(BaseModel):
    account_type: str
    currency: str = "USD"

class Transaction(BaseModel):
    id: str
    from_account_id: str
    to_account_id: Optional[str] = None
    amount: float
    transaction_type: str
    description: str
    status: str
    created_at: datetime

class TransactionCreate(BaseModel):
    to_account_id: Optional[str] = None
    amount: float
    transaction_type: str
    description: str

class Payment(BaseModel):
    id: str
    from_account_id: str
    to_account_id: str
    amount: float
    currency: str
    status: str
    created_at: datetime

class PaymentCreate(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float
    currency: str = "USD"

class PaymentProcess(BaseModel):
    payment_id: str

class ApiResponse(BaseModel):
    data: Any
    status: str = "success"
    message: Optional[str] = None

# Utility functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
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

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Authentication endpoints
@app.post("/api/auth/register", response_model=ApiResponse)
async def register(user_data: UserRegister):
    if any(user["email"] == user_data.email for user in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    
    user = {
        "id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow()
    }
    
    users_db[user_id] = user
    
    return ApiResponse(
        data=User(**{k: v for k, v in user.items() if k != "password"}),
        message="User registered successfully"
    )

@app.post("/api/auth/login", response_model=ApiResponse)
async def login(credentials: UserLogin):
    user = next((u for u in users_db.values() if u["email"] == credentials.email), None)
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["id"]})
    
    return ApiResponse(
        data=Token(access_token=access_token, token_type="bearer"),
        message="Login successful"
    )

@app.get("/api/auth/me", response_model=ApiResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return ApiResponse(
        data=User(**{k: v for k, v in current_user.items() if k != "password"})
    )

# Account endpoints
@app.get("/api/accounts", response_model=ApiResponse)
async def get_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db.values() if acc["user_id"] == current_user["id"]]
    return ApiResponse(data=[Account(**acc) for acc in user_accounts])

@app.post("/api/accounts", response_model=ApiResponse)
async def create_account(account_data: AccountCreate, current_user: dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    account_number = f"ACC{str(uuid.uuid4().int)[:10]}"
    
    account = {
        "id": account_id,
        "user_id": current_user["id"],
        "account_number": account_number,
        "account_type": account_data.account_type,
        "balance": 0.0,
        "currency": account_data.currency,
        "created_at": datetime.utcnow()
    }
    
    accounts_db[account_id] = account
    
    return ApiResponse(
        data=Account(**account),
        message="Account created successfully"
    )

@app.get("/api/accounts/{account_id}", response_model=ApiResponse)
async def get_account(account_id: str, current_user: dict = Depends(get_current_user)):
    account = accounts_db.get(account_id)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return ApiResponse(data=Account(**account))

# Transaction endpoints
@app.get("/api/transactions", response_model=ApiResponse)
async def get_transactions(current_user: dict = Depends(get_current_user)):
    user_account_ids = [acc_id for acc_id, acc in accounts_db.items() if acc["user_id"] == current_user["id"]]
    user_transactions = [
        txn for txn in transactions_db 
        if txn["from_account_id"] in user_account_ids or 
        (txn.get("to_account_id") and txn["to_account_id"] in user_account_ids)
    ]
    return ApiResponse(data=[Transaction(**txn) for txn in user_transactions])

@app.post("/api/transactions", response_model=ApiResponse)
async def create_transaction(
    transaction_data: TransactionCreate, 
    from_account_id: str,
    current_user: dict = Depends(get_current_user)
):
    from_account = accounts_db.get(from_account_id)
    if not from_account or from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="From account not found")
    
    if transaction_data.transaction_type in ["transfer", "payment"] and transaction_data.to_account_id:
        to_account = accounts_db.get(transaction_data.to_account_id)
        if not to_account:
            raise HTTPException(status_code=404, detail="To account not found")
        
        if from_account["balance"] < transaction_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        # Update balances
        accounts_db[from_account_id]["balance"] -= transaction_data.amount
        accounts_db[transaction_data.to_account_id]["balance"] += transaction_data.amount
    
    elif transaction_data.transaction_type == "deposit":
        accounts_db[from_account_id]["balance"] += transaction_data.amount
    
    elif transaction_data.transaction_type == "withdrawal":
        if from_account["balance"] < transaction_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        accounts_db[from_account_id]["balance"] -= transaction_data.amount
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "from_account_id": from_account_id,
        "to_account_id": transaction_data.to_account_id,
        "amount": transaction_data.amount,
        "transaction_type": transaction_data.transaction_type,
        "description": transaction_data.description,
        "status": "completed",
        "created_at": datetime.utcnow()
    }
    
    transactions_db.append(transaction)
    
    return ApiResponse(
        data=Transaction(**transaction),
        message="Transaction completed successfully"
    )

# Payment endpoints
@app.post("/api/payments", response_model=ApiResponse)
async def create_payment(payment_data: PaymentCreate, current_user: dict = Depends(get_current_user)):
    from_account = accounts_db.get(payment_data.from_account_id)
    if not from_account or from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="From account not found")
    
    to_account = accounts_db.get(payment_data.to_account_id)
    if not to_account:
        raise HTTPException(status_code=404, detail="To account not found")
    
    payment_id = str(uuid.uuid4())
    payment = {
        "id": payment_id,
        "from_account_id": payment_data.from_account_id,
        "to_account_id": payment_data.to_account_id,
        "amount": payment_data.amount,
        "currency": payment_data.currency,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    payments_db[payment_id] = payment
    
    return ApiResponse(
        data=Payment(**payment),
        message="Payment created successfully"
    )

@app.post("/api/payments/process", response_model=ApiResponse)
async def process_payment(payment_process: PaymentProcess, current_user: dict = Depends(get_current_user)):
    payment = payments_db.get(payment_process.payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    from_account = accounts_db.get(payment["from_account_id"])
    if not from_account or from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    if payment["status"] != "pending":
        raise HTTPException(status_code=400, detail="Payment already processed")
    
    if from_account["balance"] < payment["amount"]:
        payments_db[payment_process.payment_id]["status"] = "failed"
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Process payment
    accounts_db[payment["from_account_id"]]["balance"] -= payment["amount"]
    accounts_db[payment["to_account_id"]]["balance"] += payment["amount"]
    payments_db[payment_process.payment_id]["status"] = "completed"
    
    # Create transaction record
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "from_account_id": payment["from_account_id"],
        "to_account_id": payment["to_account_id"],
        "amount": payment["amount"],
        "transaction_type": "payment",
        "description": f"Payment {payment['id']}",
        "status": "completed",
        "created_at": datetime.utcnow()
    }
    transactions_db.append(transaction)
    
    return ApiResponse(
        data=Payment(**payments_db[payment_process.payment_id]),
        message="Payment processed successfully"
    )

@app.get("/api/payments/{payment_id}/status", response_model=ApiResponse)
async def get_payment_status(payment_id: str, current_user: dict = Depends(get_current_user)):
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    from_account = accounts_db.get(payment["from_account_id"])
    if not from_account or from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return ApiResponse(data={"status": payment["status"], "payment_id": payment_id})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)