from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from uuid import uuid4
import hashlib
import secrets

app = FastAPI(title="Digital Banking Suite", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: str
    email: str
    full_name: str
    phone: str
    created_at: str
    account_status: str

class Account(BaseModel):
    id: str
    user_id: str
    account_number: str
    account_type: str
    balance: float
    currency: str
    created_at: str
    status: str

class Transaction(BaseModel):
    id: str
    account_id: str
    transaction_type: str
    amount: float
    description: str
    timestamp: str
    balance_after: float
    status: str

class TransactionCreate(BaseModel):
    account_id: str
    transaction_type: str
    amount: float
    description: str

class Transfer(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float
    description: Optional[str] = None

class Beneficiary(BaseModel):
    id: str
    user_id: str
    name: str
    account_number: str
    bank_name: str
    created_at: str

class BeneficiaryCreate(BaseModel):
    name: str
    account_number: str
    bank_name: str

class PaymentRequest(BaseModel):
    account_id: str
    recipient: str
    amount: float
    payment_type: str
    description: Optional[str] = None

class Payment(BaseModel):
    id: str
    account_id: str
    recipient: str
    amount: float
    payment_type: str
    description: Optional[str] = None
    status: str
    created_at: str
    completed_at: Optional[str] = None

class AccountAnalytics(BaseModel):
    account_id: str
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int
    average_transaction: float
    period_start: str
    period_end: str

class AuthToken(BaseModel):
    access_token: str
    token_type: str
    expires_at: str

# In-memory storage
users_db: List[Dict] = []
accounts_db: List[Dict] = []
transactions_db: List[Dict] = []
beneficiaries_db: List[Dict] = []
payments_db: List[Dict] = []
tokens_db: Dict[str, Dict] = {}

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_account_number() -> str:
    return ''.join([str(secrets.randbelow(10)) for _ in range(12)])

def create_token(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    tokens_db[token] = {
        "user_id": user_id,
        "expires_at": expires_at.isoformat()
    }
    return token

def verify_token(token: str) -> Optional[str]:
    if token not in tokens_db:
        return None
    token_data = tokens_db[token]
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if datetime.utcnow() > expires_at:
        del tokens_db[token]
        return None
    return token_data["user_id"]

def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user_id

# Seed data
seed_user_1_id = str(uuid4())
seed_user_2_id = str(uuid4())

users_db.extend([
    {
        "id": seed_user_1_id,
        "email": "john.doe@example.com",
        "password": hash_password("password123"),
        "full_name": "John Doe",
        "phone": "+1234567890",
        "created_at": datetime.utcnow().isoformat(),
        "account_status": "active"
    },
    {
        "id": seed_user_2_id,
        "email": "jane.smith@example.com",
        "password": hash_password("password456"),
        "full_name": "Jane Smith",
        "phone": "+1987654321",
        "created_at": datetime.utcnow().isoformat(),
        "account_status": "active"
    }
])

seed_account_1_id = str(uuid4())
seed_account_2_id = str(uuid4())
seed_account_3_id = str(uuid4())

accounts_db.extend([
    {
        "id": seed_account_1_id,
        "user_id": seed_user_1_id,
        "account_number": "123456789012",
        "account_type": "checking",
        "balance": 5000.00,
        "currency": "USD",
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    },
    {
        "id": seed_account_2_id,
        "user_id": seed_user_1_id,
        "account_number": "123456789013",
        "account_type": "savings",
        "balance": 15000.00,
        "currency": "USD",
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    },
    {
        "id": seed_account_3_id,
        "user_id": seed_user_2_id,
        "account_number": "987654321098",
        "account_type": "checking",
        "balance": 3500.50,
        "currency": "USD",
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    }
])

transactions_db.extend([
    {
        "id": str(uuid4()),
        "account_id": seed_account_1_id,
        "transaction_type": "deposit",
        "amount": 1000.00,
        "description": "Salary deposit",
        "timestamp": (datetime.utcnow() - timedelta(days=5)).isoformat(),
        "balance_after": 5000.00,
        "status": "completed"
    },
    {
        "id": str(uuid4()),
        "account_id": seed_account_1_id,
        "transaction_type": "withdrawal",
        "amount": 200.00,
        "description": "ATM withdrawal",
        "timestamp": (datetime.utcnow() - timedelta(days=3)).isoformat(),
        "balance_after": 4800.00,
        "status": "completed"
    },
    {
        "id": str(uuid4()),
        "account_id": seed_account_2_id,
        "transaction_type": "deposit",
        "amount": 5000.00,
        "description": "Transfer from checking",
        "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat(),
        "balance_after": 15000.00,
        "status": "completed"
    }
])

beneficiaries_db.extend([
    {
        "id": str(uuid4()),
        "user_id": seed_user_1_id,
        "name": "Electric Company",
        "account_number": "555666777888",
        "bank_name": "Utility Bank",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid4()),
        "user_id": seed_user_1_id,
        "name": "Jane Smith",
        "account_number": "987654321098",
        "bank_name": "Same Bank",
        "created_at": datetime.utcnow().isoformat()
    }
])

# Endpoints
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Digital Banking Suite",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister):
    existing_user = next((u for u in users_db if u["email"] == user_data.email), None)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user_id = str(uuid4())
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow().isoformat(),
        "account_status": "active"
    }
    users_db.append(new_user)
    
    new_account = {
        "id": str(uuid4()),
        "user_id": user_id,
        "account_number": generate_account_number(),
        "account_type": "checking",
        "balance": 0.0,
        "currency": "USD",
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    }
    accounts_db.append(new_account)
    
    return User(**{k: v for k, v in new_user.items() if k != "password"})

@app.post("/api/auth/login", response_model=AuthToken)
def login_user(credentials: UserLogin):
    user = next((u for u in users_db if u["email"] == credentials.email), None)
    if not user or user["password"] != hash_password(credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = create_token(user["id"])
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    return AuthToken(
        access_token=token,
        token_type="bearer",
        expires_at=expires_at.isoformat()
    )

@app.get("/api/auth/me", response_model=User)
def get_current_user_info(user_id: str = Depends(get_current_user)):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return User(**{k: v for k, v in user.items() if k != "password"})

@app.post("/api/auth/logout")
def logout_user(user_id: str = Depends(get_current_user), authorization: Optional[str] = Header(None)):
    token = authorization.replace("Bearer ", "")
    if token in tokens_db:
        del tokens_db[token]
    return {"message": "Successfully logged out"}

@app.get("/api/accounts", response_model=List[Account])
def get_user_accounts(user_id: str = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == user_id]
    return [Account(**acc) for acc in user_accounts]

@app.get("/api/accounts/{account_id}", response_model=Account)
def get_account(account_id: str, user_id: str = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    if account["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return Account(**account)

@app.get("/api/accounts/{account_id}/transactions", response_model=List[Transaction])
def get_account_transactions(account_id: str, user_id: str = Depends(get_current_user), limit: int = 50):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    if account["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    account_transactions = [t for t in transactions_db if t["account_id"] == account_id]
    account_transactions.sort(key=lambda x: x["timestamp"], reverse=True)
    return [Transaction(**t) for t in account_transactions[:limit]]

@app.post("/api/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionCreate, user_id: str = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == transaction_data.account_id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    if account["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if transaction_data.transaction_type == "withdrawal" and account["balance"] < transaction_data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
    
    if transaction_data.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    
    if transaction_data.transaction_type == "deposit":
        account["balance"] += transaction_data.amount
    elif transaction_data.transaction_type == "withdrawal":
        account["balance"] -= transaction_data.amount
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid transaction type")
    
    new_transaction = {
        "id": str(uuid4()),
        "account_id": transaction_data.account_id,
        "transaction_type": transaction_data.transaction_type,
        "amount": transaction_data.amount,
        "description": transaction_data.description,
        "timestamp": datetime.utcnow().isoformat(),
        "balance_after": account["balance"],
        "status": "completed"
    }
    transactions_db.append(new_transaction)
    
    return Transaction(**new_transaction)

@app.post("/api/transfers", response_model=Dict, status_code=status.HTTP_201_CREATED)
def create_transfer(transfer_data: Transfer, user_id: str = Depends(get_current_user)):
    from_account = next((acc for acc in accounts_db if acc["id"] == transfer_data.from_account_id), None)
    to_account = next((acc for acc in accounts_db if acc["id"] == transfer_data.to_account_id), None)
    
    if not from_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source account not found")
    if not to_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination account not found")
    if from_account["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if from_account["balance"] < transfer_data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
    if transfer_data.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    
    from_account["balance"] -= transfer_data.amount
    to_account["balance"] += transfer_data.amount
    
    debit_transaction = {
        "id": str(uuid4()),
        "account_id": transfer_data.from_account_id,
        "transaction_type": "transfer_out",
        "amount": transfer_data.amount,
        "description": f"Transfer to {to_account['account_number']}: {transfer_data.description or 'No description'}",
        "timestamp": datetime.utcnow().isoformat(),
        "balance_after": from_account["balance"],
        "status": "completed"
    }
    
    credit_transaction = {
        "id": str(uuid4()),
        "account_id": transfer_data.to_account_id,
        "transaction_type": "transfer_in",
        "amount": transfer_data.amount,
        "description": f"Transfer from {from_account['account_number']}: {transfer_data.description or 'No description'}",
        "timestamp": datetime.utcnow().isoformat(),
        "balance_after": to_account["balance"],
        "status": "completed"
    }
    
    transactions_db.append(debit_transaction)
    transactions_db.append(credit_transaction)
    
    return {
        "transfer_id": str(uuid4()),
        "from_account": from_account["account_number"],
        "to_account": to_account["account_number"],
        "amount": transfer_data.amount,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/beneficiaries", response_model=List[Beneficiary])
def get_beneficiaries(user_id: str = Depends(get_current_user)):
    user_beneficiaries = [b for b in beneficiaries_db if b["user_id"] == user_id]
    return [Beneficiary(**b) for b in user_beneficiaries]

@app.post("/api/beneficiaries", response_model=Beneficiary, status_code=status.HTTP_201_CREATED)
def create_beneficiary(beneficiary_data: BeneficiaryCreate, user_id: str = Depends(get_current_user)):
    new_beneficiary = {
        "id": str(uuid4()),
        "user_id": user_id,
        "name": beneficiary_data.name,
        "account_number": beneficiary_data.account_number,
        "bank_name": beneficiary_data.bank_name,
        "created_at": datetime.utcnow().isoformat()
    }
    beneficiaries_db.append(new_beneficiary)
    return Beneficiary(**new_beneficiary)

@app.delete("/api/beneficiaries/{beneficiary_id}")
def delete_beneficiary(beneficiary_id: str, user_id: str = Depends(get_current_user)):
    beneficiary = next((b for b in beneficiaries_db if b["id"] == beneficiary_id), None)
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")
    if beneficiary["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    beneficiaries_db.remove(beneficiary)
    return {"message": "Beneficiary deleted successfully"}

@app.post("/api/payments", response_model=Payment, status_code=status.HTTP_201_CREATED)
def create_payment(payment_data: PaymentRequest, user_id: str = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == payment_data.account_id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    if account["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if account["balance"] < payment_data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
    if payment_data.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    
    account["balance"] -= payment_data.amount
    
    new_payment = {
        "id": str(uuid4()),
        "account_id": payment_data.account_id,
        "recipient": payment_data.recipient,
        "amount": payment_data.amount,
        "payment_type": payment_data.payment_type,
        "description": payment_data.description,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat()
    }
    payments_db.append(new_payment)
    
    transaction = {
        "id": str(uuid4()),
        "account_id": payment_data.account_id,
        "transaction_type": "payment",
        "amount": payment_data.amount,
        "description": f"{payment_data.payment_type} payment to {payment_data.recipient}: {payment_data.description or 'No description'}",
        "timestamp": datetime.utcnow().isoformat(),
        "balance_after": account["balance"],
        "status": "completed"
    }
    transactions_db.append(transaction)
    
    return Payment(**new_payment)

@app.get("/api/payments", response_model=List[Payment])
def get_payments(user_id: str = Depends(get_current_user), limit: int = 50):
    user_accounts = [acc["id"] for acc in accounts_db if acc["user_id"] == user_id]
    user_payments = [p for p in payments_db if p["account_id"] in user_accounts]
    user_payments.sort(key=lambda x: x["created_at"], reverse=True)
    return [Payment(**p) for p in user_payments[:limit]]

@app.get("/api/payments/{payment_id}", response_model=Payment)
def get_payment(payment_id: str, user_id: str = Depends(get_current_user)):
    payment = next((p for p in payments_db if p["id"] == payment_id), None)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    account = next((acc for acc in accounts_db if acc["id"] == payment["account_id"]), None)
    if not account or account["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return Payment(**payment)

@app.get("/api/analytics/account/{account_id}", response_model=AccountAnalytics)
def get_account_analytics(account_id: str, user_id: str = Depends(get_current_user), days: int = 30):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    if account["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    period_start = datetime.utcnow() - timedelta(days=days)
    account_transactions = [
        t for t in transactions_db 
        if t["account_id"] == account_id and datetime.fromisoformat(t["timestamp"]) >= period_start
    ]
    
    total_income = sum(
        t["amount"] for t in account_transactions 
        if t["transaction_type"] in ["deposit", "transfer_in"]
    )
    total_expenses = sum(
        t["amount"] for t in account_transactions 
        if t["transaction_type"] in ["withdrawal", "transfer_out", "payment"]
    )
    transaction_count = len(account_transactions)
    average_transaction = (total_income + total_expenses) / transaction_count if transaction_count > 0 else 0.0
    
    return AccountAnalytics(
        account_id=account_id,
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=account["balance"],
        transaction_count=transaction_count,
        average_transaction=average_transaction,
        period_start=period_start.isoformat(),
        period_end=datetime.utcnow().isoformat()
    )

@app.get("/api/analytics/overview", response_model=Dict)
def get_user_overview(user_id: str = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == user_id]
    total_balance = sum(acc["balance"] for acc in user_accounts)
    
    user_account_ids = [acc["id"] for acc in user_accounts]
    recent_transactions = [
        t for t in transactions_db 
        if t["account_id"] in user_account_ids
    ]
    recent_transactions.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "user_id": user_id,
        "total_accounts": len(user_accounts),
        "total_balance": total_balance,
        "accounts": [Account(**acc) for acc in user_accounts],
        "recent_transactions": [Transaction(**t) for t in recent_transactions[:10]],
        "generated_at": datetime.utcnow().isoformat()
    }