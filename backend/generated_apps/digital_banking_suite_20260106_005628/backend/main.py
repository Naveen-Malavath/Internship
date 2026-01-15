from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import secrets
import hashlib
from decimal import Decimal

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

class AccountResponse(BaseModel):
    id: int
    user_id: int
    account_number: str
    account_type: str
    balance: float
    currency: str
    status: str
    created_at: str

class CreateAccountRequest(BaseModel):
    account_type: str
    currency: str

class TransactionRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    from_account_id: int
    to_account_id: int
    amount: float
    currency: str
    description: Optional[str]
    status: str
    created_at: str

class PaymentRequest(BaseModel):
    account_id: int
    payee_name: str
    payee_account: str
    amount: float
    payment_type: str
    description: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    account_id: int
    payee_name: str
    payee_account: str
    amount: float
    payment_type: str
    description: Optional[str]
    status: str
    reference_number: str
    created_at: str

class BeneficiaryRequest(BaseModel):
    account_id: int
    beneficiary_name: str
    beneficiary_account: str
    bank_name: str
    nickname: Optional[str] = None

class BeneficiaryResponse(BaseModel):
    id: int
    account_id: int
    beneficiary_name: str
    beneficiary_account: str
    bank_name: str
    nickname: Optional[str]
    created_at: str

class AccountAnalytics(BaseModel):
    account_id: int
    total_income: float
    total_expenses: float
    transaction_count: int
    average_transaction: float
    balance: float
    period: str

class AuthToken(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# In-memory storage
users_db = []
accounts_db = []
transactions_db = []
payments_db = []
beneficiaries_db = []
sessions_db = {}

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_urlsafe(32)

def generate_account_number() -> str:
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(12)])

def generate_reference_number() -> str:
    import random
    return 'REF' + ''.join([str(random.randint(0, 9)) for _ in range(10)])

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

def get_current_timestamp() -> str:
    return datetime.utcnow().isoformat()

# Seed data
users_db.append({
    "id": 1,
    "email": "john.doe@example.com",
    "password": hash_password("password123"),
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "created_at": "2024-01-01T10:00:00"
})

users_db.append({
    "id": 2,
    "email": "jane.smith@example.com",
    "password": hash_password("password456"),
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "+1234567891",
    "created_at": "2024-01-02T10:00:00"
})

accounts_db.append({
    "id": 1,
    "user_id": 1,
    "account_number": "100000000001",
    "account_type": "checking",
    "balance": 5000.00,
    "currency": "USD",
    "status": "active",
    "created_at": "2024-01-01T11:00:00"
})

accounts_db.append({
    "id": 2,
    "user_id": 1,
    "account_number": "100000000002",
    "account_type": "savings",
    "balance": 15000.00,
    "currency": "USD",
    "status": "active",
    "created_at": "2024-01-01T11:30:00"
})

accounts_db.append({
    "id": 3,
    "user_id": 2,
    "account_number": "100000000003",
    "account_type": "checking",
    "balance": 3000.00,
    "currency": "USD",
    "status": "active",
    "created_at": "2024-01-02T11:00:00"
})

transactions_db.append({
    "id": 1,
    "from_account_id": 1,
    "to_account_id": 2,
    "amount": 500.00,
    "currency": "USD",
    "description": "Internal transfer to savings",
    "status": "completed",
    "created_at": "2024-01-05T14:30:00"
})

transactions_db.append({
    "id": 2,
    "from_account_id": 2,
    "to_account_id": 3,
    "amount": 200.00,
    "currency": "USD",
    "description": "Payment to Jane",
    "status": "completed",
    "created_at": "2024-01-06T09:15:00"
})

payments_db.append({
    "id": 1,
    "account_id": 1,
    "payee_name": "Electric Company",
    "payee_account": "ELEC123456",
    "amount": 150.00,
    "payment_type": "bill_payment",
    "description": "Monthly electricity bill",
    "status": "completed",
    "reference_number": "REF1234567890",
    "created_at": "2024-01-10T10:00:00"
})

beneficiaries_db.append({
    "id": 1,
    "account_id": 1,
    "beneficiary_name": "Jane Smith",
    "beneficiary_account": "100000000003",
    "bank_name": "Digital Bank",
    "nickname": "Jane",
    "created_at": "2024-01-03T12:00:00"
})

# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": get_current_timestamp(),
        "service": "Digital Banking Suite"
    }

# Authentication endpoints
@app.post("/api/auth/register", response_model=AuthToken, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister):
    if any(u["email"] == user_data.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = max([u["id"] for u in users_db], default=0) + 1
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "created_at": get_current_timestamp()
    }
    users_db.append(new_user)
    
    token = generate_token()
    sessions_db[token] = user_id
    
    user_response = UserResponse(
        id=new_user["id"],
        email=new_user["email"],
        first_name=new_user["first_name"],
        last_name=new_user["last_name"],
        phone=new_user["phone"],
        created_at=new_user["created_at"]
    )
    
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
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        phone=user["phone"],
        created_at=user["created_at"]
    )
    
    return AuthToken(
        access_token=token,
        token_type="bearer",
        user=user_response
    )

@app.post("/api/auth/logout")
def logout(current_user: dict = Depends(get_current_user), authorization: str = Header(None)):
    token = authorization.replace("Bearer ", "")
    if token in sessions_db:
        del sessions_db[token]
    return {"message": "Logged out successfully"}

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

# Account endpoints
@app.get("/api/accounts", response_model=List[AccountResponse])
def get_accounts(current_user: dict = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == current_user["id"]]
    return [AccountResponse(**acc) for acc in user_accounts]

@app.get("/api/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, current_user: dict = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return AccountResponse(**account)

@app.post("/api/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account_data: CreateAccountRequest, current_user: dict = Depends(get_current_user)):
    if account_data.account_type not in ["checking", "savings", "business"]:
        raise HTTPException(status_code=400, detail="Invalid account type")
    
    account_id = max([acc["id"] for acc in accounts_db], default=0) + 1
    new_account = {
        "id": account_id,
        "user_id": current_user["id"],
        "account_number": generate_account_number(),
        "account_type": account_data.account_type,
        "balance": 0.0,
        "currency": account_data.currency,
        "status": "active",
        "created_at": get_current_timestamp()
    }
    accounts_db.append(new_account)
    return AccountResponse(**new_account)

@app.put("/api/accounts/{account_id}/status")
def update_account_status(account_id: int, status_value: str, current_user: dict = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    if status_value not in ["active", "frozen", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    account["status"] = status_value
    return {"message": "Account status updated", "status": status_value}

# Transaction endpoints
@app.get("/api/transactions", response_model=List[TransactionResponse])
def get_transactions(account_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    user_account_ids = [acc["id"] for acc in accounts_db if acc["user_id"] == current_user["id"]]
    
    if account_id:
        if account_id not in user_account_ids:
            raise HTTPException(status_code=403, detail="Access denied")
        filtered_transactions = [
            t for t in transactions_db 
            if t["from_account_id"] == account_id or t["to_account_id"] == account_id
        ]
    else:
        filtered_transactions = [
            t for t in transactions_db 
            if t["from_account_id"] in user_account_ids or t["to_account_id"] in user_account_ids
        ]
    
    return [TransactionResponse(**t) for t in filtered_transactions]

@app.get("/api/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, current_user: dict = Depends(get_current_user)):
    transaction = next((t for t in transactions_db if t["id"] == transaction_id), None)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    user_account_ids = [acc["id"] for acc in accounts_db if acc["user_id"] == current_user["id"]]
    if transaction["from_account_id"] not in user_account_ids and transaction["to_account_id"] not in user_account_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return TransactionResponse(**transaction)

@app.post("/api/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionRequest, current_user: dict = Depends(get_current_user)):
    from_account = next((acc for acc in accounts_db if acc["id"] == transaction_data.from_account_id), None)
    to_account = next((acc for acc in accounts_db if acc["id"] == transaction_data.to_account_id), None)
    
    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if from_account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if from_account["status"] != "active":
        raise HTTPException(status_code=400, detail="From account is not active")
    
    if from_account["balance"] < transaction_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    if transaction_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    from_account["balance"] -= transaction_data.amount
    to_account["balance"] += transaction_data.amount
    
    transaction_id = max([t["id"] for t in transactions_db], default=0) + 1
    new_transaction = {
        "id": transaction_id,
        "from_account_id": transaction_data.from_account_id,
        "to_account_id": transaction_data.to_account_id,
        "amount": transaction_data.amount,
        "currency": from_account["currency"],
        "description": transaction_data.description,
        "status": "completed",
        "created_at": get_current_timestamp()
    }
    transactions_db.append(new_transaction)
    
    return TransactionResponse(**new_transaction)

# Payment endpoints
@app.get("/api/payments", response_model=List[PaymentResponse])
def get_payments(account_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    user_account_ids = [acc["id"] for acc in accounts_db if acc["user_id"] == current_user["id"]]
    
    if account_id:
        if account_id not in user_account_ids:
            raise HTTPException(status_code=403, detail="Access denied")
        filtered_payments = [p for p in payments_db if p["account_id"] == account_id]
    else:
        filtered_payments = [p for p in payments_db if p["account_id"] in user_account_ids]
    
    return [PaymentResponse(**p) for p in filtered_payments]

@app.post("/api/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment_data: PaymentRequest, current_user: dict = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == payment_data.account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if account["status"] != "active":
        raise HTTPException(status_code=400, detail="Account is not active")
    
    if account["balance"] < payment_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    if payment_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if payment_data.payment_type not in ["bill_payment", "merchant_payment", "online_payment"]:
        raise HTTPException(status_code=400, detail="Invalid payment type")
    
    account["balance"] -= payment_data.amount
    
    payment_id = max([p["id"] for p in payments_db], default=0) + 1
    new_payment = {
        "id": payment_id,
        "account_id": payment_data.account_id,
        "payee_name": payment_data.payee_name,
        "payee_account": payment_data.payee_account,
        "amount": payment_data.amount,
        "payment_type": payment_data.payment_type,
        "description": payment_data.description,
        "status": "completed",
        "reference_number": generate_reference_number(),
        "created_at": get_current_timestamp()
    }
    payments_db.append(new_payment)
    
    return PaymentResponse(**new_payment)

# Beneficiary endpoints
@app.get("/api/beneficiaries", response_model=List[BeneficiaryResponse])
def get_beneficiaries(account_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    user_account_ids = [acc["id"] for acc in accounts_db if acc["user_id"] == current_user["id"]]
    
    if account_id:
        if account_id not in user_account_ids:
            raise HTTPException(status_code=403, detail="Access denied")
        filtered_beneficiaries = [b for b in beneficiaries_db if b["account_id"] == account_id]
    else:
        filtered_beneficiaries = [b for b in beneficiaries_db if b["account_id"] in user_account_ids]
    
    return [BeneficiaryResponse(**b) for b in filtered_beneficiaries]

@app.post("/api/beneficiaries", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiary(beneficiary_data: BeneficiaryRequest, current_user: dict = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == beneficiary_data.account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    beneficiary_id = max([b["id"] for b in beneficiaries_db], default=0) + 1
    new_beneficiary = {
        "id": beneficiary_id,
        "account_id": beneficiary_data.account_id,
        "beneficiary_name": beneficiary_data.beneficiary_name,
        "beneficiary_account": beneficiary_data.beneficiary_account,
        "bank_name": beneficiary_data.bank_name,
        "nickname": beneficiary_data.nickname,
        "created_at": get_current_timestamp()
    }
    beneficiaries_db.append(new_beneficiary)
    
    return BeneficiaryResponse(**new_beneficiary)

@app.delete("/api/beneficiaries/{beneficiary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_beneficiary(beneficiary_id: int, current_user: dict = Depends(get_current_user)):
    beneficiary = next((b for b in beneficiaries_db if b["id"] == beneficiary_id), None)
    
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    
    account = next((acc for acc in accounts_db if acc["id"] == beneficiary["account_id"]), None)
    if not account or account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    beneficiaries_db.remove(beneficiary)
    return None

# Analytics endpoints
@app.get("/api/analytics/account/{account_id}", response_model=AccountAnalytics)
def get_account_analytics(account_id: int, period: str = "monthly", current_user: dict = Depends(get_current_user)):
    account = next((acc for acc in accounts_db if acc["id"] == account_id), None)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account_transactions = [
        t for t in transactions_db 
        if t["from_account_id"] == account_id or t["to_account_id"] == account_id
    ]
    
    total_income = sum(t["amount"] for t in account_transactions if t["to_account_id"] == account_id)
    total_expenses = sum(t["amount"] for t in account_transactions if t["from_account_id"] == account_id)
    
    account_payments = [p for p in payments_db if p["account_id"] == account_id]
    total_expenses += sum(p["amount"] for p in account_payments)
    
    transaction_count = len(account_transactions) + len(account_payments)
    average_transaction = (total_income + total_expenses) / transaction_count if transaction_count > 0 else 0.0
    
    return AccountAnalytics(
        account_id=account_id,
        total_income=total_income,
        total_expenses=total_expenses,
        transaction_count=transaction_count,
        average_transaction=average_transaction,
        balance=account["balance"],
        period=period
    )

@app.get("/api/analytics/overview", response_model=Dict)
def get_overview_analytics(current_user: dict = Depends(get_current_user)):
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == current_user["id"]]
    user_account_ids = [acc["id"] for acc in user_accounts]
    
    total_balance = sum(acc["balance"] for acc in user_accounts)
    
    user_transactions = [
        t for t in transactions_db 
        if t["from_account_id"] in user_account_ids or t["to_account_id"] in user_account_ids
    ]
    
    total_income = sum(
        t["amount"] for t in user_transactions 
        if t["to_account_id"] in user_account_ids and t["from_account_id"] not in user_account_ids
    )
    
    total_expenses = sum(
        t["amount"] for t in user_transactions 
        if t["from_account_id"] in user_account_ids and t["to_account_id"] not in user_account_ids
    )
    
    user_payments = [p for p in payments_db if p["account_id"] in user_account_ids]
    total_expenses += sum(p["amount"] for p in user_payments)
    
    return {
        "total_balance": total_balance,
        "total_accounts": len(user_accounts),
        "total_income": total_income,
        "total_expenses": total_expenses,
        "total_transactions": len(user_transactions) + len(user_payments),
        "net_flow": total_income - total_expenses
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)