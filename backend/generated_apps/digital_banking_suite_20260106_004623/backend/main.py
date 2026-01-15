from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid
import hashlib
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
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PaymentStatus(str, Enum):
    SCHEDULED = "scheduled"
    PROCESSED = "processed"
    FAILED = "failed"

class UserRegister(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: str
    created_at: str

class Account(BaseModel):
    id: str
    user_id: str
    account_number: str
    account_type: AccountType
    balance: float
    currency: str
    created_at: str
    is_active: bool

class AccountCreate(BaseModel):
    account_type: AccountType
    currency: str = "USD"
    initial_deposit: float = 0.0

class Transaction(BaseModel):
    id: str
    account_id: str
    transaction_type: TransactionType
    amount: float
    balance_after: float
    description: str
    status: TransactionStatus
    created_at: str
    recipient_account_id: Optional[str] = None

class TransactionCreate(BaseModel):
    account_id: str
    transaction_type: TransactionType
    amount: float
    description: str
    recipient_account_id: Optional[str] = None

class Payment(BaseModel):
    id: str
    user_id: str
    from_account_id: str
    to_account_id: str
    amount: float
    description: str
    status: PaymentStatus
    scheduled_date: str
    processed_date: Optional[str] = None
    created_at: str

class PaymentCreate(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float
    description: str
    scheduled_date: Optional[str] = None

class AccountAnalytics(BaseModel):
    account_id: str
    total_deposits: float
    total_withdrawals: float
    total_transfers: float
    transaction_count: int
    average_transaction: float
    largest_transaction: float
    period_start: str
    period_end: str

class AuthToken(BaseModel):
    access_token: str
    token_type: str
    user: User

users_db = []
accounts_db = []
transactions_db = []
payments_db = []
sessions_db = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return str(uuid.uuid4())

def generate_account_number() -> str:
    return ''.join([str(uuid.uuid4().int)[:16]])

def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user_id = sessions_db.get(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)

users_db.extend([
    {
        "id": "user-1",
        "email": "john.doe@example.com",
        "password": hash_password("password123"),
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "created_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": "user-2",
        "email": "jane.smith@example.com",
        "password": hash_password("secure456"),
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "+1987654321",
        "created_at": "2024-02-20T14:30:00Z"
    },
    {
        "id": "user-3",
        "email": "bob.wilson@example.com",
        "password": hash_password("mypass789"),
        "first_name": "Bob",
        "last_name": "Wilson",
        "phone": "+1122334455",
        "created_at": "2024-03-10T09:15:00Z"
    }
])

accounts_db.extend([
    {
        "id": "acc-1",
        "user_id": "user-1",
        "account_number": "1234567890123456",
        "account_type": "checking",
        "balance": 5000.00,
        "currency": "USD",
        "created_at": "2024-01-15T10:05:00Z",
        "is_active": True
    },
    {
        "id": "acc-2",
        "user_id": "user-1",
        "account_number": "6543210987654321",
        "account_type": "savings",
        "balance": 15000.00,
        "currency": "USD",
        "created_at": "2024-01-15T10:10:00Z",
        "is_active": True
    },
    {
        "id": "acc-3",
        "user_id": "user-2",
        "account_number": "1111222233334444",
        "account_number": "1111222233334444",
        "account_type": "checking",
        "balance": 3500.00,
        "currency": "USD",
        "created_at": "2024-02-20T14:35:00Z",
        "is_active": True
    },
    {
        "id": "acc-4",
        "user_id": "user-3",
        "account_number": "9999888877776666",
        "account_type": "checking",
        "balance": 7200.00,
        "currency": "USD",
        "created_at": "2024-03-10T09:20:00Z",
        "is_active": True
    }
])

transactions_db.extend([
    {
        "id": "txn-1",
        "account_id": "acc-1",
        "transaction_type": "deposit",
        "amount": 1000.00,
        "balance_after": 5000.00,
        "description": "Salary deposit",
        "status": "completed",
        "created_at": "2024-01-20T08:00:00Z",
        "recipient_account_id": None
    },
    {
        "id": "txn-2",
        "account_id": "acc-1",
        "transaction_type": "withdrawal",
        "amount": 200.00,
        "balance_after": 4800.00,
        "description": "ATM withdrawal",
        "status": "completed",
        "created_at": "2024-01-22T14:30:00Z",
        "recipient_account_id": None
    },
    {
        "id": "txn-3",
        "account_id": "acc-2",
        "transaction_type": "deposit",
        "amount": 5000.00,
        "balance_after": 15000.00,
        "description": "Savings contribution",
        "status": "completed",
        "created_at": "2024-01-25T10:00:00Z",
        "recipient_account_id": None
    },
    {
        "id": "txn-4",
        "account_id": "acc-3",
        "transaction_type": "payment",
        "amount": 150.00,
        "balance_after": 3350.00,
        "description": "Utility bill payment",
        "status": "completed",
        "created_at": "2024-02-25T16:45:00Z",
        "recipient_account_id": None
    },
    {
        "id": "txn-5",
        "account_id": "acc-4",
        "transaction_type": "transfer",
        "amount": 500.00,
        "balance_after": 6700.00,
        "description": "Transfer to savings",
        "status": "completed",
        "created_at": "2024-03-15T11:20:00Z",
        "recipient_account_id": "acc-2"
    }
])

payments_db.extend([
    {
        "id": "pay-1",
        "user_id": "user-1",
        "from_account_id": "acc-1",
        "to_account_id": "acc-3",
        "amount": 250.00,
        "description": "Rent payment",
        "status": "processed",
        "scheduled_date": "2024-01-30T00:00:00Z",
        "processed_date": "2024-01-30T08:00:00Z",
        "created_at": "2024-01-28T15:00:00Z"
    },
    {
        "id": "pay-2",
        "user_id": "user-2",
        "from_account_id": "acc-3",
        "to_account_id": "acc-4",
        "amount": 100.00,
        "description": "Friend reimbursement",
        "status": "processed",
        "scheduled_date": "2024-03-01T00:00:00Z",
        "processed_date": "2024-03-01T09:30:00Z",
        "created_at": "2024-02-28T12:00:00Z"
    },
    {
        "id": "pay-3",
        "user_id": "user-1",
        "from_account_id": "acc-1",
        "to_account_id": "acc-4",
        "amount": 500.00,
        "description": "Monthly subscription",
        "status": "scheduled",
        "scheduled_date": "2024-12-25T00:00:00Z",
        "processed_date": None,
        "created_at": "2024-12-01T10:00:00Z"
    }
])

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Digital Banking Suite",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.post("/api/auth/register", response_model=AuthToken, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister):
    if any(u["email"] == user_data.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user-{uuid.uuid4()}"
    user = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    users_db.append(user)
    
    token = generate_token()
    sessions_db[token] = user_id
    
    user_response = User(**{k: v for k, v in user.items() if k != "password"})
    
    return AuthToken(
        access_token=token,
        token_type="bearer",
        user=user_response
    )

@app.post("/api/auth/login", response_model=AuthToken)
def login(credentials: UserLogin):
    user = next((u for u in users_db if u["email"] == credentials.email), None)
    
    if not user or user["password"] != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = generate_token()
    sessions_db[token] = user["id"]
    
    user_response = User(**{k: v for k, v in user.items() if k != "password"})
    
    return AuthToken(
        access_token=token,
        token_type="bearer",
        user=user_response
    )

@app.post("/api/auth/logout")
def logout(current_user: User = Depends(get_current_user), authorization: str = Header(None)):
    token = authorization.replace("Bearer ", "")
    if token in sessions_db:
        del sessions_db[token]
    return {"message": "Successfully logged out"}

@app.get("/api/auth/me", response_model=User)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/api/accounts", response_model=List[Account])
def get_accounts(current_user: User = Depends(get_current_user)):
    user_accounts = [Account(**acc) for acc in accounts_db if acc["user_id"] == current_user.id]
    return user_accounts

@app.get("/api/accounts/{account_id}", response_model=Account)
def get_account(account_id: str, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Account(**account)

@app.post("/api/accounts", response_model=Account, status_code=status.HTTP_201_CREATED)
def create_account(account_data: AccountCreate, current_user: User = Depends(get_current_user)):
    account_id = f"acc-{uuid.uuid4()}"
    account = {
        "id": account_id,
        "user_id": current_user.id,
        "account_number": generate_account_number(),
        "account_type": account_data.account_type.value,
        "balance": account_data.initial_deposit,
        "currency": account_data.currency,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "is_active": True
    }
    accounts_db.append(account)
    
    if account_data.initial_deposit > 0:
        transaction = {
            "id": f"txn-{uuid.uuid4()}",
            "account_id": account_id,
            "transaction_type": "deposit",
            "amount": account_data.initial_deposit,
            "balance_after": account_data.initial_deposit,
            "description": "Initial deposit",
            "status": "completed",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "recipient_account_id": None
        }
        transactions_db.append(transaction)
    
    return Account(**account)

@app.put("/api/accounts/{account_id}/deactivate", response_model=Account)
def deactivate_account(account_id: str, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account["is_active"] = False
    return Account(**account)

@app.get("/api/accounts/{account_id}/transactions", response_model=List[Transaction])
def get_account_transactions(account_id: str, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account_transactions = [
        Transaction(**txn) for txn in transactions_db 
        if txn["account_id"] == account_id
    ]
    return sorted(account_transactions, key=lambda x: x.created_at, reverse=True)

@app.post("/api/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(txn_data: TransactionCreate, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == txn_data.account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not account["is_active"]:
        raise HTTPException(status_code=400, detail="Account is not active")
    
    if txn_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if txn_data.transaction_type in ["withdrawal", "payment", "transfer"]:
        if account["balance"] < txn_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        new_balance = account["balance"] - txn_data.amount
    else:
        new_balance = account["balance"] + txn_data.amount
    
    if txn_data.transaction_type == "transfer":
        if not txn_data.recipient_account_id:
            raise HTTPException(status_code=400, detail="Recipient account required for transfer")
        
        recipient_account = next((acc for acc in accounts_db if acc["id"] == txn_data.recipient_account_id), None)
        if not recipient_account:
            raise HTTPException(status_code=404, detail="Recipient account not found")
        
        if not recipient_account["is_active"]:
            raise HTTPException(status_code=400, detail="Recipient account is not active")
        
        recipient_account["balance"] += txn_data.amount
        
        recipient_txn = {
            "id": f"txn-{uuid.uuid4()}",
            "account_id": txn_data.recipient_account_id,
            "transaction_type": "deposit",
            "amount": txn_data.amount,
            "balance_after": recipient_account["balance"],
            "description": f"Transfer from {account['account_number']}",
            "status": "completed",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "recipient_account_id": None
        }
        transactions_db.append(recipient_txn)
    
    account["balance"] = new_balance
    
    transaction = {
        "id": f"txn-{uuid.uuid4()}",
        "account_id": txn_data.account_id,
        "transaction_type": txn_data.transaction_type.value,
        "amount": txn_data.amount,
        "balance_after": new_balance,
        "description": txn_data.description,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "recipient_account_id": txn_data.recipient_account_id
    }
    transactions_db.append(transaction)
    
    return Transaction(**transaction)

@app.get("/api/transactions/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: str, current_user: User = Depends(get_current_user)):
    transaction = next((txn for txn in transactions_db if txn["id"] == transaction_id), None)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    account = next((acc for acc in accounts_db if acc["id"] == transaction["account_id"]), None)
    if not account or account["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Transaction(**transaction)

@app.get("/api/payments", response_model=List[Payment])
def get_payments(current_user: User = Depends(get_current_user)):
    user_payments = [
        Payment(**pay) for pay in payments_db 
        if pay["user_id"] == current_user.id
    ]
    return sorted(user_payments, key=lambda x: x.created_at, reverse=True)

@app.get("/api/payments/{payment_id}", response_model=Payment)
def get_payment(payment_id: str, current_user: User = Depends(get_current_user)):
    payment = next((pay for pay in payments_db if pay["id"] == payment_id), None)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Payment(**payment)

@app.post("/api/payments", response_model=Payment, status_code=status.HTTP_201_CREATED)
def create_payment(payment_data: PaymentCreate, current_user: User = Depends(get_current_user)):
    from_account = next((acc for acc in accounts_db if acc["id"] == payment_data.from_account_id), None)
    
    if not from_account:
        raise HTTPException(status_code=404, detail="Source account not found")
    
    if from_account["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    to_account = next((acc for acc in accounts_db if acc["id"] == payment_data.to_account_id), None)
    
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    
    if payment_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    scheduled_date = payment_data.scheduled_date if payment_data.scheduled_date else datetime.utcnow().isoformat() + "Z"
    
    payment = {
        "id": f"pay-{uuid.uuid4()}",
        "user_id": current_user.id,
        "from_account_id": payment_data.from_account_id,
        "to_account_id": payment_data.to_account_id,
        "amount": payment_data.amount,
        "description": payment_data.description,
        "status": "scheduled",
        "scheduled_date": scheduled_date,
        "processed_date": None,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    payments_db.append(payment)
    
    return Payment(**payment)

@app.post("/api/payments/{payment_id}/process", response_model=Payment)
def process_payment(payment_id: str, current_user: User = Depends(get_current_user)):
    payment = next((pay for pay in payments_db if pay["id"] == payment_id), None)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if payment["status"] != "scheduled":
        raise HTTPException(status_code=400, detail="Payment already processed or failed")
    
    from_account = next((acc for acc in accounts_db if acc["id"] == payment["from_account_id"]), None)
    to_account = next((acc for acc in accounts_db if acc["id"] == payment["to_account_id"]), None)
    
    if from_account["balance"] < payment["amount"]:
        payment["status"] = "failed"
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    from_account["balance"] -= payment["amount"]
    to_account["balance"] += payment["amount"]
    
    txn_from = {
        "id": f"txn-{uuid.uuid4()}",
        "account_id": payment["from_account_id"],
        "transaction_type": "payment",
        "amount": payment["amount"],
        "balance_after": from_account["balance"],
        "description": f"Payment: {payment['description']}",
        "status": "completed",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "recipient_account_id": payment["to_account_id"]
    }
    transactions_db.append(txn_from)
    
    txn_to = {
        "id": f"txn-{uuid.uuid4()}",
        "account_id": payment["to_account_id"],
        "transaction_type": "deposit",
        "amount": payment["amount"],
        "balance_after": to_account["balance"],
        "description": f"Payment received: {payment['description']}",
        "status": "completed",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "recipient_account_id": None
    }
    transactions_db.append(txn_to)
    
    payment["status"] = "processed"
    payment["processed_date"] = datetime.utcnow().isoformat() + "Z"
    
    return Payment(**payment)

@app.delete("/api/payments/{payment_id}")
def cancel_payment(payment_id: str, current_user: User = Depends(get_current_user)):
    payment = next((pay for pay in payments_db if pay["id"] == payment_id), None)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if payment["status"] != "scheduled":
        raise HTTPException(status_code=400, detail="Can only cancel scheduled payments")
    
    payments_db.remove(payment)
    return {"message": "Payment cancelled successfully"}

@app.get("/api/accounts/{account_id}/analytics", response_model=AccountAnalytics)
def get_account_analytics(account_id: str, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account_transactions = [txn for txn in transactions_db if txn["account_id"] == account_id]
    
    if not account_transactions:
        return AccountAnalytics(
            account_id=account_id,
            total_deposits=0.0,
            total_withdrawals=0.0,
            total_transfers=0.0,
            transaction_count=0,
            average_transaction=0.0,
            largest_transaction=0.0,
            period_start=datetime.utcnow().isoformat() + "Z",
            period_end=datetime.utcnow().isoformat() + "Z"
        )
    
    total_deposits = sum(txn["amount"] for txn in account_transactions if txn["transaction_type"] == "deposit")
    total_withdrawals = sum(txn["amount"] for txn in account_transactions if txn["transaction_type"] == "withdrawal")
    total_transfers = sum(txn["amount"] for txn in account_transactions if txn["transaction_type"] == "transfer")
    transaction_count = len(account_transactions)
    average_transaction = sum(txn["amount"] for txn in account_transactions) / transaction_count
    largest_transaction = max(txn["amount"] for txn in account_transactions)
    
    dates = [txn["created_at"] for txn in account_transactions]
    period_start = min(dates)
    period_end = max(dates)
    
    return AccountAnalytics(
        account_id=account_id,
        total_deposits=total_deposits,
        total_withdrawals=total_withdrawals,
        total_transfers=total_transfers,
        transaction_count=transaction_count,
        average_transaction=round(average_transaction, 2),
        largest_transaction=largest_transaction,
        period_start=period_start,
        period_end=period_end
    )

@app.get("/api/analytics/overview")
def get_user_analytics_overview(current_user: User = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == current_user.id]
    
    total_balance = sum(acc["balance"] for acc in user_accounts)
    active_accounts = sum(1 for acc in user_accounts if acc["is_active"])
    
    user_transactions = []
    for acc in user_accounts:
        user_transactions.extend([txn for txn in transactions_db if txn["account_id"] == acc["id"]])
    
    total_transactions = len(user_transactions)
    
    pending_payments = [pay for pay in payments_db if pay["user_id"] == current_user.id and pay["status"] == "scheduled"]
    
    return {
        "user_id": current_user.id,
        "total_balance": round(total_balance, 2),
        "total_accounts": len(user_accounts),
        "active_accounts": active_accounts,
        "total_transactions": total_transactions,
        "pending_payments": len(pending_payments),
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }