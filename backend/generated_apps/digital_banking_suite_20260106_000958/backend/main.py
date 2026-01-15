from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import secrets
from decimal import Decimal

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


class AccountType(str, Enum):
    SAVINGS = "SAVINGS"
    CHECKING = "CHECKING"
    CREDIT = "CREDIT"


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


class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


class UserRegistration(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    phone: str
    date_of_birth: str
    address: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    first_name: str
    last_name: str
    phone: str
    created_at: str
    role: UserRole


class AuthToken(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class AccountCreate(BaseModel):
    account_type: AccountType
    account_name: str
    initial_balance: float = Field(default=0.0, ge=0)


class AccountResponse(BaseModel):
    account_id: str
    user_id: str
    account_number: str
    account_type: AccountType
    account_name: str
    balance: float
    currency: str
    created_at: str
    is_active: bool


class TransactionCreate(BaseModel):
    from_account_id: str
    to_account_id: Optional[str] = None
    amount: float = Field(..., gt=0)
    transaction_type: TransactionType
    description: Optional[str] = None
    recipient_name: Optional[str] = None


class TransactionResponse(BaseModel):
    transaction_id: str
    from_account_id: str
    to_account_id: Optional[str]
    amount: float
    transaction_type: TransactionType
    status: TransactionStatus
    description: Optional[str]
    recipient_name: Optional[str]
    created_at: str
    completed_at: Optional[str]


class PaymentCreate(BaseModel):
    from_account_id: str
    payee_name: str
    payee_account_number: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = None


class BeneficiaryCreate(BaseModel):
    name: str
    account_number: str
    bank_name: str
    nickname: Optional[str] = None


class BeneficiaryResponse(BaseModel):
    beneficiary_id: str
    user_id: str
    name: str
    account_number: str
    bank_name: str
    nickname: Optional[str]
    created_at: str


class AccountAnalytics(BaseModel):
    account_id: str
    total_deposits: float
    total_withdrawals: float
    total_transactions: int
    average_transaction_amount: float
    largest_transaction: float
    current_balance: float


class UserAnalytics(BaseModel):
    user_id: str
    total_accounts: int
    total_balance: float
    monthly_spending: float
    monthly_income: float
    transaction_count: int


class User:
    def __init__(self, user_id: str, email: str, password: str, first_name: str, 
                 last_name: str, phone: str, date_of_birth: str, address: str, role: UserRole):
        self.user_id = user_id
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.date_of_birth = date_of_birth
        self.address = address
        self.role = role
        self.created_at = datetime.utcnow().isoformat()


class Account:
    def __init__(self, account_id: str, user_id: str, account_number: str, 
                 account_type: AccountType, account_name: str, balance: float):
        self.account_id = account_id
        self.user_id = user_id
        self.account_number = account_number
        self.account_type = account_type
        self.account_name = account_name
        self.balance = balance
        self.currency = "USD"
        self.created_at = datetime.utcnow().isoformat()
        self.is_active = True


class Transaction:
    def __init__(self, transaction_id: str, from_account_id: str, to_account_id: Optional[str],
                 amount: float, transaction_type: TransactionType, description: Optional[str],
                 recipient_name: Optional[str], status: TransactionStatus):
        self.transaction_id = transaction_id
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description
        self.recipient_name = recipient_name
        self.status = status
        self.created_at = datetime.utcnow().isoformat()
        self.completed_at = None if status == TransactionStatus.PENDING else datetime.utcnow().isoformat()


class Beneficiary:
    def __init__(self, beneficiary_id: str, user_id: str, name: str, 
                 account_number: str, bank_name: str, nickname: Optional[str]):
        self.beneficiary_id = beneficiary_id
        self.user_id = user_id
        self.name = name
        self.account_number = account_number
        self.bank_name = bank_name
        self.nickname = nickname
        self.created_at = datetime.utcnow().isoformat()


users_db: List[User] = []
accounts_db: List[Account] = []
transactions_db: List[Transaction] = []
beneficiaries_db: List[Beneficiary] = []
tokens_db: Dict[str, str] = {}


def generate_account_number() -> str:
    return f"{secrets.randbelow(9000000000) + 1000000000}"


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def get_user_by_token(token: str) -> Optional[User]:
    user_id = tokens_db.get(token)
    if not user_id:
        return None
    return next((u for u in users_db if u.user_id == user_id), None)


def get_current_user(authorization: Optional[str] = None) -> User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = parts[1]
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user


user1_id = str(uuid.uuid4())
user2_id = str(uuid.uuid4())
user3_id = str(uuid.uuid4())

user1 = User(
    user_id=user1_id,
    email="john.doe@example.com",
    password="password123",
    first_name="John",
    last_name="Doe",
    phone="+1234567890",
    date_of_birth="1990-05-15",
    address="123 Main St, New York, NY 10001",
    role=UserRole.CUSTOMER
)

user2 = User(
    user_id=user2_id,
    email="jane.smith@example.com",
    password="securepass456",
    first_name="Jane",
    last_name="Smith",
    phone="+1987654321",
    date_of_birth="1985-08-22",
    address="456 Oak Ave, Los Angeles, CA 90001",
    role=UserRole.CUSTOMER
)

user3 = User(
    user_id=user3_id,
    email="admin@digitalbank.com",
    password="admin123",
    first_name="Admin",
    last_name="User",
    phone="+1122334455",
    date_of_birth="1980-01-01",
    address="789 Admin Blvd, Chicago, IL 60601",
    role=UserRole.ADMIN
)

users_db.extend([user1, user2, user3])

account1 = Account(
    account_id=str(uuid.uuid4()),
    user_id=user1_id,
    account_number=generate_account_number(),
    account_type=AccountType.CHECKING,
    account_name="John's Checking",
    balance=5000.00
)

account2 = Account(
    account_id=str(uuid.uuid4()),
    user_id=user1_id,
    account_number=generate_account_number(),
    account_type=AccountType.SAVINGS,
    account_name="John's Savings",
    balance=15000.00
)

account3 = Account(
    account_id=str(uuid.uuid4()),
    user_id=user2_id,
    account_number=generate_account_number(),
    account_type=AccountType.CHECKING,
    account_name="Jane's Checking",
    balance=8500.00
)

account4 = Account(
    account_id=str(uuid.uuid4()),
    user_id=user2_id,
    account_number=generate_account_number(),
    account_type=AccountType.CREDIT,
    account_name="Jane's Credit Card",
    balance=2000.00
)

accounts_db.extend([account1, account2, account3, account4])

transaction1 = Transaction(
    transaction_id=str(uuid.uuid4()),
    from_account_id=account1.account_id,
    to_account_id=None,
    amount=1000.00,
    transaction_type=TransactionType.DEPOSIT,
    description="Salary deposit",
    recipient_name=None,
    status=TransactionStatus.COMPLETED
)

transaction2 = Transaction(
    transaction_id=str(uuid.uuid4()),
    from_account_id=account1.account_id,
    to_account_id=account2.account_id,
    amount=500.00,
    transaction_type=TransactionType.TRANSFER,
    description="Transfer to savings",
    recipient_name=None,
    status=TransactionStatus.COMPLETED
)

transaction3 = Transaction(
    transaction_id=str(uuid.uuid4()),
    from_account_id=account3.account_id,
    to_account_id=None,
    amount=200.00,
    transaction_type=TransactionType.WITHDRAWAL,
    description="ATM withdrawal",
    recipient_name=None,
    status=TransactionStatus.COMPLETED
)

transactions_db.extend([transaction1, transaction2, transaction3])

beneficiary1 = Beneficiary(
    beneficiary_id=str(uuid.uuid4()),
    user_id=user1_id,
    name="Electric Company",
    account_number="9876543210",
    bank_name="Utility Bank",
    nickname="Electric Bill"
)

beneficiary2 = Beneficiary(
    beneficiary_id=str(uuid.uuid4()),
    user_id=user1_id,
    name="Jane Smith",
    account_number=account3.account_number,
    bank_name="Digital Bank",
    nickname="Jane"
)

beneficiaries_db.extend([beneficiary1, beneficiary2])


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Digital Banking Suite"
    }


@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegistration):
    if any(u.email == user_data.email for u in users_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_id = str(uuid.uuid4())
    new_user = User(
        user_id=user_id,
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        date_of_birth=user_data.date_of_birth,
        address=user_data.address,
        role=UserRole.CUSTOMER
    )
    
    users_db.append(new_user)
    
    return UserResponse(
        user_id=new_user.user_id,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        phone=new_user.phone,
        created_at=new_user.created_at,
        role=new_user.role
    )


@app.post("/api/auth/login", response_model=AuthToken)
def login_user(credentials: UserLogin):
    user = next((u for u in users_db if u.email == credentials.email), None)
    
    if not user or user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = generate_token()
    tokens_db[token] = user.user_id
    
    return AuthToken(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            user_id=user.user_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            created_at=user.created_at,
            role=user.role
        )
    )


@app.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(authorization: Optional[str] = None):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        token = parts[1]
        if token in tokens_db:
            del tokens_db[token]
    
    return None


@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_profile(authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        created_at=user.created_at,
        role=user.role
    )


@app.get("/api/accounts", response_model=List[AccountResponse])
def get_user_accounts(authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    user_accounts = [acc for acc in accounts_db if acc.user_id == user.user_id]
    
    return [
        AccountResponse(
            account_id=acc.account_id,
            user_id=acc.user_id,
            account_number=acc.account_number,
            account_type=acc.account_type,
            account_name=acc.account_name,
            balance=acc.balance,
            currency=acc.currency,
            created_at=acc.created_at,
            is_active=acc.is_active
        )
        for acc in user_accounts
    ]


@app.post("/api/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account_data: AccountCreate, authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    account_id = str(uuid.uuid4())
    account_number = generate_account_number()
    
    new_account = Account(
        account_id=account_id,
        user_id=user.user_id,
        account_number=account_number,
        account_type=account_data.account_type,
        account_name=account_data.account_name,
        balance=account_data.initial_balance
    )
    
    accounts_db.append(new_account)
    
    return AccountResponse(
        account_id=new_account.account_id,
        user_id=new_account.user_id,
        account_number=new_account.account_number,
        account_type=new_account.account_type,
        account_name=new_account.account_name,
        balance=new_account.balance,
        currency=new_account.currency,
        created_at=new_account.created_at,
        is_active=new_account.is_active
    )


@app.get("/api/accounts/{account_id}", response_model=AccountResponse)
def get_account_details(account_id: str, authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    account = next((acc for acc in accounts_db if acc.account_id == account_id), None)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if account.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this account"
        )
    
    return AccountResponse(
        account_id=account.account_id,
        user_id=account.user_id,
        account_number=account.account_number,
        account_type=account.account_type,
        account_name=account.account_name,
        balance=account.balance,
        currency=account.currency,
        created_at=account.created_at,
        is_active=account.is_active
    )


@app.get("/api/transactions", response_model=List[TransactionResponse])
def get_user_transactions(
    account_id: Optional[str] = None,
    limit: int = 50,
    authorization: Optional[str] = None
):
    user = get_current_user(authorization)
    
    user_account_ids = {acc.account_id for acc in accounts_db if acc.user_id == user.user_id}
    
    filtered_transactions = [
        t for t in transactions_db
        if t.from_account_id in user_account_ids or t.to_account_id in user_account_ids
    ]
    
    if account_id:
        filtered_transactions = [
            t for t in filtered_transactions
            if t.from_account_id == account_id or t.to_account_id == account_id
        ]
    
    filtered_transactions.sort(key=lambda x: x.created_at, reverse=True)
    filtered_transactions = filtered_transactions[:limit]
    
    return [
        TransactionResponse(
            transaction_id=t.transaction_id,
            from_account_id=t.from_account_id,
            to_account_id=t.to_account_id,
            amount=t.amount,
            transaction_type=t.transaction_type,
            status=t.status,
            description=t.description,
            recipient_name=t.recipient_name,
            created_at=t.created_at,
            completed_at=t.completed_at
        )
        for t in filtered_transactions
    ]


@app.get("/api/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction_details(transaction_id: str, authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    transaction = next((t for t in transactions_db if t.transaction_id == transaction_id), None)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    user_account_ids = {acc.account_id for acc in accounts_db if acc.user_id == user.user_id}
    
    if transaction.from_account_id not in user_account_ids and transaction.to_account_id not in user_account_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this transaction"
        )
    
    return TransactionResponse(
        transaction_id=transaction.transaction_id,
        from_account_id=transaction.from_account_id,
        to_account_id=transaction.to_account_id,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        status=transaction.status,
        description=transaction.description,
        recipient_name=transaction.recipient_name,
        created_at=transaction.created_at,
        completed_at=transaction.completed_at
    )


@app.post("/api/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionCreate, authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    from_account = next((acc for acc in accounts_db if acc.account_id == transaction_data.from_account_id), None)
    
    if not from_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source account not found"
        )
    
    if from_account.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to source account"
        )
    
    if not from_account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source account is not active"
        )
    
    if transaction_data.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER, TransactionType.PAYMENT]:
        if from_account.balance < transaction_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )
    
    to_account = None
    if transaction_data.to_account_id:
        to_account = next((acc for acc in accounts_db if acc.account_id == transaction_data.to_account_id), None)
        if not to_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found"
            )
        if not to_account.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Destination account is not active"
            )
    
    transaction_id = str(uuid.uuid4())
    new_transaction = Transaction(
        transaction_id=transaction_id,
        from_account_id=transaction_data.from_account_id,
        to_account_id=transaction_data.to_account_id,
        amount=transaction_data.amount,
        transaction_type=transaction_data.transaction_type,
        description=transaction_data.description,
        recipient_name=transaction_data.recipient_name,
        status=TransactionStatus.COMPLETED
    )
    
    if transaction_data.transaction_type == TransactionType.DEPOSIT:
        from_account.balance += transaction_data.amount
    elif transaction_data.transaction_type == TransactionType.WITHDRAWAL:
        from_account.balance -= transaction_data.amount
    elif transaction_data.transaction_type == TransactionType.TRANSFER:
        from_account.balance -= transaction_data.amount
        if to_account:
            to_account.balance += transaction_data.amount
    elif transaction_data.transaction_type == TransactionType.PAYMENT:
        from_account.balance -= transaction_data.amount
    
    transactions_db.append(new_transaction)
    
    return TransactionResponse(
        transaction_id=new_transaction.transaction_id,
        from_account_id=new_transaction.from_account_id,
        to_account_id=new_transaction.to_account_id,
        amount=new_transaction.amount,
        transaction_type=new_transaction.transaction_type,
        status=new_transaction.status,
        description=new_transaction.description,
        recipient_name=new_transaction.recipient_name,
        created_at=new_transaction.created_at,
        completed_at=new_transaction.completed_at
    )


@app.post("/api/payments", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def process_payment(payment_data: PaymentCreate, authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    from_account = next((acc for acc in accounts_db if acc.account_id == payment_data.from_account_id), None)
    
    if not from_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source account not found"
        )
    
    if from_account.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to source account"
        )
    
    if not from_account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source account is not active"
        )
    
    if from_account.balance < payment_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds"
        )
    
    transaction_id = str(uuid.uuid4())
    new_transaction = Transaction(
        transaction_id=transaction_id,
        from_account_id=payment_data.from_account_id,
        to_account_id=None,
        amount=payment_data.amount,
        transaction_type=TransactionType.PAYMENT,
        description=payment_data.description,
        recipient_name=payment_data.payee_name,
        status=TransactionStatus.COMPLETED
    )
    
    from_account.balance -= payment_data.amount
    transactions_db.append(new_transaction)
    
    return TransactionResponse(
        transaction_id=new_transaction.transaction_id,
        from_account_id=new_transaction.from_account_id,
        to_account_id=new_transaction.to_account_id,
        amount=new_transaction.amount,
        transaction_type=new_transaction.transaction_type,
        status=new_transaction.status,
        description=new_transaction.description,
        recipient_name=new_transaction.recipient_name,
        created_at=new_transaction.created_at,
        completed_at=new_transaction.completed_at
    )


@app.get("/api/beneficiaries", response_model=List[BeneficiaryResponse])
def get_beneficiaries(authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    user_beneficiaries = [b for b in beneficiaries_db if b.user_id == user.user_id]
    
    return [
        BeneficiaryResponse(
            beneficiary_id=b.beneficiary_id,
            user_id=b.user_id,
            name=b.name,
            account_number=b.account_number,
            bank_name=b.bank_name,
            nickname=b.nickname,
            created_at=b.created_at
        )
        for b in user_beneficiaries
    ]


@app.post("/api/beneficiaries", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiary(beneficiary_data: BeneficiaryCreate, authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    beneficiary_id = str(uuid.uuid4())
    new_beneficiary = Beneficiary(
        beneficiary_id=beneficiary_id,
        user_id=user.user_id,
        name=beneficiary_data.name,
        account_number=beneficiary_data.account_number,
        bank_name=beneficiary_data.bank_name,
        nickname=beneficiary_data.nickname
    )
    
    beneficiaries_db.append(new_beneficiary)
    
    return BeneficiaryResponse(
        beneficiary_id=new_beneficiary.beneficiary_id,
        user_id=new_beneficiary.user_id,
        name=new_beneficiary.name,
        account_number=new_beneficiary.account_number,
        bank_name=new_beneficiary.bank_name,
        nickname=new_beneficiary.nickname,
        created_at=new_beneficiary.created_at
    )


@app.delete("/api/beneficiaries/{beneficiary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_beneficiary(beneficiary_id: str, authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    beneficiary = next((b for b in beneficiaries_db if b.beneficiary_id == beneficiary_id), None)
    
    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found"
        )
    
    if beneficiary.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this beneficiary"
        )
    
    beneficiaries_db.remove(beneficiary)
    return None


@app.get("/api/analytics/account/{account_id}", response_model=AccountAnalytics)
def get_account_analytics(account_id: str, authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    account = next((acc for acc in accounts_db if acc.account_id == account_id), None)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if account.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this account"
        )
    
    account_transactions = [
        t for t in transactions_db
        if (t.from_account_id == account_id or t.to_account_id == account_id) 
        and t.status == TransactionStatus.COMPLETED
    ]
    
    deposits = sum(
        t.amount for t in account_transactions
        if (t.to_account_id == account_id and t.transaction_type in [TransactionType.DEPOSIT, TransactionType.TRANSFER]) 
        or (t.from_account_id == account_id and t.transaction_type == TransactionType.DEPOSIT)
    )
    
    withdrawals = sum(
        t.amount for t in account_transactions
        if t.from_account_id == account_id and t.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER, TransactionType.PAYMENT]
    )
    
    total_transactions = len(account_transactions)
    average_amount = sum(t.amount for t in account_transactions) / total_transactions if total_transactions > 0 else 0
    largest_amount = max((t.amount for t in account_transactions), default=0)
    
    return AccountAnalytics(
        account_id=account_id,
        total_deposits=deposits,
        total_withdrawals=withdrawals,
        total_transactions=total_transactions,
        average_transaction_amount=round(average_amount, 2),
        largest_transaction=largest_amount,
        current_balance=account.balance
    )


@app.get("/api/analytics/user", response_model=UserAnalytics)
def get_user_analytics(authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    user_accounts = [acc for acc in accounts_db if acc.user_id == user.user_id]
    total_balance = sum(acc.balance for acc in user_accounts)
    
    user_account_ids = {acc.account_id for acc in user_accounts}
    
    user_transactions = [
        t for t in transactions_db
        if (t.from_account_id in user_account_ids or t.to_account_id in user_account_ids)
        and t.status == TransactionStatus.COMPLETED
    ]
    
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    
    monthly_transactions = [
        t for t in user_transactions
        if datetime.fromisoformat(t.created_at).month == current_month
        and datetime.fromisoformat(t.created_at).year == current_year
    ]
    
    monthly_spending = sum(
        t.amount for t in monthly_transactions
        if t.from_account_id in user_account_ids
        and t.transaction_type in [TransactionType.WITHDRAWAL, TransactionType.PAYMENT]
    )
    
    monthly_income = sum(
        t.amount for t in monthly_transactions
        if t.transaction_type == TransactionType.DEPOSIT
        or (t.to_account_id in user_account_ids and t.transaction_type == TransactionType.TRANSFER)
    )
    
    return UserAnalytics(
        user_id=user.user_id,
        total_accounts=len(user_accounts),
        total_balance=round(total_balance, 2),
        monthly_spending=round(monthly_spending, 2),
        monthly_income=round(monthly_income, 2),
        transaction_count=len(user_transactions)
    )


@app.put("/api/accounts/{account_id}/status", response_model=AccountResponse)
def update_account_status(account_id: str, is_active: bool, authorization: Optional[str] = None):
    user = get_current_user(authorization)
    
    account = next((acc for acc in accounts_db if acc.account_id == account_id), None)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if account.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this account"
        )
    
    account.is_active = is_active
    
    return AccountResponse(
        account_id=account.account_id,
        user_id=account.user_id,
        account_number=account.account_number,
        account_type=account.account_type,
        account_name=account.account_name,
        balance=account.balance,
        currency=account.currency,
        created_at=account.created_at,
        is_active=account.is_active
    )