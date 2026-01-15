from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import hashlib
import secrets
from enum import Enum

app = FastAPI(title="Digital Banking Suite", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"

class TransactionType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    TRANSFER = "transfer"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: str
    is_active: bool

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class Account(BaseModel):
    id: int
    user_id: int
    account_number: str
    account_type: AccountType
    balance: float
    currency: str
    created_at: str
    is_active: bool

class AccountCreate(BaseModel):
    account_type: AccountType
    currency: str = "USD"

class Transaction(BaseModel):
    id: int
    account_id: int
    transaction_type: TransactionType
    amount: float
    currency: str
    description: str
    status: TransactionStatus
    created_at: str
    balance_after: float

class TransactionCreate(BaseModel):
    account_id: int
    transaction_type: TransactionType
    amount: float
    description: str

class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float
    description: str

class Beneficiary(BaseModel):
    id: int
    user_id: int
    name: str
    account_number: str
    bank_name: str
    created_at: str

class BeneficiaryCreate(BaseModel):
    name: str
    account_number: str
    bank_name: str

class PaymentRequest(BaseModel):
    account_id: int
    beneficiary_id: int
    amount: float
    description: str

class Payment(BaseModel):
    id: int
    account_id: int
    beneficiary_id: int
    amount: float
    description: str
    status: TransactionStatus
    created_at: str
    reference_number: str

class Analytics(BaseModel):
    total_accounts: int
    total_balance: float
    total_transactions: int
    monthly_spending: float
    monthly_income: float
    account_breakdown: List[Dict]
    recent_transactions: List[Transaction]

users_db = []
accounts_db = []
transactions_db = []
beneficiaries_db = []
payments_db = []
sessions_db = {}

user_id_counter = 1
account_id_counter = 1
transaction_id_counter = 1
beneficiary_id_counter = 1
payment_id_counter = 1

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_account_number() -> str:
    return f"{secrets.randbelow(9000000000) + 1000000000}"

def generate_token() -> str:
    return secrets.token_urlsafe(32)

def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user_id = sessions_db.get(token)
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return User(**user)

seed_user_1_password = hash_password("password123")
seed_user_2_password = hash_password("securepass456")
seed_user_3_password = hash_password("bankpass789")

users_db.extend([
    {
        "id": 1,
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "password": seed_user_1_password,
        "created_at": "2024-01-15T10:30:00",
        "is_active": True
    },
    {
        "id": 2,
        "email": "jane.smith@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "+1234567891",
        "password": seed_user_2_password,
        "created_at": "2024-02-20T14:20:00",
        "is_active": True
    },
    {
        "id": 3,
        "email": "bob.wilson@example.com",
        "first_name": "Bob",
        "last_name": "Wilson",
        "phone": "+1234567892",
        "password": seed_user_3_password,
        "created_at": "2024-03-10T09:15:00",
        "is_active": True
    }
])
user_id_counter = 4

accounts_db.extend([
    {
        "id": 1,
        "user_id": 1,
        "account_number": "1234567890",
        "account_type": "checking",
        "balance": 5000.00,
        "currency": "USD",
        "created_at": "2024-01-15T10:35:00",
        "is_active": True
    },
    {
        "id": 2,
        "user_id": 1,
        "account_number": "1234567891",
        "account_type": "savings",
        "balance": 15000.00,
        "currency": "USD",
        "created_at": "2024-01-15T10:36:00",
        "is_active": True
    },
    {
        "id": 3,
        "user_id": 2,
        "account_number": "2345678901",
        "account_type": "checking",
        "balance": 3500.00,
        "currency": "USD",
        "created_at": "2024-02-20T14:25:00",
        "is_active": True
    },
    {
        "id": 4,
        "user_id": 3,
        "account_number": "3456789012",
        "account_type": "checking",
        "balance": 7200.00,
        "currency": "USD",
        "created_at": "2024-03-10T09:20:00",
        "is_active": True
    }
])
account_id_counter = 5

transactions_db.extend([
    {
        "id": 1,
        "account_id": 1,
        "transaction_type": "credit",
        "amount": 2000.00,
        "currency": "USD",
        "description": "Salary deposit",
        "status": "completed",
        "created_at": "2024-01-20T09:00:00",
        "balance_after": 5000.00
    },
    {
        "id": 2,
        "account_id": 1,
        "transaction_type": "debit",
        "amount": 150.00,
        "currency": "USD",
        "description": "Grocery shopping",
        "status": "completed",
        "created_at": "2024-01-22T15:30:00",
        "balance_after": 4850.00
    },
    {
        "id": 3,
        "account_id": 2,
        "transaction_type": "credit",
        "amount": 5000.00,
        "currency": "USD",
        "description": "Initial deposit",
        "status": "completed",
        "created_at": "2024-01-15T10:40:00",
        "balance_after": 5000.00
    },
    {
        "id": 4,
        "account_id": 3,
        "transaction_type": "credit",
        "amount": 3000.00,
        "currency": "USD",
        "description": "Freelance payment",
        "status": "completed",
        "created_at": "2024-02-25T11:00:00",
        "balance_after": 3500.00
    },
    {
        "id": 5,
        "account_id": 4,
        "transaction_type": "debit",
        "amount": 800.00,
        "currency": "USD",
        "description": "Rent payment",
        "status": "completed",
        "created_at": "2024-03-15T10:00:00",
        "balance_after": 6400.00
    }
])
transaction_id_counter = 6

beneficiaries_db.extend([
    {
        "id": 1,
        "user_id": 1,
        "name": "Electric Company",
        "account_number": "9876543210",
        "bank_name": "Utility Bank",
        "created_at": "2024-01-16T10:00:00"
    },
    {
        "id": 2,
        "user_id": 1,
        "name": "Jane Smith",
        "account_number": "2345678901",
        "bank_name": "Same Bank",
        "created_at": "2024-01-18T14:00:00"
    },
    {
        "id": 3,
        "user_id": 2,
        "name": "Landlord Services",
        "account_number": "5555555555",
        "bank_name": "Property Bank",
        "created_at": "2024-02-21T09:00:00"
    }
])
beneficiary_id_counter = 4

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Digital Banking Suite",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    global user_id_counter
    
    if any(u["email"] == user_data.email for u in users_db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    new_user = {
        "id": user_id_counter,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "password": hash_password(user_data.password),
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    
    users_db.append(new_user)
    user_id_counter += 1
    
    return User(**{k: v for k, v in new_user.items() if k != "password"})

@app.post("/api/auth/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    user = next((u for u in users_db if u["email"] == credentials.email), None)
    
    if not user or user["password"] != hash_password(credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    
    token = generate_token()
    sessions_db[token] = user["id"]
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=User(**{k: v for k, v in user.items() if k != "password"})
    )

@app.post("/api/auth/logout")
def logout(current_user: User = Depends(get_current_user), authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        sessions_db.pop(token, None)
    
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me", response_model=User)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/api/accounts", response_model=List[Account])
def get_accounts(current_user: User = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == current_user.id]
    return [Account(**acc) for acc in user_accounts]

@app.post("/api/accounts", response_model=Account, status_code=status.HTTP_201_CREATED)
def create_account(account_data: AccountCreate, current_user: User = Depends(get_current_user)):
    global account_id_counter
    
    new_account = {
        "id": account_id_counter,
        "user_id": current_user.id,
        "account_number": generate_account_number(),
        "account_type": account_data.account_type.value,
        "balance": 0.0,
        "currency": account_data.currency,
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    
    accounts_db.append(new_account)
    account_id_counter += 1
    
    return Account(**new_account)

@app.get("/api/accounts/{account_id}", response_model=Account)
def get_account(account_id: int, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    if account["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return Account(**account)

@app.get("/api/accounts/{account_id}/transactions", response_model=List[Transaction])
def get_account_transactions(account_id: int, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    if account["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    account_transactions = [txn for txn in transactions_db if txn["account_id"] == account_id]
    account_transactions.sort(key=lambda x: x["created_at"], reverse=True)
    
    return [Transaction(**txn) for txn in account_transactions]

@app.post("/api/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionCreate, current_user: User = Depends(get_current_user)):
    global transaction_id_counter
    
    account = next((acc for acc in accounts_db if acc["id"] == transaction_data.account_id), None)
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    if account["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if transaction_data.transaction_type == TransactionType.DEBIT:
        if account["balance"] < transaction_data.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
        account["balance"] -= transaction_data.amount
    else:
        account["balance"] += transaction_data.amount
    
    new_transaction = {
        "id": transaction_id_counter,
        "account_id": transaction_data.account_id,
        "transaction_type": transaction_data.transaction_type.value,
        "amount": transaction_data.amount,
        "currency": account["currency"],
        "description": transaction_data.description,
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "balance_after": account["balance"]
    }
    
    transactions_db.append(new_transaction)
    transaction_id_counter += 1
    
    return Transaction(**new_transaction)

@app.post("/api/transfers", response_model=Dict, status_code=status.HTTP_201_CREATED)
def transfer_funds(transfer_data: TransferRequest, current_user: User = Depends(get_current_user)):
    global transaction_id_counter
    
    from_account = next((acc for acc in accounts_db if acc["id"] == transfer_data.from_account_id), None)
    to_account = next((acc for acc in accounts_db if acc["id"] == transfer_data.to_account_id), None)
    
    if not from_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source account not found")
    
    if not to_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination account not found")
    
    if from_account["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if from_account["balance"] < transfer_data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
    
    if transfer_data.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid amount")
    
    from_account["balance"] -= transfer_data.amount
    to_account["balance"] += transfer_data.amount
    
    debit_transaction = {
        "id": transaction_id_counter,
        "account_id": transfer_data.from_account_id,
        "transaction_type": "transfer",
        "amount": transfer_data.amount,
        "currency": from_account["currency"],
        "description": f"Transfer to {to_account['account_number']}: {transfer_data.description}",
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "balance_after": from_account["balance"]
    }
    transactions_db.append(debit_transaction)
    transaction_id_counter += 1
    
    credit_transaction = {
        "id": transaction_id_counter,
        "account_id": transfer_data.to_account_id,
        "transaction_type": "transfer",
        "amount": transfer_data.amount,
        "currency": to_account["currency"],
        "description": f"Transfer from {from_account['account_number']}: {transfer_data.description}",
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "balance_after": to_account["balance"]
    }
    transactions_db.append(credit_transaction)
    transaction_id_counter += 1
    
    return {
        "message": "Transfer completed successfully",
        "from_account": from_account["account_number"],
        "to_account": to_account["account_number"],
        "amount": transfer_data.amount,
        "debit_transaction": Transaction(**debit_transaction),
        "credit_transaction": Transaction(**credit_transaction)
    }

@app.get("/api/beneficiaries", response_model=List[Beneficiary])
def get_beneficiaries(current_user: User = Depends(get_current_user)):
    user_beneficiaries = [ben for ben in beneficiaries_db if ben["user_id"] == current_user.id]
    return [Beneficiary(**ben) for ben in user_beneficiaries]

@app.post("/api/beneficiaries", response_model=Beneficiary, status_code=status.HTTP_201_CREATED)
def create_beneficiary(beneficiary_data: BeneficiaryCreate, current_user: User = Depends(get_current_user)):
    global beneficiary_id_counter
    
    new_beneficiary = {
        "id": beneficiary_id_counter,
        "user_id": current_user.id,
        "name": beneficiary_data.name,
        "account_number": beneficiary_data.account_number,
        "bank_name": beneficiary_data.bank_name,
        "created_at": datetime.now().isoformat()
    }
    
    beneficiaries_db.append(new_beneficiary)
    beneficiary_id_counter += 1
    
    return Beneficiary(**new_beneficiary)

@app.delete("/api/beneficiaries/{beneficiary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_beneficiary(beneficiary_id: int, current_user: User = Depends(get_current_user)):
    beneficiary = next((ben for ben in beneficiaries_db if ben["id"] == beneficiary_id), None)
    
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")
    
    if beneficiary["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    beneficiaries_db.remove(beneficiary)
    return None

@app.post("/api/payments", response_model=Payment, status_code=status.HTTP_201_CREATED)
def process_payment(payment_data: PaymentRequest, current_user: User = Depends(get_current_user)):
    global payment_id_counter, transaction_id_counter
    
    account = next((acc for acc in accounts_db if acc["id"] == payment_data.account_id), None)
    beneficiary = next((ben for ben in beneficiaries_db if ben["id"] == payment_data.beneficiary_id), None)
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")
    
    if account["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if beneficiary["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Beneficiary access denied")
    
    if account["balance"] < payment_data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
    
    if payment_data.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid amount")
    
    account["balance"] -= payment_data.amount
    
    reference_number = f"PAY{payment_id_counter}{secrets.randbelow(10000):04d}"
    
    new_payment = {
        "id": payment_id_counter,
        "account_id": payment_data.account_id,
        "beneficiary_id": payment_data.beneficiary_id,
        "amount": payment_data.amount,
        "description": payment_data.description,
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "reference_number": reference_number
    }
    
    payments_db.append(new_payment)
    payment_id_counter += 1
    
    new_transaction = {
        "id": transaction_id_counter,
        "account_id": payment_data.account_id,
        "transaction_type": "debit",
        "amount": payment_data.amount,
        "currency": account["currency"],
        "description": f"Payment to {beneficiary['name']}: {payment_data.description}",
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "balance_after": account["balance"]
    }
    
    transactions_db.append(new_transaction)
    transaction_id_counter += 1
    
    return Payment(**new_payment)

@app.get("/api/payments", response_model=List[Payment])
def get_payments(current_user: User = Depends(get_current_user)):
    user_account_ids = [acc["id"] for acc in accounts_db if acc["user_id"] == current_user.id]
    user_payments = [pay for pay in payments_db if pay["account_id"] in user_account_ids]
    user_payments.sort(key=lambda x: x["created_at"], reverse=True)
    
    return [Payment(**pay) for pay in user_payments]

@app.get("/api/payments/{payment_id}", response_model=Payment)
def get_payment(payment_id: int, current_user: User = Depends(get_current_user)):
    payment = next((pay for pay in payments_db if pay["id"] == payment_id), None)
    
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    account = next((acc for acc in accounts_db if acc["id"] == payment["account_id"]), None)
    
    if not account or account["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return Payment(**payment)

@app.get("/api/analytics", response_model=Analytics)
def get_analytics(current_user: User = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == current_user.id]
    user_account_ids = [acc["id"] for acc in user_accounts]
    
    total_accounts = len(user_accounts)
    total_balance = sum(acc["balance"] for acc in user_accounts)
    
    user_transactions = [txn for txn in transactions_db if txn["account_id"] in user_account_ids]
    total_transactions = len(user_transactions)
    
    now = datetime.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_transactions = [
        txn for txn in user_transactions 
        if datetime.fromisoformat(txn["created_at"]) >= first_day_of_month
    ]
    
    monthly_spending = sum(
        txn["amount"] for txn in monthly_transactions 
        if txn["transaction_type"] in ["debit", "transfer"] and txn["account_id"] in user_account_ids
    )
    
    monthly_income = sum(
        txn["amount"] for txn in monthly_transactions 
        if txn["transaction_type"] == "credit"
    )
    
    account_breakdown = [
        {
            "account_number": acc["account_number"],
            "account_type": acc["account_type"],
            "balance": acc["balance"],
            "currency": acc["currency"]
        }
        for acc in user_accounts
    ]
    
    recent_transactions = sorted(user_transactions, key=lambda x: x["created_at"], reverse=True)[:10]
    
    return Analytics(
        total_accounts=total_accounts,
        total_balance=total_balance,
        total_transactions=total_transactions,
        monthly_spending=monthly_spending,
        monthly_income=monthly_income,
        account_breakdown=account_breakdown,
        recent_transactions=[Transaction(**txn) for txn in recent_transactions]
    )

@app.get("/api/dashboard")
def get_dashboard(current_user: User = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == current_user.id]
    user_account_ids = [acc["id"] for acc in user_accounts]
    
    recent_transactions = [
        txn for txn in transactions_db 
        if txn["account_id"] in user_account_ids
    ]
    recent_transactions.sort(key=lambda x: x["created_at"], reverse=True)
    recent_transactions = recent_transactions[:5]
    
    total_balance = sum(acc["balance"] for acc in user_accounts)
    
    return {
        "user": {
            "id": current_user.id,
            "name": f"{current_user.first_name} {current_user.last_name}",
            "email": current_user.email
        },
        "summary": {
            "total_balance": total_balance,
            "account_count": len(user_accounts),
            "currency": "USD"
        },
        "accounts": [Account(**acc) for acc in user_accounts],
        "recent_transactions": [Transaction(**txn) for txn in recent_transactions]
    }