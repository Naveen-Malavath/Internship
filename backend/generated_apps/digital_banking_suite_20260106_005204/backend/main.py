from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from enum import Enum
import uuid
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

# Models
class User(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: str
    created_at: str
    is_active: bool = True

class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str

class UserLogin(BaseModel):
    email: str
    password: str

class AuthToken(BaseModel):
    access_token: str
    token_type: str
    user: User

class Account(BaseModel):
    id: str
    user_id: str
    account_number: str
    account_type: AccountType
    balance: float
    currency: str
    nickname: Optional[str] = None
    created_at: str
    is_active: bool = True

class AccountCreate(BaseModel):
    account_type: AccountType
    nickname: Optional[str] = None
    initial_deposit: float = 0.0

class Transaction(BaseModel):
    id: str
    account_id: str
    transaction_type: TransactionType
    amount: float
    currency: str
    description: str
    status: TransactionStatus
    created_at: str
    to_account_id: Optional[str] = None
    reference_number: str

class TransactionCreate(BaseModel):
    account_id: str
    transaction_type: TransactionType
    amount: float
    description: str
    to_account_id: Optional[str] = None

class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float
    description: str

class PaymentRequest(BaseModel):
    account_id: str
    payee_name: str
    amount: float
    description: str

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

class Analytics(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int
    categories: Dict[str, float]

# In-memory storage
users_db = []
accounts_db = []
transactions_db = []
beneficiaries_db = []
sessions_db = {}
user_credentials = {}

# Utility functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def generate_token() -> str:
    return secrets.token_urlsafe(32)

def generate_account_number() -> str:
    return str(uuid.uuid4().int)[:12]

def generate_reference_number() -> str:
    return f"REF{uuid.uuid4().hex[:8].upper()}"

def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user_id = sessions_db.get(token)
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

# Seed data
seed_user_1_id = str(uuid.uuid4())
seed_user_2_id = str(uuid.uuid4())

users_db.extend([
    User(
        id=seed_user_1_id,
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
        created_at=datetime.now().isoformat(),
        is_active=True
    ),
    User(
        id=seed_user_2_id,
        email="jane.smith@example.com",
        first_name="Jane",
        last_name="Smith",
        phone="+1987654321",
        created_at=datetime.now().isoformat(),
        is_active=True
    )
])

user_credentials["john.doe@example.com"] = hash_password("password123")
user_credentials["jane.smith@example.com"] = hash_password("password456")

seed_account_1_id = str(uuid.uuid4())
seed_account_2_id = str(uuid.uuid4())
seed_account_3_id = str(uuid.uuid4())

accounts_db.extend([
    Account(
        id=seed_account_1_id,
        user_id=seed_user_1_id,
        account_number=generate_account_number(),
        account_type=AccountType.CHECKING,
        balance=15000.50,
        currency="USD",
        nickname="Main Checking",
        created_at=datetime.now().isoformat(),
        is_active=True
    ),
    Account(
        id=seed_account_2_id,
        user_id=seed_user_1_id,
        account_number=generate_account_number(),
        account_type=AccountType.SAVINGS,
        balance=50000.00,
        currency="USD",
        nickname="Emergency Fund",
        created_at=datetime.now().isoformat(),
        is_active=True
    ),
    Account(
        id=seed_account_3_id,
        user_id=seed_user_2_id,
        account_number=generate_account_number(),
        account_type=AccountType.CHECKING,
        balance=8500.75,
        currency="USD",
        nickname="Primary Account",
        created_at=datetime.now().isoformat(),
        is_active=True
    )
])

transactions_db.extend([
    Transaction(
        id=str(uuid.uuid4()),
        account_id=seed_account_1_id,
        transaction_type=TransactionType.DEPOSIT,
        amount=5000.00,
        currency="USD",
        description="Salary deposit",
        status=TransactionStatus.COMPLETED,
        created_at=(datetime.now() - timedelta(days=5)).isoformat(),
        reference_number=generate_reference_number()
    ),
    Transaction(
        id=str(uuid.uuid4()),
        account_id=seed_account_1_id,
        transaction_type=TransactionType.PAYMENT,
        amount=150.00,
        currency="USD",
        description="Electricity bill",
        status=TransactionStatus.COMPLETED,
        created_at=(datetime.now() - timedelta(days=3)).isoformat(),
        reference_number=generate_reference_number()
    ),
    Transaction(
        id=str(uuid.uuid4()),
        account_id=seed_account_2_id,
        transaction_type=TransactionType.DEPOSIT,
        amount=10000.00,
        currency="USD",
        description="Investment return",
        status=TransactionStatus.COMPLETED,
        created_at=(datetime.now() - timedelta(days=7)).isoformat(),
        reference_number=generate_reference_number()
    ),
    Transaction(
        id=str(uuid.uuid4()),
        account_id=seed_account_3_id,
        transaction_type=TransactionType.WITHDRAWAL,
        amount=200.00,
        currency="USD",
        description="ATM withdrawal",
        status=TransactionStatus.COMPLETED,
        created_at=(datetime.now() - timedelta(days=2)).isoformat(),
        reference_number=generate_reference_number()
    )
])

beneficiaries_db.extend([
    Beneficiary(
        id=str(uuid.uuid4()),
        user_id=seed_user_1_id,
        name="Alice Johnson",
        account_number="123456789012",
        bank_name="Chase Bank",
        created_at=datetime.now().isoformat()
    ),
    Beneficiary(
        id=str(uuid.uuid4()),
        user_id=seed_user_1_id,
        name="Bob Williams",
        account_number="987654321098",
        bank_name="Bank of America",
        created_at=datetime.now().isoformat()
    )
])

# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Digital Banking Suite"
    }

# Authentication endpoints
@app.post("/api/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    if any(u.email == user_data.email for u in users_db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        created_at=datetime.now().isoformat(),
        is_active=True
    )
    
    users_db.append(new_user)
    user_credentials[user_data.email] = hash_password(user_data.password)
    
    return new_user

@app.post("/api/auth/login", response_model=AuthToken)
def login(credentials: UserLogin):
    if credentials.email not in user_credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not verify_password(credentials.password, user_credentials[credentials.email]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    user = next((u for u in users_db if u.email == credentials.email), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    token = generate_token()
    sessions_db[token] = user.id
    
    return AuthToken(access_token=token, token_type="bearer", user=user)

@app.post("/api/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "")
        if token in sessions_db:
            del sessions_db[token]
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Account endpoints
@app.get("/api/accounts", response_model=List[Account])
def get_accounts(current_user: User = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc.user_id == current_user.id]
    return user_accounts

@app.get("/api/accounts/{account_id}", response_model=Account)
def get_account(account_id: str, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc.id == account_id and acc.user_id == current_user.id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account

@app.post("/api/accounts", response_model=Account, status_code=status.HTTP_201_CREATED)
def create_account(account_data: AccountCreate, current_user: User = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    new_account = Account(
        id=account_id,
        user_id=current_user.id,
        account_number=generate_account_number(),
        account_type=account_data.account_type,
        balance=account_data.initial_deposit,
        currency="USD",
        nickname=account_data.nickname,
        created_at=datetime.now().isoformat(),
        is_active=True
    )
    
    accounts_db.append(new_account)
    
    if account_data.initial_deposit > 0:
        transaction = Transaction(
            id=str(uuid.uuid4()),
            account_id=account_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=account_data.initial_deposit,
            currency="USD",
            description="Initial deposit",
            status=TransactionStatus.COMPLETED,
            created_at=datetime.now().isoformat(),
            reference_number=generate_reference_number()
        )
        transactions_db.append(transaction)
    
    return new_account

@app.put("/api/accounts/{account_id}", response_model=Account)
def update_account(account_id: str, nickname: str, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc.id == account_id and acc.user_id == current_user.id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    account.nickname = nickname
    return account

@app.delete("/api/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_account(account_id: str, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc.id == account_id and acc.user_id == current_user.id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    if account.balance > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot close account with remaining balance")
    
    account.is_active = False
    return None

# Transaction endpoints
@app.get("/api/transactions", response_model=List[Transaction])
def get_transactions(account_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    user_account_ids = [acc.id for acc in accounts_db if acc.user_id == current_user.id]
    
    if account_id:
        if account_id not in user_account_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        transactions = [t for t in transactions_db if t.account_id == account_id]
    else:
        transactions = [t for t in transactions_db if t.account_id in user_account_ids]
    
    return sorted(transactions, key=lambda x: x.created_at, reverse=True)

@app.get("/api/transactions/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: str, current_user: User = Depends(get_current_user)):
    user_account_ids = [acc.id for acc in accounts_db if acc.user_id == current_user.id]
    transaction = next((t for t in transactions_db if t.id == transaction_id and t.account_id in user_account_ids), None)
    
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    
    return transaction

@app.post("/api/transactions/transfer", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transfer(transfer: TransferRequest, current_user: User = Depends(get_current_user)):
    from_account = next((acc for acc in accounts_db if acc.id == transfer.from_account_id and acc.user_id == current_user.id), None)
    if not from_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source account not found")
    
    to_account = next((acc for acc in accounts_db if acc.id == transfer.to_account_id), None)
    if not to_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination account not found")
    
    if from_account.balance < transfer.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
    
    if transfer.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    
    from_account.balance -= transfer.amount
    to_account.balance += transfer.amount
    
    transaction = Transaction(
        id=str(uuid.uuid4()),
        account_id=transfer.from_account_id,
        transaction_type=TransactionType.TRANSFER,
        amount=transfer.amount,
        currency="USD",
        description=transfer.description,
        status=TransactionStatus.COMPLETED,
        created_at=datetime.now().isoformat(),
        to_account_id=transfer.to_account_id,
        reference_number=generate_reference_number()
    )
    
    transactions_db.append(transaction)
    
    incoming_transaction = Transaction(
        id=str(uuid.uuid4()),
        account_id=transfer.to_account_id,
        transaction_type=TransactionType.TRANSFER,
        amount=transfer.amount,
        currency="USD",
        description=f"Transfer from {from_account.account_number}",
        status=TransactionStatus.COMPLETED,
        created_at=datetime.now().isoformat(),
        to_account_id=transfer.from_account_id,
        reference_number=transaction.reference_number
    )
    
    transactions_db.append(incoming_transaction)
    
    return transaction

@app.post("/api/transactions/payment", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentRequest, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc.id == payment.account_id and acc.user_id == current_user.id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    if account.balance < payment.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
    
    if payment.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    
    account.balance -= payment.amount
    
    transaction = Transaction(
        id=str(uuid.uuid4()),
        account_id=payment.account_id,
        transaction_type=TransactionType.PAYMENT,
        amount=payment.amount,
        currency="USD",
        description=f"Payment to {payment.payee_name}: {payment.description}",
        status=TransactionStatus.COMPLETED,
        created_at=datetime.now().isoformat(),
        reference_number=generate_reference_number()
    )
    
    transactions_db.append(transaction)
    return transaction

@app.post("/api/transactions/deposit", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_deposit(transaction_data: TransactionCreate, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc.id == transaction_data.account_id and acc.user_id == current_user.id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    if transaction_data.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    
    account.balance += transaction_data.amount
    
    transaction = Transaction(
        id=str(uuid.uuid4()),
        account_id=transaction_data.account_id,
        transaction_type=TransactionType.DEPOSIT,
        amount=transaction_data.amount,
        currency="USD",
        description=transaction_data.description,
        status=TransactionStatus.COMPLETED,
        created_at=datetime.now().isoformat(),
        reference_number=generate_reference_number()
    )
    
    transactions_db.append(transaction)
    return transaction

@app.post("/api/transactions/withdrawal", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_withdrawal(transaction_data: TransactionCreate, current_user: User = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc.id == transaction_data.account_id and acc.user_id == current_user.id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    if account.balance < transaction_data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
    
    if transaction_data.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    
    account.balance -= transaction_data.amount
    
    transaction = Transaction(
        id=str(uuid.uuid4()),
        account_id=transaction_data.account_id,
        transaction_type=TransactionType.WITHDRAWAL,
        amount=transaction_data.amount,
        currency="USD",
        description=transaction_data.description,
        status=TransactionStatus.COMPLETED,
        created_at=datetime.now().isoformat(),
        reference_number=generate_reference_number()
    )
    
    transactions_db.append(transaction)
    return transaction

# Beneficiary endpoints
@app.get("/api/beneficiaries", response_model=List[Beneficiary])
def get_beneficiaries(current_user: User = Depends(get_current_user)):
    user_beneficiaries = [b for b in beneficiaries_db if b.user_id == current_user.id]
    return user_beneficiaries

@app.post("/api/beneficiaries", response_model=Beneficiary, status_code=status.HTTP_201_CREATED)
def create_beneficiary(beneficiary_data: BeneficiaryCreate, current_user: User = Depends(get_current_user)):
    beneficiary_id = str(uuid.uuid4())
    new_beneficiary = Beneficiary(
        id=beneficiary_id,
        user_id=current_user.id,
        name=beneficiary_data.name,
        account_number=beneficiary_data.account_number,
        bank_name=beneficiary_data.bank_name,
        created_at=datetime.now().isoformat()
    )
    
    beneficiaries_db.append(new_beneficiary)
    return new_beneficiary

@app.delete("/api/beneficiaries/{beneficiary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_beneficiary(beneficiary_id: str, current_user: User = Depends(get_current_user)):
    beneficiary = next((b for b in beneficiaries_db if b.id == beneficiary_id and b.user_id == current_user.id), None)
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")
    
    beneficiaries_db.remove(beneficiary)
    return None

# Analytics endpoints
@app.get("/api/analytics/summary", response_model=Analytics)
def get_analytics_summary(account_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    user_account_ids = [acc.id for acc in accounts_db if acc.user_id == current_user.id]
    
    if account_id:
        if account_id not in user_account_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        filter_accounts = [account_id]
    else:
        filter_accounts = user_account_ids
    
    transactions = [t for t in transactions_db if t.account_id in filter_accounts]
    
    total_income = sum(t.amount for t in transactions if t.transaction_type in [TransactionType.DEPOSIT] or (t.transaction_type == TransactionType.TRANSFER and t.account_id in filter_accounts and t.to_account_id not in user_account_ids))
    total_expenses = sum(t.amount for t in transactions if t.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.PAYMENT] or (t.transaction_type == TransactionType.TRANSFER and t.account_id in filter_accounts and t.to_account_id in user_account_ids))
    
    total_balance = sum(acc.balance for acc in accounts_db if acc.id in filter_accounts)
    
    categories = {
        "deposits": sum(t.amount for t in transactions if t.transaction_type == TransactionType.DEPOSIT),
        "withdrawals": sum(t.amount for t in transactions if t.transaction_type == TransactionType.WITHDRAWAL),
        "payments": sum(t.amount for t in transactions if t.transaction_type == TransactionType.PAYMENT),
        "transfers": sum(t.amount for t in transactions if t.transaction_type == TransactionType.TRANSFER and t.account_id in filter_accounts)
    }
    
    return Analytics(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        net_balance=round(total_balance, 2),
        transaction_count=len(transactions),
        categories=categories
    )

@app.get("/api/analytics/spending")
def get_spending_analytics(days: int = 30, current_user: User = Depends(get_current_user)):
    user_account_ids = [acc.id for acc in accounts_db if acc.user_id == current_user.id]
    cutoff_date = datetime.now() - timedelta(days=days)
    
    transactions = [
        t for t in transactions_db 
        if t.account_id in user_account_ids 
        and datetime.fromisoformat(t.created_at) >= cutoff_date
        and t.transaction_type in [TransactionType.PAYMENT, TransactionType.WITHDRAWAL]
    ]
    
    total_spending = sum(t.amount for t in transactions)
    daily_average = total_spending / days if days > 0 else 0
    
    return {
        "period_days": days,
        "total_spending": round(total_spending, 2),
        "daily_average": round(daily_average, 2),
        "transaction_count": len(transactions),
        "largest_transaction": max((t.amount for t in transactions), default=0)
    }