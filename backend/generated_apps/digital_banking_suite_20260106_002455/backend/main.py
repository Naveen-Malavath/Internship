from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import secrets
import hashlib
from enum import Enum

app = FastAPI(
    title="Digital Banking Suite",
    description="Secure, personalised banking experience with account management, payments, and analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    PAYMENT = "PAYMENT"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AccountType(str, Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    BUSINESS = "BUSINESS"


class UserRegister(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: str
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class AccountCreate(BaseModel):
    account_type: AccountType
    account_name: str
    initial_balance: float = 0.0


class AccountResponse(BaseModel):
    id: int
    user_id: int
    account_number: str
    account_type: AccountType
    account_name: str
    balance: float
    currency: str
    status: str
    created_at: str


class TransferRequest(BaseModel):
    from_account_id: int
    to_account_number: str
    amount: float
    description: Optional[str] = None


class PaymentRequest(BaseModel):
    account_id: int
    recipient_name: str
    recipient_account: str
    amount: float
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    account_id: int
    transaction_type: TransactionType
    amount: float
    balance_after: float
    description: Optional[str] = None
    reference_number: str
    status: TransactionStatus
    created_at: str
    completed_at: Optional[str] = None


class BalanceUpdate(BaseModel):
    amount: float
    transaction_type: TransactionType
    description: Optional[str] = None


class AnalyticsResponse(BaseModel):
    total_accounts: int
    total_balance: float
    total_transactions: int
    spending_by_category: Dict[str, float]
    income_vs_expense: Dict[str, float]
    monthly_summary: List[Dict[str, any]]


class BeneficiaryCreate(BaseModel):
    name: str
    account_number: str
    bank_name: str
    nickname: Optional[str] = None


class BeneficiaryResponse(BaseModel):
    id: int
    user_id: int
    name: str
    account_number: str
    bank_name: str
    nickname: Optional[str] = None
    created_at: str


users_db = []
accounts_db = []
transactions_db = []
tokens_db = {}
beneficiaries_db = []

user_id_counter = 1
account_id_counter = 1
transaction_id_counter = 1
beneficiary_id_counter = 1


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def generate_account_number() -> str:
    return str(secrets.randbelow(9000000000) + 1000000000)


def generate_reference_number() -> str:
    return f"TXN{secrets.randbelow(900000) + 100000}"


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    user_id = tokens_db.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


seed_user_1 = {
    "id": 1,
    "email": "john.doe@example.com",
    "password": hash_password("password123"),
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "created_at": "2024-01-15T10:00:00Z"
}

seed_user_2 = {
    "id": 2,
    "email": "jane.smith@example.com",
    "password": hash_password("securepass456"),
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "+1987654321",
    "created_at": "2024-02-20T14:30:00Z"
}

seed_user_3 = {
    "id": 3,
    "email": "bob.wilson@example.com",
    "password": hash_password("mypassword789"),
    "first_name": "Bob",
    "last_name": "Wilson",
    "phone": "+1122334455",
    "created_at": "2024-03-10T09:15:00Z"
}

users_db.extend([seed_user_1, seed_user_2, seed_user_3])
user_id_counter = 4

seed_account_1 = {
    "id": 1,
    "user_id": 1,
    "account_number": "1234567890",
    "account_type": AccountType.CHECKING,
    "account_name": "Main Checking",
    "balance": 5000.00,
    "currency": "USD",
    "status": "ACTIVE",
    "created_at": "2024-01-15T10:05:00Z"
}

seed_account_2 = {
    "id": 2,
    "user_id": 1,
    "account_number": "1234567891",
    "account_type": AccountType.SAVINGS,
    "account_name": "Emergency Savings",
    "balance": 15000.00,
    "currency": "USD",
    "status": "ACTIVE",
    "created_at": "2024-01-15T10:10:00Z"
}

seed_account_3 = {
    "id": 3,
    "user_id": 2,
    "account_number": "2345678901",
    "account_type": AccountType.CHECKING,
    "account_name": "Personal Account",
    "balance": 8500.00,
    "currency": "USD",
    "status": "ACTIVE",
    "created_at": "2024-02-20T14:35:00Z"
}

seed_account_4 = {
    "id": 4,
    "user_id": 3,
    "account_number": "3456789012",
    "account_type": AccountType.BUSINESS,
    "account_name": "Business Operations",
    "balance": 25000.00,
    "currency": "USD",
    "status": "ACTIVE",
    "created_at": "2024-03-10T09:20:00Z"
}

accounts_db.extend([seed_account_1, seed_account_2, seed_account_3, seed_account_4])
account_id_counter = 5

seed_transaction_1 = {
    "id": 1,
    "account_id": 1,
    "transaction_type": TransactionType.DEPOSIT,
    "amount": 1000.00,
    "balance_after": 5000.00,
    "description": "Salary deposit",
    "reference_number": "TXN100001",
    "status": TransactionStatus.COMPLETED,
    "created_at": "2024-01-20T08:00:00Z",
    "completed_at": "2024-01-20T08:00:05Z"
}

seed_transaction_2 = {
    "id": 2,
    "account_id": 1,
    "transaction_type": TransactionType.PAYMENT,
    "amount": 150.00,
    "balance_after": 4850.00,
    "description": "Electricity bill payment",
    "reference_number": "TXN100002",
    "status": TransactionStatus.COMPLETED,
    "created_at": "2024-01-22T15:30:00Z",
    "completed_at": "2024-01-22T15:30:03Z"
}

seed_transaction_3 = {
    "id": 3,
    "account_id": 3,
    "transaction_type": TransactionType.WITHDRAWAL,
    "amount": 500.00,
    "balance_after": 8000.00,
    "description": "ATM withdrawal",
    "reference_number": "TXN100003",
    "status": TransactionStatus.COMPLETED,
    "created_at": "2024-02-25T12:00:00Z",
    "completed_at": "2024-02-25T12:00:02Z"
}

transactions_db.extend([seed_transaction_1, seed_transaction_2, seed_transaction_3])
transaction_id_counter = 4

seed_beneficiary_1 = {
    "id": 1,
    "user_id": 1,
    "name": "Jane Smith",
    "account_number": "2345678901",
    "bank_name": "Digital Banking Suite",
    "nickname": "Sister Jane",
    "created_at": "2024-01-16T11:00:00Z"
}

beneficiaries_db.append(seed_beneficiary_1)
beneficiary_id_counter = 2


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Digital Banking Suite",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister):
    global user_id_counter
    
    if any(u["email"] == user_data.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = {
        "id": user_id_counter,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    users_db.append(new_user)
    user_id_counter += 1
    
    return UserResponse(
        id=new_user["id"],
        email=new_user["email"],
        first_name=new_user["first_name"],
        last_name=new_user["last_name"],
        phone=new_user["phone"],
        created_at=new_user["created_at"]
    )


@app.post("/api/auth/login", response_model=TokenResponse)
def login_user(credentials: UserLogin):
    hashed_pass = hash_password(credentials.password)
    user = next((u for u in users_db if u["email"] == credentials.email and u["password"] == hashed_pass), None)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = generate_token()
    tokens_db[token] = user["id"]
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        phone=user["phone"],
        created_at=user["created_at"]
    )
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user_response
    )


@app.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(current_user: dict = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token in tokens_db:
        del tokens_db[token]
    return None


@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        phone=current_user["phone"],
        created_at=current_user["created_at"]
    )


@app.post("/api/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account_data: AccountCreate, current_user: dict = Depends(get_current_user)):
    global account_id_counter
    
    account_number = generate_account_number()
    
    new_account = {
        "id": account_id_counter,
        "user_id": current_user["id"],
        "account_number": account_number,
        "account_type": account_data.account_type,
        "account_name": account_data.account_name,
        "balance": account_data.initial_balance,
        "currency": "USD",
        "status": "ACTIVE",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    accounts_db.append(new_account)
    account_id_counter += 1
    
    return AccountResponse(**new_account)


@app.get("/api/accounts", response_model=List[AccountResponse])
def get_user_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == current_user["id"]]
    return [AccountResponse(**acc) for acc in user_accounts]


@app.get("/api/accounts/{account_id}", response_model=AccountResponse)
def get_account_details(account_id: int, current_user: dict = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id and acc["user_id"] == current_user["id"]), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return AccountResponse(**account)


@app.put("/api/accounts/{account_id}/balance", response_model=AccountResponse)
def update_account_balance(account_id: int, balance_update: BalanceUpdate, current_user: dict = Depends(get_current_user)):
    global transaction_id_counter
    
    account = next((acc for acc in accounts_db if acc["id"] == account_id and acc["user_id"] == current_user["id"]), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if balance_update.transaction_type == TransactionType.WITHDRAWAL and account["balance"] < balance_update.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    if balance_update.transaction_type in [TransactionType.DEPOSIT, TransactionType.TRANSFER]:
        account["balance"] += balance_update.amount
    else:
        account["balance"] -= balance_update.amount
    
    transaction = {
        "id": transaction_id_counter,
        "account_id": account_id,
        "transaction_type": balance_update.transaction_type,
        "amount": balance_update.amount,
        "balance_after": account["balance"],
        "description": balance_update.description,
        "reference_number": generate_reference_number(),
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "completed_at": datetime.utcnow().isoformat() + "Z"
    }
    
    transactions_db.append(transaction)
    transaction_id_counter += 1
    
    return AccountResponse(**account)


@app.post("/api/transfers", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transfer(transfer: TransferRequest, current_user: dict = Depends(get_current_user)):
    global transaction_id_counter
    
    from_account = next((acc for acc in accounts_db if acc["id"] == transfer.from_account_id and acc["user_id"] == current_user["id"]), None)
    
    if not from_account:
        raise HTTPException(status_code=404, detail="Source account not found")
    
    if from_account["balance"] < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    to_account = next((acc for acc in accounts_db if acc["account_number"] == transfer.to_account_number), None)
    
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    
    from_account["balance"] -= transfer.amount
    to_account["balance"] += transfer.amount
    
    transaction = {
        "id": transaction_id_counter,
        "account_id": transfer.from_account_id,
        "transaction_type": TransactionType.TRANSFER,
        "amount": transfer.amount,
        "balance_after": from_account["balance"],
        "description": transfer.description or f"Transfer to {transfer.to_account_number}",
        "reference_number": generate_reference_number(),
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "completed_at": datetime.utcnow().isoformat() + "Z"
    }
    
    transactions_db.append(transaction)
    transaction_id_counter += 1
    
    return TransactionResponse(**transaction)


@app.post("/api/payments", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentRequest, current_user: dict = Depends(get_current_user)):
    global transaction_id_counter
    
    account = next((acc for acc in accounts_db if acc["id"] == payment.account_id and acc["user_id"] == current_user["id"]), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["balance"] < payment.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    account["balance"] -= payment.amount
    
    transaction = {
        "id": transaction_id_counter,
        "account_id": payment.account_id,
        "transaction_type": TransactionType.PAYMENT,
        "amount": payment.amount,
        "balance_after": account["balance"],
        "description": payment.description or f"Payment to {payment.recipient_name}",
        "reference_number": generate_reference_number(),
        "status": TransactionStatus.COMPLETED,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "completed_at": datetime.utcnow().isoformat() + "Z"
    }
    
    transactions_db.append(transaction)
    transaction_id_counter += 1
    
    return TransactionResponse(**transaction)


@app.get("/api/transactions", response_model=List[TransactionResponse])
def get_transactions(
    account_id: Optional[int] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    user_account_ids = [acc["id"] for acc in accounts_db if acc["user_id"] == current_user["id"]]
    
    filtered_transactions = [
        txn for txn in transactions_db
        if txn["account_id"] in user_account_ids
    ]
    
    if account_id:
        if account_id not in user_account_ids:
            raise HTTPException(status_code=403, detail="Access denied to this account")
        filtered_transactions = [txn for txn in filtered_transactions if txn["account_id"] == account_id]
    
    filtered_transactions.sort(key=lambda x: x["created_at"], reverse=True)
    
    return [TransactionResponse(**txn) for txn in filtered_transactions[:limit]]


@app.get("/api/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction_details(transaction_id: int, current_user: dict = Depends(get_current_user)):
    user_account_ids = [acc["id"] for acc in accounts_db if acc["user_id"] == current_user["id"]]
    
    transaction = next((txn for txn in transactions_db if txn["id"] == transaction_id and txn["account_id"] in user_account_ids), None)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return TransactionResponse(**transaction)


@app.get("/api/analytics", response_model=AnalyticsResponse)
def get_analytics(current_user: dict = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == current_user["id"]]
    user_account_ids = [acc["id"] for acc in user_accounts]
    user_transactions = [txn for txn in transactions_db if txn["account_id"] in user_account_ids]
    
    total_accounts = len(user_accounts)
    total_balance = sum(acc["balance"] for acc in user_accounts)
    total_transactions = len(user_transactions)
    
    income = sum(txn["amount"] for txn in user_transactions if txn["transaction_type"] == TransactionType.DEPOSIT)
    expense = sum(txn["amount"] for txn in user_transactions if txn["transaction_type"] in [TransactionType.WITHDRAWAL, TransactionType.PAYMENT, TransactionType.TRANSFER])
    
    spending_by_category = {
        "payments": sum(txn["amount"] for txn in user_transactions if txn["transaction_type"] == TransactionType.PAYMENT),
        "transfers": sum(txn["amount"] for txn in user_transactions if txn["transaction_type"] == TransactionType.TRANSFER),
        "withdrawals": sum(txn["amount"] for txn in user_transactions if txn["transaction_type"] == TransactionType.WITHDRAWAL)
    }
    
    income_vs_expense = {
        "income": income,
        "expense": expense,
        "net": income - expense
    }
    
    monthly_summary = []
    months = set()
    for txn in user_transactions:
        month = txn["created_at"][:7]
        months.add(month)
    
    for month in sorted(months):
        month_txns = [txn for txn in user_transactions if txn["created_at"].startswith(month)]
        month_income = sum(txn["amount"] for txn in month_txns if txn["transaction_type"] == TransactionType.DEPOSIT)
        month_expense = sum(txn["amount"] for txn in month_txns if txn["transaction_type"] in [TransactionType.WITHDRAWAL, TransactionType.PAYMENT, TransactionType.TRANSFER])
        
        monthly_summary.append({
            "month": month,
            "income": month_income,
            "expense": month_expense,
            "transactions": len(month_txns)
        })
    
    return AnalyticsResponse(
        total_accounts=total_accounts,
        total_balance=total_balance,
        total_transactions=total_transactions,
        spending_by_category=spending_by_category,
        income_vs_expense=income_vs_expense,
        monthly_summary=monthly_summary
    )


@app.post("/api/beneficiaries", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiary(beneficiary_data: BeneficiaryCreate, current_user: dict = Depends(get_current_user)):
    global beneficiary_id_counter
    
    new_beneficiary = {
        "id": beneficiary_id_counter,
        "user_id": current_user["id"],
        "name": beneficiary_data.name,
        "account_number": beneficiary_data.account_number,
        "bank_name": beneficiary_data.bank_name,
        "nickname": beneficiary_data.nickname,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    beneficiaries_db.append(new_beneficiary)
    beneficiary_id_counter += 1
    
    return BeneficiaryResponse(**new_beneficiary)


@app.get("/api/beneficiaries", response_model=List[BeneficiaryResponse])
def get_beneficiaries(current_user: dict = Depends(get_current_user)):
    user_beneficiaries = [ben for ben in beneficiaries_db if ben["user_id"] == current_user["id"]]
    return [BeneficiaryResponse(**ben) for ben in user_beneficiaries]


@app.delete("/api/beneficiaries/{beneficiary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_beneficiary(beneficiary_id: int, current_user: dict = Depends(get_current_user)):
    beneficiary = next((ben for ben in beneficiaries_db if ben["id"] == beneficiary_id and ben["user_id"] == current_user["id"]), None)
    
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    
    beneficiaries_db.remove(beneficiary)
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)