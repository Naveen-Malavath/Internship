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

class UserBase(BaseModel):
    email: str
    full_name: str
    phone: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    created_at: str
    is_active: bool

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

class AccountBase(BaseModel):
    account_type: AccountType
    currency: str = "USD"

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    id: str
    user_id: str
    account_number: str
    balance: float
    created_at: str
    is_active: bool

class TransactionBase(BaseModel):
    amount: float
    transaction_type: TransactionType
    description: Optional[str] = None

class TransactionCreate(BaseModel):
    from_account_id: str
    to_account_id: Optional[str] = None
    amount: float
    transaction_type: TransactionType
    description: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: str
    from_account_id: str
    to_account_id: Optional[str]
    status: TransactionStatus
    created_at: str
    completed_at: Optional[str]

class PaymentRequest(BaseModel):
    account_id: str
    payee_name: str
    payee_account: str
    amount: float
    description: Optional[str] = None

class PaymentResponse(BaseModel):
    id: str
    account_id: str
    payee_name: str
    payee_account: str
    amount: float
    status: TransactionStatus
    created_at: str
    description: Optional[str]

class BeneficiaryCreate(BaseModel):
    name: str
    account_number: str
    bank_name: str
    nickname: Optional[str] = None

class BeneficiaryResponse(BeneficiaryCreate):
    id: str
    user_id: str
    created_at: str

class AccountAnalytics(BaseModel):
    account_id: str
    account_number: str
    current_balance: float
    total_income: float
    total_expenses: float
    transaction_count: int
    average_transaction: float
    largest_transaction: float
    period_start: str
    period_end: str

class UserAnalytics(BaseModel):
    user_id: str
    total_accounts: int
    total_balance: float
    total_transactions: int
    monthly_income: float
    monthly_expenses: float
    accounts: List[AccountAnalytics]

users_db = []
accounts_db = []
transactions_db = []
beneficiaries_db = []
sessions_db = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def generate_account_number() -> str:
    return f"{uuid.uuid4().int % 10000000000:010d}"

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user_id = sessions_db.get(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

seed_user_1_id = str(uuid.uuid4())
seed_user_2_id = str(uuid.uuid4())
seed_token_1 = str(uuid.uuid4())
seed_token_2 = str(uuid.uuid4())

users_db.extend([
    {
        "id": seed_user_1_id,
        "email": "john.doe@example.com",
        "password": hash_password("password123"),
        "full_name": "John Doe",
        "phone": "+1234567890",
        "created_at": datetime.now().isoformat(),
        "is_active": True
    },
    {
        "id": seed_user_2_id,
        "email": "jane.smith@example.com",
        "password": hash_password("password456"),
        "full_name": "Jane Smith",
        "phone": "+1987654321",
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
])

sessions_db[seed_token_1] = seed_user_1_id
sessions_db[seed_token_2] = seed_user_2_id

seed_account_1 = str(uuid.uuid4())
seed_account_2 = str(uuid.uuid4())
seed_account_3 = str(uuid.uuid4())

accounts_db.extend([
    {
        "id": seed_account_1,
        "user_id": seed_user_1_id,
        "account_number": generate_account_number(),
        "account_type": "checking",
        "currency": "USD",
        "balance": 5000.00,
        "created_at": datetime.now().isoformat(),
        "is_active": True
    },
    {
        "id": seed_account_2,
        "user_id": seed_user_1_id,
        "account_number": generate_account_number(),
        "account_type": "savings",
        "currency": "USD",
        "balance": 15000.00,
        "created_at": datetime.now().isoformat(),
        "is_active": True
    },
    {
        "id": seed_account_3,
        "user_id": seed_user_2_id,
        "account_number": generate_account_number(),
        "account_type": "checking",
        "currency": "USD",
        "balance": 3000.00,
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
])

transactions_db.extend([
    {
        "id": str(uuid.uuid4()),
        "from_account_id": seed_account_1,
        "to_account_id": None,
        "amount": 1000.00,
        "transaction_type": "deposit",
        "description": "Salary deposit",
        "status": "completed",
        "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
        "completed_at": (datetime.now() - timedelta(days=5)).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "from_account_id": seed_account_1,
        "to_account_id": None,
        "amount": 150.00,
        "transaction_type": "withdrawal",
        "description": "ATM withdrawal",
        "status": "completed",
        "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
        "completed_at": (datetime.now() - timedelta(days=3)).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "from_account_id": seed_account_1,
        "to_account_id": seed_account_2,
        "amount": 500.00,
        "transaction_type": "transfer",
        "description": "Transfer to savings",
        "status": "completed",
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "completed_at": (datetime.now() - timedelta(days=1)).isoformat()
    }
])

beneficiaries_db.extend([
    {
        "id": str(uuid.uuid4()),
        "user_id": seed_user_1_id,
        "name": "Electric Company",
        "account_number": "9876543210",
        "bank_name": "Utility Bank",
        "nickname": "Electric Bill",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": seed_user_1_id,
        "name": "Jane Smith",
        "account_number": accounts_db[2]["account_number"],
        "bank_name": "Same Bank",
        "nickname": "Jane",
        "created_at": datetime.now().isoformat()
    }
])

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Digital Banking Suite",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    if any(u["email"] == user.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "email": user.email,
        "password": hash_password(user.password),
        "full_name": user.full_name,
        "phone": user.phone,
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    users_db.append(new_user)
    
    return UserResponse(
        id=new_user["id"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        phone=new_user["phone"],
        created_at=new_user["created_at"],
        is_active=new_user["is_active"]
    )

@app.post("/api/auth/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    user = next((u for u in users_db if u["email"] == credentials.email), None)
    
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    token = str(uuid.uuid4())
    sessions_db[token] = user["id"]
    
    return LoginResponse(
        token=token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            phone=user["phone"],
            created_at=user["created_at"],
            is_active=user["is_active"]
        )
    )

@app.post("/api/auth/logout")
def logout(current_user: dict = Depends(get_current_user), authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        if token in sessions_db:
            del sessions_db[token]
    
    return {"message": "Successfully logged out"}

@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        phone=current_user["phone"],
        created_at=current_user["created_at"],
        is_active=current_user["is_active"]
    )

@app.get("/api/accounts", response_model=List[AccountResponse])
def get_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == current_user["id"]]
    return [AccountResponse(**acc) for acc in user_accounts]

@app.post("/api/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account: AccountCreate, current_user: dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    new_account = {
        "id": account_id,
        "user_id": current_user["id"],
        "account_number": generate_account_number(),
        "account_type": account.account_type,
        "currency": account.currency,
        "balance": 0.0,
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    accounts_db.append(new_account)
    
    return AccountResponse(**new_account)

@app.get("/api/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: str, current_user: dict = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return AccountResponse(**account)

@app.delete("/api/accounts/{account_id}")
def deactivate_account(account_id: str, current_user: dict = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if account["balance"] > 0:
        raise HTTPException(status_code=400, detail="Cannot deactivate account with positive balance")
    
    account["is_active"] = False
    
    return {"message": "Account deactivated successfully"}

@app.get("/api/accounts/{account_id}/transactions", response_model=List[TransactionResponse])
def get_account_transactions(account_id: str, current_user: dict = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account_transactions = [
        tx for tx in transactions_db 
        if tx["from_account_id"] == account_id or tx.get("to_account_id") == account_id
    ]
    
    return [TransactionResponse(**tx) for tx in sorted(account_transactions, key=lambda x: x["created_at"], reverse=True)]

@app.post("/api/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: TransactionCreate, current_user: dict = Depends(get_current_user)):
    from_account = next((acc for acc in accounts_db if acc["id"] == transaction.from_account_id), None)
    
    if not from_account:
        raise HTTPException(status_code=404, detail="From account not found")
    
    if from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not from_account["is_active"]:
        raise HTTPException(status_code=400, detail="Account is not active")
    
    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if transaction.transaction_type in ["withdrawal", "transfer", "payment"]:
        if from_account["balance"] < transaction.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
    
    to_account = None
    if transaction.to_account_id:
        to_account = next((acc for acc in accounts_db if acc["id"] == transaction.to_account_id), None)
        if not to_account:
            raise HTTPException(status_code=404, detail="To account not found")
        if not to_account["is_active"]:
            raise HTTPException(status_code=400, detail="Destination account is not active")
    
    transaction_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    new_transaction = {
        "id": transaction_id,
        "from_account_id": transaction.from_account_id,
        "to_account_id": transaction.to_account_id,
        "amount": transaction.amount,
        "transaction_type": transaction.transaction_type,
        "description": transaction.description,
        "status": "completed",
        "created_at": now,
        "completed_at": now
    }
    
    if transaction.transaction_type == "deposit":
        from_account["balance"] += transaction.amount
    elif transaction.transaction_type == "withdrawal":
        from_account["balance"] -= transaction.amount
    elif transaction.transaction_type == "transfer":
        from_account["balance"] -= transaction.amount
        if to_account:
            to_account["balance"] += transaction.amount
    elif transaction.transaction_type == "payment":
        from_account["balance"] -= transaction.amount
    
    transactions_db.append(new_transaction)
    
    return TransactionResponse(**new_transaction)

@app.get("/api/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str, current_user: dict = Depends(get_current_user)):
    transaction = next((tx for tx in transactions_db if tx["id"] == transaction_id), None)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    from_account = next((acc for acc in accounts_db if acc["id"] == transaction["from_account_id"]), None)
    to_account = None
    if transaction.get("to_account_id"):
        to_account = next((acc for acc in accounts_db if acc["id"] == transaction["to_account_id"]), None)
    
    if (from_account and from_account["user_id"] != current_user["id"]) and \
       (not to_account or to_account["user_id"] != current_user["id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return TransactionResponse(**transaction)

@app.post("/api/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentRequest, current_user: dict = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == payment.account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not account["is_active"]:
        raise HTTPException(status_code=400, detail="Account is not active")
    
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if account["balance"] < payment.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    payment_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    account["balance"] -= payment.amount
    
    transaction = {
        "id": str(uuid.uuid4()),
        "from_account_id": payment.account_id,
        "to_account_id": None,
        "amount": payment.amount,
        "transaction_type": "payment",
        "description": f"Payment to {payment.payee_name}: {payment.description or ''}",
        "status": "completed",
        "created_at": now,
        "completed_at": now
    }
    transactions_db.append(transaction)
    
    payment_record = {
        "id": payment_id,
        "account_id": payment.account_id,
        "payee_name": payment.payee_name,
        "payee_account": payment.payee_account,
        "amount": payment.amount,
        "status": "completed",
        "created_at": now,
        "description": payment.description
    }
    
    return PaymentResponse(**payment_record)

@app.get("/api/beneficiaries", response_model=List[BeneficiaryResponse])
def get_beneficiaries(current_user: dict = Depends(get_current_user)):
    user_beneficiaries = [b for b in beneficiaries_db if b["user_id"] == current_user["id"]]
    return [BeneficiaryResponse(**b) for b in user_beneficiaries]

@app.post("/api/beneficiaries", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiary(beneficiary: BeneficiaryCreate, current_user: dict = Depends(get_current_user)):
    beneficiary_id = str(uuid.uuid4())
    new_beneficiary = {
        "id": beneficiary_id,
        "user_id": current_user["id"],
        "name": beneficiary.name,
        "account_number": beneficiary.account_number,
        "bank_name": beneficiary.bank_name,
        "nickname": beneficiary.nickname,
        "created_at": datetime.now().isoformat()
    }
    beneficiaries_db.append(new_beneficiary)
    
    return BeneficiaryResponse(**new_beneficiary)

@app.delete("/api/beneficiaries/{beneficiary_id}")
def delete_beneficiary(beneficiary_id: str, current_user: dict = Depends(get_current_user)):
    beneficiary = next((b for b in beneficiaries_db if b["id"] == beneficiary_id), None)
    
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    
    if beneficiary["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    beneficiaries_db.remove(beneficiary)
    
    return {"message": "Beneficiary deleted successfully"}

@app.get("/api/analytics/account/{account_id}", response_model=AccountAnalytics)
def get_account_analytics(account_id: str, days: int = 30, current_user: dict = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    start_date = datetime.now() - timedelta(days=days)
    
    account_transactions = [
        tx for tx in transactions_db 
        if (tx["from_account_id"] == account_id or tx.get("to_account_id") == account_id) and
        datetime.fromisoformat(tx["created_at"]) >= start_date
    ]
    
    total_income = sum(
        tx["amount"] for tx in account_transactions 
        if tx["transaction_type"] == "deposit" or 
        (tx["transaction_type"] == "transfer" and tx.get("to_account_id") == account_id)
    )
    
    total_expenses = sum(
        tx["amount"] for tx in account_transactions 
        if tx["transaction_type"] in ["withdrawal", "payment"] or 
        (tx["transaction_type"] == "transfer" and tx["from_account_id"] == account_id)
    )
    
    transaction_amounts = [tx["amount"] for tx in account_transactions]
    
    return AccountAnalytics(
        account_id=account["id"],
        account_number=account["account_number"],
        current_balance=account["balance"],
        total_income=total_income,
        total_expenses=total_expenses,
        transaction_count=len(account_transactions),
        average_transaction=sum(transaction_amounts) / len(transaction_amounts) if transaction_amounts else 0,
        largest_transaction=max(transaction_amounts) if transaction_amounts else 0,
        period_start=start_date.isoformat(),
        period_end=datetime.now().isoformat()
    )

@app.get("/api/analytics/user", response_model=UserAnalytics)
def get_user_analytics(days: int = 30, current_user: dict = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == current_user["id"]]
    
    total_balance = sum(acc["balance"] for acc in user_accounts)
    
    start_date = datetime.now() - timedelta(days=days)
    
    all_transactions = [
        tx for tx in transactions_db 
        if any(tx["from_account_id"] == acc["id"] or tx.get("to_account_id") == acc["id"] for acc in user_accounts) and
        datetime.fromisoformat(tx["created_at"]) >= start_date
    ]
    
    monthly_income = sum(
        tx["amount"] for tx in all_transactions 
        if tx["transaction_type"] == "deposit" or 
        (tx["transaction_type"] == "transfer" and any(tx.get("to_account_id") == acc["id"] for acc in user_accounts))
    )
    
    monthly_expenses = sum(
        tx["amount"] for tx in all_transactions 
        if tx["transaction_type"] in ["withdrawal", "payment"] or 
        (tx["transaction_type"] == "transfer" and any(tx["from_account_id"] == acc["id"] for acc in user_accounts))
    )
    
    account_analytics = []
    for acc in user_accounts:
        account_transactions = [
            tx for tx in all_transactions 
            if tx["from_account_id"] == acc["id"] or tx.get("to_account_id") == acc["id"]
        ]
        
        acc_income = sum(
            tx["amount"] for tx in account_transactions 
            if tx["transaction_type"] == "deposit" or 
            (tx["transaction_type"] == "transfer" and tx.get("to_account_id") == acc["id"])
        )
        
        acc_expenses = sum(
            tx["amount"] for tx in account_transactions 
            if tx["transaction_type"] in ["withdrawal", "payment"] or 
            (tx["transaction_type"] == "transfer" and tx["from_account_id"] == acc["id"])
        )
        
        transaction_amounts = [tx["amount"] for tx in account_transactions]
        
        account_analytics.append(AccountAnalytics(
            account_id=acc["id"],
            account_number=acc["account_number"],
            current_balance=acc["balance"],
            total_income=acc_income,
            total_expenses=acc_expenses,
            transaction_count=len(account_transactions),
            average_transaction=sum(transaction_amounts) / len(transaction_amounts) if transaction_amounts else 0,
            largest_transaction=max(transaction_amounts) if transaction_amounts else 0,
            period_start=start_date.isoformat(),
            period_end=datetime.now().isoformat()
        ))
    
    return UserAnalytics(
        user_id=current_user["id"],
        total_accounts=len(user_accounts),
        total_balance=total_balance,
        total_transactions=len(all_transactions),
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        accounts=account_analytics
    )