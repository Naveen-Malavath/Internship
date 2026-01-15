from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid
import secrets

app = FastAPI(title="Digital Banking Suite", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: str

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Account(BaseModel):
    id: str
    user_id: str
    account_number: str
    account_type: str
    balance: float
    currency: str
    created_at: str
    status: str

class AccountCreate(BaseModel):
    account_type: str
    currency: str

class Transaction(BaseModel):
    id: str
    account_id: str
    transaction_type: str
    amount: float
    currency: str
    description: str
    timestamp: str
    status: str
    balance_after: float

class TransactionCreate(BaseModel):
    account_id: str
    transaction_type: str
    amount: float
    description: str

class Transfer(BaseModel):
    id: str
    from_account_id: str
    to_account_id: str
    amount: float
    currency: str
    description: str
    timestamp: str
    status: str

class TransferCreate(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float
    description: Optional[str] = ""

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

class PaymentSchedule(BaseModel):
    id: str
    user_id: str
    account_id: str
    beneficiary_id: str
    amount: float
    frequency: str
    next_payment: str
    status: str

class PaymentScheduleCreate(BaseModel):
    account_id: str
    beneficiary_id: str
    amount: float
    frequency: str

class Analytics(BaseModel):
    user_id: str
    total_balance: float
    total_accounts: int
    monthly_spending: float
    monthly_income: float
    top_categories: List[Dict[str, float]]
    recent_transactions: List[Transaction]

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

users_db = []
accounts_db = []
transactions_db = []
transfers_db = []
beneficiaries_db = []
payment_schedules_db = []
sessions_db = {}

def create_sample_data():
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    
    users_db.append({
        "id": user1_id,
        "email": "john.doe@example.com",
        "password": "password123",
        "full_name": "John Doe",
        "created_at": datetime.now().isoformat()
    })
    
    users_db.append({
        "id": user2_id,
        "email": "jane.smith@example.com",
        "password": "password456",
        "full_name": "Jane Smith",
        "created_at": datetime.now().isoformat()
    })
    
    account1_id = str(uuid.uuid4())
    account2_id = str(uuid.uuid4())
    account3_id = str(uuid.uuid4())
    
    accounts_db.append({
        "id": account1_id,
        "user_id": user1_id,
        "account_number": "ACC1001234567",
        "account_type": "checking",
        "balance": 15000.50,
        "currency": "USD",
        "created_at": datetime.now().isoformat(),
        "status": "active"
    })
    
    accounts_db.append({
        "id": account2_id,
        "user_id": user1_id,
        "account_number": "ACC1001234568",
        "account_type": "savings",
        "balance": 50000.00,
        "currency": "USD",
        "created_at": datetime.now().isoformat(),
        "status": "active"
    })
    
    accounts_db.append({
        "id": account3_id,
        "user_id": user2_id,
        "account_number": "ACC2001234569",
        "account_type": "checking",
        "balance": 8500.75,
        "currency": "USD",
        "created_at": datetime.now().isoformat(),
        "status": "active"
    })
    
    transactions_db.append({
        "id": str(uuid.uuid4()),
        "account_id": account1_id,
        "transaction_type": "deposit",
        "amount": 2000.00,
        "currency": "USD",
        "description": "Salary deposit",
        "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
        "status": "completed",
        "balance_after": 15000.50
    })
    
    transactions_db.append({
        "id": str(uuid.uuid4()),
        "account_id": account1_id,
        "transaction_type": "withdrawal",
        "amount": 150.00,
        "currency": "USD",
        "description": "ATM withdrawal",
        "timestamp": (datetime.now() - timedelta(days=3)).isoformat(),
        "status": "completed",
        "balance_after": 13000.50
    })
    
    transactions_db.append({
        "id": str(uuid.uuid4()),
        "account_id": account1_id,
        "transaction_type": "payment",
        "amount": 89.99,
        "currency": "USD",
        "description": "Online shopping",
        "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
        "status": "completed",
        "balance_after": 14910.51
    })
    
    transactions_db.append({
        "id": str(uuid.uuid4()),
        "account_id": account2_id,
        "transaction_type": "deposit",
        "amount": 10000.00,
        "currency": "USD",
        "description": "Transfer from checking",
        "timestamp": (datetime.now() - timedelta(days=10)).isoformat(),
        "status": "completed",
        "balance_after": 50000.00
    })
    
    beneficiary1_id = str(uuid.uuid4())
    beneficiary2_id = str(uuid.uuid4())
    
    beneficiaries_db.append({
        "id": beneficiary1_id,
        "user_id": user1_id,
        "name": "Electric Company",
        "account_number": "UTIL001234",
        "bank_name": "Utility Bank",
        "created_at": datetime.now().isoformat()
    })
    
    beneficiaries_db.append({
        "id": beneficiary2_id,
        "user_id": user1_id,
        "name": "Jane Smith",
        "account_number": "ACC2001234569",
        "bank_name": "Same Bank",
        "created_at": datetime.now().isoformat()
    })
    
    payment_schedules_db.append({
        "id": str(uuid.uuid4()),
        "user_id": user1_id,
        "account_id": account1_id,
        "beneficiary_id": beneficiary1_id,
        "amount": 150.00,
        "frequency": "monthly",
        "next_payment": (datetime.now() + timedelta(days=15)).isoformat(),
        "status": "active"
    })

create_sample_data()

def get_current_user(token: str) -> dict:
    if token not in sessions_db:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return sessions_db[token]

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Digital Banking Suite",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister):
    for user in users_db:
        if user["email"] == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "password": user_data.password,
        "full_name": user_data.full_name,
        "created_at": datetime.now().isoformat()
    }
    users_db.append(new_user)
    
    token = secrets.token_urlsafe(32)
    sessions_db[token] = new_user
    
    user_response = User(
        id=new_user["id"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        created_at=new_user["created_at"]
    )
    
    return Token(access_token=token, token_type="bearer", user=user_response)

@app.post("/api/auth/login", response_model=Token)
def login(credentials: UserLogin):
    for user in users_db:
        if user["email"] == credentials.email and user["password"] == credentials.password:
            token = secrets.token_urlsafe(32)
            sessions_db[token] = user
            
            user_response = User(
                id=user["id"],
                email=user["email"],
                full_name=user["full_name"],
                created_at=user["created_at"]
            )
            
            return Token(access_token=token, token_type="bearer", user=user_response)
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/logout")
def logout(token: str):
    if token in sessions_db:
        del sessions_db[token]
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me", response_model=User)
def get_me(token: str):
    user = get_current_user(token)
    return User(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        created_at=user["created_at"]
    )

@app.get("/api/accounts", response_model=List[Account])
def get_accounts(token: str):
    user = get_current_user(token)
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == user["id"]]
    return user_accounts

@app.get("/api/accounts/{account_id}", response_model=Account)
def get_account(account_id: str, token: str):
    user = get_current_user(token)
    
    for account in accounts_db:
        if account["id"] == account_id:
            if account["user_id"] != user["id"]:
                raise HTTPException(status_code=403, detail="Access denied")
            return account
    
    raise HTTPException(status_code=404, detail="Account not found")

@app.post("/api/accounts", response_model=Account, status_code=status.HTTP_201_CREATED)
def create_account(account_data: AccountCreate, token: str):
    user = get_current_user(token)
    
    account_id = str(uuid.uuid4())
    account_number = f"ACC{user['id'][:4]}{secrets.token_hex(5)}"
    
    new_account = {
        "id": account_id,
        "user_id": user["id"],
        "account_number": account_number,
        "account_type": account_data.account_type,
        "balance": 0.0,
        "currency": account_data.currency,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    accounts_db.append(new_account)
    return new_account

@app.get("/api/transactions", response_model=List[Transaction])
def get_transactions(token: str, account_id: Optional[str] = None):
    user = get_current_user(token)
    
    user_account_ids = [acc["id"] for acc in accounts_db if acc["user_id"] == user["id"]]
    
    filtered_transactions = [
        txn for txn in transactions_db 
        if txn["account_id"] in user_account_ids
    ]
    
    if account_id:
        if account_id not in user_account_ids:
            raise HTTPException(status_code=403, detail="Access denied")
        filtered_transactions = [txn for txn in filtered_transactions if txn["account_id"] == account_id]
    
    return sorted(filtered_transactions, key=lambda x: x["timestamp"], reverse=True)

@app.get("/api/transactions/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: str, token: str):
    user = get_current_user(token)
    user_account_ids = [acc["id"] for acc in accounts_db if acc["user_id"] == user["id"]]
    
    for txn in transactions_db:
        if txn["id"] == transaction_id:
            if txn["account_id"] not in user_account_ids:
                raise HTTPException(status_code=403, detail="Access denied")
            return txn
    
    raise HTTPException(status_code=404, detail="Transaction not found")

@app.post("/api/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(txn_data: TransactionCreate, token: str):
    user = get_current_user(token)
    
    account = None
    for acc in accounts_db:
        if acc["id"] == txn_data.account_id:
            if acc["user_id"] != user["id"]:
                raise HTTPException(status_code=403, detail="Access denied")
            account = acc
            break
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if txn_data.transaction_type in ["withdrawal", "payment"] and account["balance"] < txn_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    if txn_data.transaction_type in ["withdrawal", "payment"]:
        account["balance"] -= txn_data.amount
    elif txn_data.transaction_type == "deposit":
        account["balance"] += txn_data.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")
    
    transaction_id = str(uuid.uuid4())
    new_transaction = {
        "id": transaction_id,
        "account_id": txn_data.account_id,
        "transaction_type": txn_data.transaction_type,
        "amount": txn_data.amount,
        "currency": account["currency"],
        "description": txn_data.description,
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "balance_after": account["balance"]
    }
    
    transactions_db.append(new_transaction)
    return new_transaction

@app.post("/api/transfers", response_model=Transfer, status_code=status.HTTP_201_CREATED)
def create_transfer(transfer_data: TransferCreate, token: str):
    user = get_current_user(token)
    
    from_account = None
    to_account = None
    
    for acc in accounts_db:
        if acc["id"] == transfer_data.from_account_id:
            from_account = acc
        if acc["id"] == transfer_data.to_account_id:
            to_account = acc
    
    if not from_account:
        raise HTTPException(status_code=404, detail="Source account not found")
    
    if not to_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    
    if from_account["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied to source account")
    
    if from_account["balance"] < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    if from_account["currency"] != to_account["currency"]:
        raise HTTPException(status_code=400, detail="Currency mismatch")
    
    from_account["balance"] -= transfer_data.amount
    to_account["balance"] += transfer_data.amount
    
    transfer_id = str(uuid.uuid4())
    new_transfer = {
        "id": transfer_id,
        "from_account_id": transfer_data.from_account_id,
        "to_account_id": transfer_data.to_account_id,
        "amount": transfer_data.amount,
        "currency": from_account["currency"],
        "description": transfer_data.description,
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    }
    
    transfers_db.append(new_transfer)
    
    transactions_db.append({
        "id": str(uuid.uuid4()),
        "account_id": transfer_data.from_account_id,
        "transaction_type": "transfer_out",
        "amount": transfer_data.amount,
        "currency": from_account["currency"],
        "description": f"Transfer to {to_account['account_number']} - {transfer_data.description}",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "balance_after": from_account["balance"]
    })
    
    transactions_db.append({
        "id": str(uuid.uuid4()),
        "account_id": transfer_data.to_account_id,
        "transaction_type": "transfer_in",
        "amount": transfer_data.amount,
        "currency": to_account["currency"],
        "description": f"Transfer from {from_account['account_number']} - {transfer_data.description}",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "balance_after": to_account["balance"]
    })
    
    return new_transfer

@app.get("/api/transfers", response_model=List[Transfer])
def get_transfers(token: str):
    user = get_current_user(token)
    user_account_ids = [acc["id"] for acc in accounts_db if acc["user_id"] == user["id"]]
    
    user_transfers = [
        transfer for transfer in transfers_db
        if transfer["from_account_id"] in user_account_ids or transfer["to_account_id"] in user_account_ids
    ]
    
    return sorted(user_transfers, key=lambda x: x["timestamp"], reverse=True)

@app.get("/api/beneficiaries", response_model=List[Beneficiary])
def get_beneficiaries(token: str):
    user = get_current_user(token)
    user_beneficiaries = [ben for ben in beneficiaries_db if ben["user_id"] == user["id"]]
    return user_beneficiaries

@app.post("/api/beneficiaries", response_model=Beneficiary, status_code=status.HTTP_201_CREATED)
def create_beneficiary(beneficiary_data: BeneficiaryCreate, token: str):
    user = get_current_user(token)
    
    beneficiary_id = str(uuid.uuid4())
    new_beneficiary = {
        "id": beneficiary_id,
        "user_id": user["id"],
        "name": beneficiary_data.name,
        "account_number": beneficiary_data.account_number,
        "bank_name": beneficiary_data.bank_name,
        "created_at": datetime.now().isoformat()
    }
    
    beneficiaries_db.append(new_beneficiary)
    return new_beneficiary

@app.delete("/api/beneficiaries/{beneficiary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_beneficiary(beneficiary_id: str, token: str):
    user = get_current_user(token)
    
    for i, ben in enumerate(beneficiaries_db):
        if ben["id"] == beneficiary_id:
            if ben["user_id"] != user["id"]:
                raise HTTPException(status_code=403, detail="Access denied")
            beneficiaries_db.pop(i)
            return
    
    raise HTTPException(status_code=404, detail="Beneficiary not found")

@app.get("/api/payment-schedules", response_model=List[PaymentSchedule])
def get_payment_schedules(token: str):
    user = get_current_user(token)
    user_schedules = [sched for sched in payment_schedules_db if sched["user_id"] == user["id"]]
    return user_schedules

@app.post("/api/payment-schedules", response_model=PaymentSchedule, status_code=status.HTTP_201_CREATED)
def create_payment_schedule(schedule_data: PaymentScheduleCreate, token: str):
    user = get_current_user(token)
    
    account = None
    for acc in accounts_db:
        if acc["id"] == schedule_data.account_id:
            if acc["user_id"] != user["id"]:
                raise HTTPException(status_code=403, detail="Access denied")
            account = acc
            break
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    beneficiary_exists = any(
        ben["id"] == schedule_data.beneficiary_id and ben["user_id"] == user["id"]
        for ben in beneficiaries_db
    )
    
    if not beneficiary_exists:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    
    if schedule_data.frequency == "weekly":
        next_payment = datetime.now() + timedelta(weeks=1)
    elif schedule_data.frequency == "monthly":
        next_payment = datetime.now() + timedelta(days=30)
    elif schedule_data.frequency == "yearly":
        next_payment = datetime.now() + timedelta(days=365)
    else:
        raise HTTPException(status_code=400, detail="Invalid frequency")
    
    schedule_id = str(uuid.uuid4())
    new_schedule = {
        "id": schedule_id,
        "user_id": user["id"],
        "account_id": schedule_data.account_id,
        "beneficiary_id": schedule_data.beneficiary_id,
        "amount": schedule_data.amount,
        "frequency": schedule_data.frequency,
        "next_payment": next_payment.isoformat(),
        "status": "active"
    }
    
    payment_schedules_db.append(new_schedule)
    return new_schedule

@app.delete("/api/payment-schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_schedule(schedule_id: str, token: str):
    user = get_current_user(token)
    
    for i, sched in enumerate(payment_schedules_db):
        if sched["id"] == schedule_id:
            if sched["user_id"] != user["id"]:
                raise HTTPException(status_code=403, detail="Access denied")
            payment_schedules_db.pop(i)
            return
    
    raise HTTPException(status_code=404, detail="Payment schedule not found")

@app.get("/api/analytics", response_model=Analytics)
def get_analytics(token: str):
    user = get_current_user(token)
    
    user_accounts = [acc for acc in accounts_db if acc["user_id"] == user["id"]]
    total_balance = sum(acc["balance"] for acc in user_accounts)
    total_accounts = len(user_accounts)
    
    user_account_ids = [acc["id"] for acc in user_accounts]
    user_transactions = [txn for txn in transactions_db if txn["account_id"] in user_account_ids]
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_transactions = [
        txn for txn in user_transactions
        if datetime.fromisoformat(txn["timestamp"]) >= thirty_days_ago
    ]
    
    monthly_spending = sum(
        txn["amount"] for txn in recent_transactions
        if txn["transaction_type"] in ["withdrawal", "payment", "transfer_out"]
    )
    
    monthly_income = sum(
        txn["amount"] for txn in recent_transactions
        if txn["transaction_type"] in ["deposit", "transfer_in"]
    )
    
    categories = {}
    for txn in recent_transactions:
        if txn["transaction_type"] in ["payment", "withdrawal"]:
            desc = txn["description"].lower()
            if "shopping" in desc or "store" in desc:
                category = "Shopping"
            elif "restaurant" in desc or "food" in desc:
                category = "Food"
            elif "utility" in desc or "electric" in desc or "water" in desc:
                category = "Utilities"
            elif "transport" in desc or "gas" in desc:
                category = "Transport"
            else:
                category = "Other"
            
            categories[category] = categories.get(category, 0.0) + txn["amount"]
    
    top_categories = [{"category": k, "amount": v} for k, v in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    recent_txns_list = sorted(user_transactions, key=lambda x: x["timestamp"], reverse=True)[:10]
    
    return Analytics(
        user_id=user["id"],
        total_balance=total_balance,
        total_accounts=total_accounts,
        monthly_spending=monthly_spending,
        monthly_income=monthly_income,
        top_categories=top_categories,
        recent_transactions=recent_txns_list
    )