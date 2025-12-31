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
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# In-memory storage
users_db = {}
accounts_db = {}
transactions_db = {}
payment_methods_db = {}
sessions_db = {}

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

class PaymentMethodType(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"
    DIGITAL_WALLET = "digital_wallet"

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    created_at: datetime

class AccountCreate(BaseModel):
    account_type: AccountType
    initial_balance: Decimal = Decimal("0.00")

class AccountResponse(BaseModel):
    id: str
    user_id: str
    account_type: AccountType
    account_number: str
    balance: Decimal
    created_at: datetime
    is_active: bool

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
    payment_method_id: str

class TransactionResponse(BaseModel):
    id: str
    account_id: str
    transaction_type: TransactionType
    amount: Decimal
    description: Optional[str]
    status: TransactionStatus
    created_at: datetime
    reference_number: str

class PaymentMethodCreate(BaseModel):
    method_type: PaymentMethodType
    details: Dict[str, Any]
    is_default: bool = False

class PaymentMethodResponse(BaseModel):
    id: str
    user_id: str
    method_type: PaymentMethodType
    details: Dict[str, Any]
    is_default: bool
    created_at: datetime

class AnalyticsResponse(BaseModel):
    total_balance: Decimal
    monthly_income: Decimal
    monthly_expenses: Decimal
    account_summary: List[Dict[str, Any]]
    recent_transactions: List[TransactionResponse]

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {"user_id": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def generate_account_number() -> str:
    return f"ACC{uuid.uuid4().hex[:10].upper()}"

def generate_reference_number() -> str:
    return f"REF{uuid.uuid4().hex[:8].upper()}"

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
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

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Authentication endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    if any(u["email"] == user_data.email for u in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow()
    }
    users_db[user_id] = user
    
    return UserResponse(**{k: v for k, v in user.items() if k != "password"})

@app.post("/api/auth/login")
async def login(login_data: UserLogin):
    user = next((u for u in users_db.values() if u["email"] == login_data.email), None)
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user["id"])
    sessions_db[user["id"]] = {"token": token, "created_at": datetime.utcnow()}
    
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    sessions_db.pop(current_user["id"], None)
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    return UserResponse(**{k: v for k, v in current_user.items() if k != "password"})

# Account management endpoints
@app.post("/api/accounts", response_model=AccountResponse)
async def create_account(account_data: AccountCreate, current_user: dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    account = {
        "id": account_id,
        "user_id": current_user["id"],
        "account_type": account_data.account_type,
        "account_number": generate_account_number(),
        "balance": account_data.initial_balance,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    accounts_db[account_id] = account
    return AccountResponse(**account)

@app.get("/api/accounts", response_model=List[AccountResponse])
async def get_user_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db.values() if acc["user_id"] == current_user["id"]]
    return [AccountResponse(**acc) for acc in user_accounts]

@app.get("/api/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str, current_user: dict = Depends(get_current_user)):
    account = accounts_db.get(account_id)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountResponse(**account)

# Transaction endpoints
@app.post("/api/transactions/transfer", response_model=TransactionResponse)
async def transfer_funds(transfer_data: TransferRequest, current_user: dict = Depends(get_current_user)):
    from_account = accounts_db.get(transfer_data.from_account_id)
    to_account = accounts_db.get(transfer_data.to_account_id)
    
    if not from_account or from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Source account not found")
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    if from_account["balance"] < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Update balances
    accounts_db[transfer_data.from_account_id]["balance"] -= transfer_data.amount
    accounts_db[transfer_data.to_account_id]["balance"] += transfer_data.amount
    
    # Create transaction record
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "account_id": transfer_data.from_account_id,
        "transaction_type": TransactionType.TRANSFER,
        "amount": -transfer_data.amount,
        "description": transfer_data.description or f"Transfer to {to_account['account_number']}",
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "reference_number": generate_reference_number()
    }
    transactions_db[transaction_id] = transaction
    
    # Create corresponding credit transaction
    credit_transaction_id = str(uuid.uuid4())
    credit_transaction = {
        "id": credit_transaction_id,
        "account_id": transfer_data.to_account_id,
        "transaction_type": TransactionType.TRANSFER,
        "amount": transfer_data.amount,
        "description": f"Transfer from {from_account['account_number']}",
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "reference_number": transaction["reference_number"]
    }
    transactions_db[credit_transaction_id] = credit_transaction
    
    return TransactionResponse(**transaction)

@app.get("/api/transactions", response_model=List[TransactionResponse])
async def get_user_transactions(
    account_id: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    user_account_ids = {acc["id"] for acc in accounts_db.values() if acc["user_id"] == current_user["id"]}
    
    transactions = []
    for trans in transactions_db.values():
        if trans["account_id"] in user_account_ids:
            if not account_id or trans["account_id"] == account_id:
                transactions.append(trans)
    
    # Sort by created_at descending and limit
    transactions.sort(key=lambda x: x["created_at"], reverse=True)
    return [TransactionResponse(**trans) for trans in transactions[:limit]]

# Payment endpoints
@app.post("/api/payments/process", response_model=TransactionResponse)
async def process_payment(payment_data: PaymentRequest, current_user: dict = Depends(get_current_user)):
    account = accounts_db.get(payment_data.account_id)
    payment_method = payment_methods_db.get(payment_data.payment_method_id)
    
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Account not found")
    if not payment_method or payment_method["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Payment method not found")
    if account["balance"] < payment_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Process payment
    accounts_db[payment_data.account_id]["balance"] -= payment_data.amount
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "account_id": payment_data.account_id,
        "transaction_type": TransactionType.PAYMENT,
        "amount": -payment_data.amount,
        "description": payment_data.description or f"Payment to {payment_data.recipient}",
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow(),
        "reference_number": generate_reference_number()
    }
    transactions_db[transaction_id] = transaction
    
    return TransactionResponse(**transaction)

# Payment method endpoints
@app.post("/api/payment-methods", response_model=PaymentMethodResponse)
async def create_payment_method(method_data: PaymentMethodCreate, current_user: dict = Depends(get_current_user)):
    method_id = str(uuid.uuid4())
    payment_method = {
        "id": method_id,
        "user_id": current_user["id"],
        "method_type": method_data.method_type,
        "details": method_data.details,
        "is_default": method_data.is_default,
        "created_at": datetime.utcnow()
    }
    payment_methods_db[method_id] = payment_method
    return PaymentMethodResponse(**payment_method)

@app.get("/api/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(current_user: dict = Depends(get_current_user)):
    user_methods = [method for method in payment_methods_db.values() if method["user_id"] == current_user["id"]]
    return [PaymentMethodResponse(**method) for method in user_methods]

# Analytics endpoint
@app.get("/api/analytics", response_model=AnalyticsResponse)
async def get_analytics(current_user: dict = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db.values() if acc["user_id"] == current_user["id"]]
    user_account_ids = {acc["id"] for acc in user_accounts}
    
    total_balance = sum(acc["balance"] for acc in user_accounts)
    
    # Calculate monthly income and expenses
    current_month = datetime.utcnow().replace(day=1)
    monthly_income = Decimal("0.00")
    monthly_expenses = Decimal("0.00")
    
    recent_transactions = []
    for trans in transactions_db.values():
        if trans["account_id"] in user_account_ids:
            if trans["created_at"] >= current_month:
                if trans["amount"] > 0:
                    monthly_income += trans["amount"]
                else:
                    monthly_expenses += abs(trans["amount"])
            recent_transactions.append(trans)
    
    # Sort recent transactions and limit to 10
    recent_transactions.sort(key=lambda x: x["created_at"], reverse=True)
    recent_transactions = recent_transactions[:10]
    
    # Account summary
    account_summary = [
        {
            "account_type": acc["account_type"],
            "account_number": acc["account_number"],
            "balance": acc["balance"]
        }
        for acc in user_accounts
    ]
    
    return AnalyticsResponse(
        total_balance=total_balance,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        account_summary=account_summary,
        recent_transactions=[TransactionResponse(**trans) for trans in recent_transactions]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)