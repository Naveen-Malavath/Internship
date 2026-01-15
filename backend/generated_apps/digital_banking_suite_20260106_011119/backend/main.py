from fastapi import FastAPI, HTTPException, status, Depends, Header
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

class User(BaseModel):
    id: str
    email: str
    full_name: str
    phone: str
    created_at: str
    password_hash: str

class UserCreate(BaseModel):
    email: str
    full_name: str
    phone: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: str
    created_at: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

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
    initial_deposit: float = 0.0
    currency: str = "USD"

class AccountResponse(BaseModel):
    id: str
    user_id: str
    account_number: str
    account_type: AccountType
    balance: float
    currency: str
    created_at: str
    is_active: bool

class Transaction(BaseModel):
    id: str
    account_id: str
    transaction_type: TransactionType
    amount: float
    currency: str
    description: str
    status: TransactionStatus
    created_at: str
    reference_number: str
    to_account_id: Optional[str] = None

class TransactionCreate(BaseModel):
    account_id: str
    transaction_type: TransactionType
    amount: float
    description: str
    to_account_id: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    account_id: str
    transaction_type: TransactionType
    amount: float
    currency: str
    description: str
    status: TransactionStatus
    created_at: str
    reference_number: str
    to_account_id: Optional[str] = None

class PaymentRequest(BaseModel):
    from_account_id: str
    to_account_number: str
    amount: float
    description: str

class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    reference_number: str
    message: str

class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float
    description: str

class AccountAnalytics(BaseModel):
    account_id: str
    total_deposits: float
    total_withdrawals: float
    total_transfers: float
    transaction_count: int
    average_transaction: float
    current_balance: float

class UserAnalytics(BaseModel):
    user_id: str
    total_accounts: int
    total_balance: float
    accounts_breakdown: List[Dict]
    recent_transactions: List[TransactionResponse]

users_db: List[User] = []
accounts_db: List[Account] = []
transactions_db: List[Transaction] = []
sessions_db: Dict[str, str] = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_account_number() -> str:
    return str(uuid.uuid4().int)[:12]

def generate_reference_number() -> str:
    return f"REF{uuid.uuid4().hex[:10].upper()}"

def verify_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    
    if token not in sessions_db:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return sessions_db[token]

def get_user_by_id(user_id: str) -> Optional[User]:
    for user in users_db:
        if user.id == user_id:
            return user
    return None

def get_account_by_id(account_id: str) -> Optional[Account]:
    for account in accounts_db:
        if account.id == account_id:
            return account
    return None

def get_account_by_number(account_number: str) -> Optional[Account]:
    for account in accounts_db:
        if account.account_number == account_number:
            return account
    return None

user1_id = str(uuid.uuid4())
user2_id = str(uuid.uuid4())
user3_id = str(uuid.uuid4())

users_db.extend([
    User(
        id=user1_id,
        email="john.doe@example.com",
        full_name="John Doe",
        phone="+1234567890",
        created_at=datetime.now().isoformat(),
        password_hash=hash_password("password123")
    ),
    User(
        id=user2_id,
        email="jane.smith@example.com",
        full_name="Jane Smith",
        phone="+1234567891",
        created_at=datetime.now().isoformat(),
        password_hash=hash_password("password123")
    ),
    User(
        id=user3_id,
        email="bob.wilson@example.com",
        full_name="Bob Wilson",
        phone="+1234567892",
        created_at=datetime.now().isoformat(),
        password_hash=hash_password("password123")
    )
])

account1_id = str(uuid.uuid4())
account2_id = str(uuid.uuid4())
account3_id = str(uuid.uuid4())
account4_id = str(uuid.uuid4())

accounts_db.extend([
    Account(
        id=account1_id,
        user_id=user1_id,
        account_number=generate_account_number(),
        account_type=AccountType.CHECKING,
        balance=5000.00,
        currency="USD",
        created_at=datetime.now().isoformat(),
        is_active=True
    ),
    Account(
        id=account2_id,
        user_id=user1_id,
        account_number=generate_account_number(),
        account_type=AccountType.SAVINGS,
        balance=15000.00,
        currency="USD",
        created_at=datetime.now().isoformat(),
        is_active=True
    ),
    Account(
        id=account3_id,
        user_id=user2_id,
        account_number=generate_account_number(),
        account_type=AccountType.CHECKING,
        balance=3500.00,
        currency="USD",
        created_at=datetime.now().isoformat(),
        is_active=True
    ),
    Account(
        id=account4_id,
        user_id=user3_id,
        account_number=generate_account_number(),
        account_type=AccountType.SAVINGS,
        balance=25000.00,
        currency="USD",
        created_at=datetime.now().isoformat(),
        is_active=True
    )
])

transactions_db.extend([
    Transaction(
        id=str(uuid.uuid4()),
        account_id=account1_id,
        transaction_type=TransactionType.DEPOSIT,
        amount=1000.00,
        currency="USD",
        description="Initial deposit",
        status=TransactionStatus.COMPLETED,
        created_at=(datetime.now() - timedelta(days=5)).isoformat(),
        reference_number=generate_reference_number()
    ),
    Transaction(
        id=str(uuid.uuid4()),
        account_id=account1_id,
        transaction_type=TransactionType.WITHDRAWAL,
        amount=200.00,
        currency="USD",
        description="ATM withdrawal",
        status=TransactionStatus.COMPLETED,
        created_at=(datetime.now() - timedelta(days=3)).isoformat(),
        reference_number=generate_reference_number()
    ),
    Transaction(
        id=str(uuid.uuid4()),
        account_id=account2_id,
        transaction_type=TransactionType.DEPOSIT,
        amount=5000.00,
        currency="USD",
        description="Savings deposit",
        status=TransactionStatus.COMPLETED,
        created_at=(datetime.now() - timedelta(days=2)).isoformat(),
        reference_number=generate_reference_number()
    ),
    Transaction(
        id=str(uuid.uuid4()),
        account_id=account3_id,
        transaction_type=TransactionType.PAYMENT,
        amount=150.00,
        currency="USD",
        description="Utility payment",
        status=TransactionStatus.COMPLETED,
        created_at=(datetime.now() - timedelta(days=1)).isoformat(),
        reference_number=generate_reference_number()
    )
])

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Digital Banking Suite",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate):
    for user in users_db:
        if user.email == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone,
        created_at=datetime.now().isoformat(),
        password_hash=hash_password(user_data.password)
    )
    
    users_db.append(new_user)
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        phone=new_user.phone,
        created_at=new_user.created_at
    )

@app.post("/api/auth/login", response_model=LoginResponse)
def login(login_data: LoginRequest):
    user = None
    for u in users_db:
        if u.email == login_data.email:
            user = u
            break
    
    if not user or user.password_hash != hash_password(login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = str(uuid.uuid4())
    sessions_db[token] = user.id
    
    return LoginResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            created_at=user.created_at
        )
    )

@app.post("/api/auth/logout")
def logout(user_id: str = Depends(verify_token)):
    tokens_to_remove = [token for token, uid in sessions_db.items() if uid == user_id]
    for token in tokens_to_remove:
        del sessions_db[token]
    
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user(user_id: str = Depends(verify_token)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        created_at=user.created_at
    )

@app.get("/api/accounts", response_model=List[AccountResponse])
def get_accounts(user_id: str = Depends(verify_token)):
    user_accounts = [acc for acc in accounts_db if acc.user_id == user_id]
    return [AccountResponse(**acc.dict()) for acc in user_accounts]

@app.post("/api/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account_data: AccountCreate, user_id: str = Depends(verify_token)):
    new_account = Account(
        id=str(uuid.uuid4()),
        user_id=user_id,
        account_number=generate_account_number(),
        account_type=account_data.account_type,
        balance=account_data.initial_deposit,
        currency=account_data.currency,
        created_at=datetime.now().isoformat(),
        is_active=True
    )
    
    accounts_db.append(new_account)
    
    if account_data.initial_deposit > 0:
        initial_transaction = Transaction(
            id=str(uuid.uuid4()),
            account_id=new_account.id,
            transaction_type=TransactionType.DEPOSIT,
            amount=account_data.initial_deposit,
            currency=account_data.currency,
            description="Initial deposit",
            status=TransactionStatus.COMPLETED,
            created_at=datetime.now().isoformat(),
            reference_number=generate_reference_number()
        )
        transactions_db.append(initial_transaction)
    
    return AccountResponse(**new_account.dict())

@app.get("/api/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: str, user_id: str = Depends(verify_token)):
    account = get_account_by_id(account_id)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return AccountResponse(**account.dict())

@app.put("/api/accounts/{account_id}/status", response_model=AccountResponse)
def update_account_status(account_id: str, is_active: bool, user_id: str = Depends(verify_token)):
    account = get_account_by_id(account_id)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account.is_active = is_active
    
    return AccountResponse(**account.dict())

@app.get("/api/accounts/{account_id}/transactions", response_model=List[TransactionResponse])
def get_account_transactions(account_id: str, user_id: str = Depends(verify_token)):
    account = get_account_by_id(account_id)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account_transactions = [
        t for t in transactions_db 
        if t.account_id == account_id or t.to_account_id == account_id
    ]
    
    account_transactions.sort(key=lambda x: x.created_at, reverse=True)
    
    return [TransactionResponse(**t.dict()) for t in account_transactions]

@app.post("/api/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionCreate, user_id: str = Depends(verify_token)):
    account = get_account_by_id(transaction_data.account_id)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not account.is_active:
        raise HTTPException(status_code=400, detail="Account is not active")
    
    if transaction_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if transaction_data.transaction_type == TransactionType.WITHDRAWAL:
        if account.balance < transaction_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        account.balance -= transaction_data.amount
    elif transaction_data.transaction_type == TransactionType.DEPOSIT:
        account.balance += transaction_data.amount
    elif transaction_data.transaction_type == TransactionType.PAYMENT:
        if account.balance < transaction_data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        account.balance -= transaction_data.amount
    
    new_transaction = Transaction(
        id=str(uuid.uuid4()),
        account_id=transaction_data.account_id,
        transaction_type=transaction_data.transaction_type,
        amount=transaction_data.amount,
        currency=account.currency,
        description=transaction_data.description,
        status=TransactionStatus.COMPLETED,
        created_at=datetime.now().isoformat(),
        reference_number=generate_reference_number(),
        to_account_id=transaction_data.to_account_id
    )
    
    transactions_db.append(new_transaction)
    
    return TransactionResponse(**new_transaction.dict())

@app.post("/api/payments", response_model=PaymentResponse)
def process_payment(payment_data: PaymentRequest, user_id: str = Depends(verify_token)):
    from_account = get_account_by_id(payment_data.from_account_id)
    
    if not from_account:
        raise HTTPException(status_code=404, detail="Source account not found")
    
    if from_account.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not from_account.is_active:
        raise HTTPException(status_code=400, detail="Source account is not active")
    
    if payment_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if from_account.balance < payment_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    to_account = get_account_by_number(payment_data.to_account_number)
    
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    
    if not to_account.is_active:
        raise HTTPException(status_code=400, detail="Destination account is not active")
    
    from_account.balance -= payment_data.amount
    to_account.balance += payment_data.amount
    
    reference = generate_reference_number()
    
    payment_transaction = Transaction(
        id=str(uuid.uuid4()),
        account_id=payment_data.from_account_id,
        transaction_type=TransactionType.PAYMENT,
        amount=payment_data.amount,
        currency=from_account.currency,
        description=payment_data.description,
        status=TransactionStatus.COMPLETED,
        created_at=datetime.now().isoformat(),
        reference_number=reference,
        to_account_id=to_account.id
    )
    
    transactions_db.append(payment_transaction)
    
    receipt_transaction = Transaction(
        id=str(uuid.uuid4()),
        account_id=to_account.id,
        transaction_type=TransactionType.DEPOSIT,
        amount=payment_data.amount,
        currency=to_account.currency,
        description=f"Payment received: {payment_data.description}",
        status=TransactionStatus.COMPLETED,
        created_at=datetime.now().isoformat(),
        reference_number=reference,
        to_account_id=None
    )
    
    transactions_db.append(receipt_transaction)
    
    return PaymentResponse(
        transaction_id=payment_transaction.id,
        status="completed",
        reference_number=reference,
        message="Payment processed successfully"
    )

@app.post("/api/transfers", response_model=PaymentResponse)
def transfer_funds(transfer_data: TransferRequest, user_id: str = Depends(verify_token)):
    from_account = get_account_by_id(transfer_data.from_account_id)
    to_account = get_account_by_id(transfer_data.to_account_id)
    
    if not from_account:
        raise HTTPException(status_code=404, detail="Source account not found")
    
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    
    if from_account.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied to source account")
    
    if not from_account.is_active or not to_account.is_active:
        raise HTTPException(status_code=400, detail="One or both accounts are not active")
    
    if transfer_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if from_account.balance < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    from_account.balance -= transfer_data.amount
    to_account.balance += transfer_data.amount
    
    reference = generate_reference_number()
    
    transfer_out = Transaction(
        id=str(uuid.uuid4()),
        account_id=transfer_data.from_account_id,
        transaction_type=TransactionType.TRANSFER,
        amount=transfer_data.amount,
        currency=from_account.currency,
        description=transfer_data.description,
        status=TransactionStatus.COMPLETED,
        created_at=datetime.now().isoformat(),
        reference_number=reference,
        to_account_id=transfer_data.to_account_id
    )
    
    transactions_db.append(transfer_out)
    
    transfer_in = Transaction(
        id=str(uuid.uuid4()),
        account_id=transfer_data.to_account_id,
        transaction_type=TransactionType.TRANSFER,
        amount=transfer_data.amount,
        currency=to_account.currency,
        description=f"Transfer received: {transfer_data.description}",
        status=TransactionStatus.COMPLETED,
        created_at=datetime.now().isoformat(),
        reference_number=reference,
        to_account_id=None
    )
    
    transactions_db.append(transfer_in)
    
    return PaymentResponse(
        transaction_id=transfer_out.id,
        status="completed",
        reference_number=reference,
        message="Transfer completed successfully"
    )

@app.get("/api/analytics/account/{account_id}", response_model=AccountAnalytics)
def get_account_analytics(account_id: str, user_id: str = Depends(verify_token)):
    account = get_account_by_id(account_id)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account_transactions = [t for t in transactions_db if t.account_id == account_id]
    
    total_deposits = sum(
        t.amount for t in account_transactions 
        if t.transaction_type == TransactionType.DEPOSIT and t.status == TransactionStatus.COMPLETED
    )
    
    total_withdrawals = sum(
        t.amount for t in account_transactions 
        if t.transaction_type == TransactionType.WITHDRAWAL and t.status == TransactionStatus.COMPLETED
    )
    
    total_transfers = sum(
        t.amount for t in account_transactions 
        if t.transaction_type == TransactionType.TRANSFER and t.status == TransactionStatus.COMPLETED
    )
    
    transaction_count = len([t for t in account_transactions if t.status == TransactionStatus.COMPLETED])
    
    average_transaction = (
        sum(t.amount for t in account_transactions if t.status == TransactionStatus.COMPLETED) / transaction_count
        if transaction_count > 0 else 0.0
    )
    
    return AccountAnalytics(
        account_id=account_id,
        total_deposits=total_deposits,
        total_withdrawals=total_withdrawals,
        total_transfers=total_transfers,
        transaction_count=transaction_count,
        average_transaction=round(average_transaction, 2),
        current_balance=account.balance
    )

@app.get("/api/analytics/user", response_model=UserAnalytics)
def get_user_analytics(user_id: str = Depends(verify_token)):
    user_accounts = [acc for acc in accounts_db if acc.user_id == user_id]
    
    if not user_accounts:
        raise HTTPException(status_code=404, detail="No accounts found for user")
    
    total_balance = sum(acc.balance for acc in user_accounts)
    
    accounts_breakdown = [
        {
            "account_id": acc.id,
            "account_number": acc.account_number,
            "account_type": acc.account_type,
            "balance": acc.balance,
            "currency": acc.currency
        }
        for acc in user_accounts
    ]
    
    all_transactions = []
    for acc in user_accounts:
        acc_transactions = [t for t in transactions_db if t.account_id == acc.id or t.to_account_id == acc.id]
        all_transactions.extend(acc_transactions)
    
    all_transactions.sort(key=lambda x: x.created_at, reverse=True)
    recent_transactions = all_transactions[:10]
    
    return UserAnalytics(
        user_id=user_id,
        total_accounts=len(user_accounts),
        total_balance=round(total_balance, 2),
        accounts_breakdown=accounts_breakdown,
        recent_transactions=[TransactionResponse(**t.dict()) for t in recent_transactions]
    )

@app.get("/api/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str, user_id: str = Depends(verify_token)):
    transaction = None
    for t in transactions_db:
        if t.id == transaction_id:
            transaction = t
            break
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    account = get_account_by_id(transaction.account_id)
    
    if not account or account.user_id != user_id:
        if transaction.to_account_id:
            to_account = get_account_by_id(transaction.to_account_id)
            if not to_account or to_account.user_id != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
        else:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return TransactionResponse(**transaction.dict())

@app.delete("/api/accounts/{account_id}")
def delete_account(account_id: str, user_id: str = Depends(verify_token)):
    account = get_account_by_id(account_id)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if account.balance > 0:
        raise HTTPException(status_code=400, detail="Cannot delete account with positive balance")
    
    accounts_db.remove(account)
    
    return {"message": "Account deleted successfully", "account_id": account_id}