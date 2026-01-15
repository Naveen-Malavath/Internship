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
    DEBIT = "debit"
    CREDIT = "credit"
    TRANSFER = "transfer"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str
    address: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: str
    address: str
    created_at: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class AccountCreate(BaseModel):
    account_type: AccountType
    account_name: str
    initial_balance: float = 0.0

class AccountResponse(BaseModel):
    id: str
    user_id: str
    account_type: AccountType
    account_name: str
    account_number: str
    balance: float
    currency: str
    created_at: str
    is_active: bool

class TransactionCreate(BaseModel):
    account_id: str
    amount: float
    transaction_type: TransactionType
    description: str
    recipient_account_id: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    account_id: str
    amount: float
    transaction_type: TransactionType
    description: str
    status: TransactionStatus
    recipient_account_id: Optional[str] = None
    balance_after: float
    created_at: str

class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float
    description: str

class PaymentCreate(BaseModel):
    account_id: str
    payee_name: str
    payee_account: str
    amount: float
    description: str

class PaymentResponse(BaseModel):
    id: str
    user_id: str
    account_id: str
    payee_name: str
    payee_account: str
    amount: float
    description: str
    status: PaymentStatus
    created_at: str
    completed_at: Optional[str] = None

class AnalyticsResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_flow: float
    transaction_count: int
    average_transaction: float
    largest_transaction: float
    by_category: Dict[str, float]

class BudgetCreate(BaseModel):
    category: str
    amount: float
    period: str

class BudgetResponse(BaseModel):
    id: str
    user_id: str
    category: str
    amount: float
    spent: float
    remaining: float
    period: str
    created_at: str

users_db = []
accounts_db = []
transactions_db = []
payments_db = []
budgets_db = []
sessions_db = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_account_number() -> str:
    return f"{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}"

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user_id = sessions_db.get(token)
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

def seed_data():
    user1_id = str(uuid.uuid4())
    user1_password = hash_password("password123")
    user1 = {
        "id": user1_id,
        "email": "john.doe@example.com",
        "password": user1_password,
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "address": "123 Main St, New York, NY 10001",
        "created_at": datetime.utcnow().isoformat()
    }
    users_db.append(user1)
    
    user2_id = str(uuid.uuid4())
    user2_password = hash_password("password456")
    user2 = {
        "id": user2_id,
        "email": "jane.smith@example.com",
        "password": user2_password,
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "+1234567891",
        "address": "456 Oak Ave, Los Angeles, CA 90001",
        "created_at": datetime.utcnow().isoformat()
    }
    users_db.append(user2)
    
    account1_id = str(uuid.uuid4())
    account1 = {
        "id": account1_id,
        "user_id": user1_id,
        "account_type": AccountType.CHECKING,
        "account_name": "Main Checking",
        "account_number": generate_account_number(),
        "balance": 5000.00,
        "currency": "USD",
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True
    }
    accounts_db.append(account1)
    
    account2_id = str(uuid.uuid4())
    account2 = {
        "id": account2_id,
        "user_id": user1_id,
        "account_type": AccountType.SAVINGS,
        "account_name": "Emergency Fund",
        "account_number": generate_account_number(),
        "balance": 10000.00,
        "currency": "USD",
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True
    }
    accounts_db.append(account2)
    
    account3_id = str(uuid.uuid4())
    account3 = {
        "id": account3_id,
        "user_id": user2_id,
        "account_type": AccountType.CHECKING,
        "account_name": "Primary Account",
        "account_number": generate_account_number(),
        "balance": 3500.00,
        "currency": "USD",
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True
    }
    accounts_db.append(account3)
    
    transaction1_id = str(uuid.uuid4())
    transaction1 = {
        "id": transaction1_id,
        "account_id": account1_id,
        "amount": 1000.00,
        "transaction_type": TransactionType.CREDIT,
        "description": "Salary deposit",
        "status": TransactionStatus.COMPLETED,
        "recipient_account_id": None,
        "balance_after": 5000.00,
        "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat()
    }
    transactions_db.append(transaction1)
    
    transaction2_id = str(uuid.uuid4())
    transaction2 = {
        "id": transaction2_id,
        "account_id": account1_id,
        "amount": 150.50,
        "transaction_type": TransactionType.DEBIT,
        "description": "Grocery shopping",
        "status": TransactionStatus.COMPLETED,
        "recipient_account_id": None,
        "balance_after": 4849.50,
        "created_at": (datetime.utcnow() - timedelta(days=3)).isoformat()
    }
    transactions_db.append(transaction2)
    
    transaction3_id = str(uuid.uuid4())
    transaction3 = {
        "id": transaction3_id,
        "account_id": account2_id,
        "amount": 500.00,
        "transaction_type": TransactionType.CREDIT,
        "description": "Monthly savings",
        "status": TransactionStatus.COMPLETED,
        "recipient_account_id": None,
        "balance_after": 10000.00,
        "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat()
    }
    transactions_db.append(transaction3)
    
    payment1_id = str(uuid.uuid4())
    payment1 = {
        "id": payment1_id,
        "user_id": user1_id,
        "account_id": account1_id,
        "payee_name": "Electric Company",
        "payee_account": "ELEC-123456",
        "amount": 120.00,
        "description": "Monthly electricity bill",
        "status": PaymentStatus.COMPLETED,
        "created_at": (datetime.utcnow() - timedelta(days=7)).isoformat(),
        "completed_at": (datetime.utcnow() - timedelta(days=7, hours=2)).isoformat()
    }
    payments_db.append(payment1)
    
    budget1_id = str(uuid.uuid4())
    budget1 = {
        "id": budget1_id,
        "user_id": user1_id,
        "category": "Groceries",
        "amount": 500.00,
        "spent": 150.50,
        "remaining": 349.50,
        "period": "monthly",
        "created_at": datetime.utcnow().isoformat()
    }
    budgets_db.append(budget1)
    
    budget2_id = str(uuid.uuid4())
    budget2 = {
        "id": budget2_id,
        "user_id": user1_id,
        "category": "Entertainment",
        "amount": 200.00,
        "spent": 0.00,
        "remaining": 200.00,
        "period": "monthly",
        "created_at": datetime.utcnow().isoformat()
    }
    budgets_db.append(budget2)

seed_data()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Digital Banking Suite"
    }

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    existing_user = next((u for u in users_db if u["email"] == user_data.email), None)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "address": user_data.address,
        "created_at": datetime.utcnow().isoformat()
    }
    users_db.append(user)
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        phone=user["phone"],
        address=user["address"],
        created_at=user["created_at"]
    )

@app.post("/api/auth/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    user = next((u for u in users_db if u["email"] == credentials.email), None)
    if not user or user["password"] != hash_password(credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = str(uuid.uuid4())
    sessions_db[token] = user["id"]
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            phone=user["phone"],
            address=user["address"],
            created_at=user["created_at"]
        )
    )

@app.post("/api/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "")
        if token in sessions_db:
            del sessions_db[token]
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        phone=current_user["phone"],
        address=current_user["address"],
        created_at=current_user["created_at"]
    )

@app.get("/api/accounts", response_model=List[AccountResponse])
def get_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [a for a in accounts_db if a["user_id"] == current_user["id"]]
    return [AccountResponse(**account) for account in user_accounts]

@app.get("/api/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: str, current_user: dict = Depends(get_current_user)):
    account = next((a for a in accounts_db if a["id"] == account_id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return AccountResponse(**account)

@app.post("/api/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account_data: AccountCreate, current_user: dict = Depends(get_current_user)):
    account_id = str(uuid.uuid4())
    account = {
        "id": account_id,
        "user_id": current_user["id"],
        "account_type": account_data.account_type,
        "account_name": account_data.account_name,
        "account_number": generate_account_number(),
        "balance": account_data.initial_balance,
        "currency": "USD",
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True
    }
    accounts_db.append(account)
    return AccountResponse(**account)

@app.delete("/api/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: str, current_user: dict = Depends(get_current_user)):
    account = next((a for a in accounts_db if a["id"] == account_id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if account["balance"] != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete account with non-zero balance")
    
    accounts_db.remove(account)
    return None

@app.get("/api/transactions", response_model=List[TransactionResponse])
def get_transactions(account_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    user_account_ids = [a["id"] for a in accounts_db if a["user_id"] == current_user["id"]]
    
    if account_id:
        if account_id not in user_account_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        user_transactions = [t for t in transactions_db if t["account_id"] == account_id]
    else:
        user_transactions = [t for t in transactions_db if t["account_id"] in user_account_ids]
    
    user_transactions.sort(key=lambda x: x["created_at"], reverse=True)
    return [TransactionResponse(**transaction) for transaction in user_transactions]

@app.get("/api/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str, current_user: dict = Depends(get_current_user)):
    transaction = next((t for t in transactions_db if t["id"] == transaction_id), None)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    
    account = next((a for a in accounts_db if a["id"] == transaction["account_id"]), None)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return TransactionResponse(**transaction)

@app.post("/api/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionCreate, current_user: dict = Depends(get_current_user)):
    account = next((a for a in accounts_db if a["id"] == transaction_data.account_id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if not account["is_active"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not active")
    
    if transaction_data.transaction_type == TransactionType.DEBIT:
        if account["balance"] < transaction_data.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
        account["balance"] -= transaction_data.amount
    else:
        account["balance"] += transaction_data.amount
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "account_id": transaction_data.account_id,
        "amount": transaction_data.amount,
        "transaction_type": transaction_data.transaction_type,
        "description": transaction_data.description,
        "status": TransactionStatus.COMPLETED,
        "recipient_account_id": transaction_data.recipient_account_id,
        "balance_after": account["balance"],
        "created_at": datetime.utcnow().isoformat()
    }
    transactions_db.append(transaction)
    
    return TransactionResponse(**transaction)

@app.post("/api/transfers", response_model=Dict[str, TransactionResponse], status_code=status.HTTP_201_CREATED)
def create_transfer(transfer_data: TransferRequest, current_user: dict = Depends(get_current_user)):
    from_account = next((a for a in accounts_db if a["id"] == transfer_data.from_account_id), None)
    if not from_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source account not found")
    
    if from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    to_account = next((a for a in accounts_db if a["id"] == transfer_data.to_account_id), None)
    if not to_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination account not found")
    
    if not from_account["is_active"] or not to_account["is_active"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or both accounts are not active")
    
    if from_account["balance"] < transfer_data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
    
    from_account["balance"] -= transfer_data.amount
    to_account["balance"] += transfer_data.amount
    
    debit_transaction_id = str(uuid.uuid4())
    debit_transaction = {
        "id": debit_transaction_id,
        "account_id": transfer_data.from_account_id,
        "amount": transfer_data.amount,
        "transaction_type": TransactionType.TRANSFER,
        "description": f"Transfer to {to_account['account_number']}: {transfer_data.description}",
        "status": TransactionStatus.COMPLETED,
        "recipient_account_id": transfer_data.to_account_id,
        "balance_after": from_account["balance"],
        "created_at": datetime.utcnow().isoformat()
    }
    transactions_db.append(debit_transaction)
    
    credit_transaction_id = str(uuid.uuid4())
    credit_transaction = {
        "id": credit_transaction_id,
        "account_id": transfer_data.to_account_id,
        "amount": transfer_data.amount,
        "transaction_type": TransactionType.TRANSFER,
        "description": f"Transfer from {from_account['account_number']}: {transfer_data.description}",
        "status": TransactionStatus.COMPLETED,
        "recipient_account_id": transfer_data.from_account_id,
        "balance_after": to_account["balance"],
        "created_at": datetime.utcnow().isoformat()
    }
    transactions_db.append(credit_transaction)
    
    return {
        "debit": TransactionResponse(**debit_transaction),
        "credit": TransactionResponse(**credit_transaction)
    }

@app.get("/api/payments", response_model=List[PaymentResponse])
def get_payments(current_user: dict = Depends(get_current_user)):
    user_payments = [p for p in payments_db if p["user_id"] == current_user["id"]]
    user_payments.sort(key=lambda x: x["created_at"], reverse=True)
    return [PaymentResponse(**payment) for payment in user_payments]

@app.get("/api/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: str, current_user: dict = Depends(get_current_user)):
    payment = next((p for p in payments_db if p["id"] == payment_id), None)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    if payment["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return PaymentResponse(**payment)

@app.post("/api/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment_data: PaymentCreate, current_user: dict = Depends(get_current_user)):
    account = next((a for a in accounts_db if a["id"] == payment_data.account_id), None)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if not account["is_active"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not active")
    
    if account["balance"] < payment_data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
    
    payment_id = str(uuid.uuid4())
    payment = {
        "id": payment_id,
        "user_id": current_user["id"],
        "account_id": payment_data.account_id,
        "payee_name": payment_data.payee_name,
        "payee_account": payment_data.payee_account,
        "amount": payment_data.amount,
        "description": payment_data.description,
        "status": PaymentStatus.COMPLETED,
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat()
    }
    payments_db.append(payment)
    
    account["balance"] -= payment_data.amount
    
    transaction_id = str(uuid.uuid4())
    transaction = {
        "id": transaction_id,
        "account_id": payment_data.account_id,
        "amount": payment_data.amount,
        "transaction_type": TransactionType.DEBIT,
        "description": f"Payment to {payment_data.payee_name}: {payment_data.description}",
        "status": TransactionStatus.COMPLETED,
        "recipient_account_id": None,
        "balance_after": account["balance"],
        "created_at": datetime.utcnow().isoformat()
    }
    transactions_db.append(transaction)
    
    return PaymentResponse(**payment)

@app.get("/api/analytics", response_model=AnalyticsResponse)
def get_analytics(account_id: Optional[str] = None, days: int = 30, current_user: dict = Depends(get_current_user)):
    user_account_ids = [a["id"] for a in accounts_db if a["user_id"] == current_user["id"]]
    
    if account_id:
        if account_id not in user_account_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        filter_account_ids = [account_id]
    else:
        filter_account_ids = user_account_ids
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    relevant_transactions = [
        t for t in transactions_db 
        if t["account_id"] in filter_account_ids 
        and datetime.fromisoformat(t["created_at"]) >= cutoff_date
        and t["status"] == TransactionStatus.COMPLETED
    ]
    
    total_income = sum(t["amount"] for t in relevant_transactions if t["transaction_type"] in [TransactionType.CREDIT])
    total_expenses = sum(t["amount"] for t in relevant_transactions if t["transaction_type"] in [TransactionType.DEBIT, TransactionType.TRANSFER] and t["recipient_account_id"])
    
    net_flow = total_income - total_expenses
    transaction_count = len(relevant_transactions)
    average_transaction = sum(t["amount"] for t in relevant_transactions) / transaction_count if transaction_count > 0 else 0.0
    largest_transaction = max((t["amount"] for t in relevant_transactions), default=0.0)
    
    by_category = {}
    for transaction in relevant_transactions:
        description_lower = transaction["description"].lower()
        category = "Other"
        if "salary" in description_lower or "income" in description_lower:
            category = "Income"
        elif "grocery" in description_lower or "food" in description_lower:
            category = "Groceries"
        elif "electric" in description_lower or "utility" in description_lower or "bill" in description_lower:
            category = "Utilities"
        elif "transfer" in description_lower:
            category = "Transfers"
        elif "savings" in description_lower:
            category = "Savings"
        
        if category not in by_category:
            by_category[category] = 0.0
        by_category[category] += transaction["amount"]
    
    return AnalyticsResponse(
        total_income=total_income,
        total_expenses=total_expenses,
        net_flow=net_flow,
        transaction_count=transaction_count,
        average_transaction=average_transaction,
        largest_transaction=largest_transaction,
        by_category=by_category
    )

@app.get("/api/budgets", response_model=List[BudgetResponse])
def get_budgets(current_user: dict = Depends(get_current_user)):
    user_budgets = [b for b in budgets_db if b["user_id"] == current_user["id"]]
    return [BudgetResponse(**budget) for budget in user_budgets]

@app.get("/api/budgets/{budget_id}", response_model=BudgetResponse)
def get_budget(budget_id: str, current_user: dict = Depends(get_current_user)):
    budget = next((b for b in budgets_db if b["id"] == budget_id), None)
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    if budget["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return BudgetResponse(**budget)

@app.post("/api/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(budget_data: BudgetCreate, current_user: dict = Depends(get_current_user)):
    budget_id = str(uuid.uuid4())
    budget = {
        "id": budget_id,
        "user_id": current_user["id"],
        "category": budget_data.category,
        "amount": budget_data.amount,
        "spent": 0.0,
        "remaining": budget_data.amount,
        "period": budget_data.period,
        "created_at": datetime.utcnow().isoformat()
    }
    budgets_db.append(budget)
    return BudgetResponse(**budget)

@app.put("/api/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: str, budget_data: BudgetCreate, current_user: dict = Depends(get_current_user)):
    budget = next((b for b in budgets_db if b["id"] == budget_id), None)
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    if budget["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    budget["category"] = budget_data.category
    budget["amount"] = budget_data.amount
    budget["remaining"] = budget_data.amount - budget["spent"]
    budget["period"] = budget_data.period
    
    return BudgetResponse(**budget)

@app.delete("/api/budgets/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: str, current_user: dict = Depends(get_current_user)):
    budget = next((b for b in budgets_db if b["id"] == budget_id), None)
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    if budget["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    budgets_db.remove(budget)
    return None