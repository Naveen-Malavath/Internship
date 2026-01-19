from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import jwt
import hashlib
import secrets
from collections import defaultdict

app = FastAPI(
    title="E-Commerce Platform",
    description="Modern e-commerce platform with user authentication, product catalog, and order management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    created_at: str


class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: Optional[str] = None
    created_at: str
    rating: float = 0.0
    review_count: int = 0


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0)
    category: str
    stock: int = Field(ge=0)
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = None
    stock: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = None


class Review(BaseModel):
    id: int
    product_id: int
    user_id: int
    username: str
    rating: int = Field(ge=1, le=5)
    comment: str
    created_at: str


class ReviewCreate(BaseModel):
    product_id: int
    rating: int = Field(ge=1, le=5)
    comment: str


class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class Cart(BaseModel):
    user_id: int
    items: List[CartItem]
    updated_at: str


class OrderItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float


class Order(BaseModel):
    id: int
    user_id: int
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus
    shipping_address: str
    payment_method: str
    created_at: str
    updated_at: str


class OrderCreate(BaseModel):
    shipping_address: str
    payment_method: str


class PaymentRequest(BaseModel):
    order_id: int
    payment_method: str
    card_number: Optional[str] = None
    card_holder: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: User


class HealthResponse(BaseModel):
    status: str
    timestamp: str


users_db: List[Dict[str, Any]] = []
products_db: List[Dict[str, Any]] = []
reviews_db: List[Dict[str, Any]] = []
carts_db: Dict[int, Dict[str, Any]] = {}
orders_db: List[Dict[str, Any]] = []
user_behavior_db: Dict[int, List[int]] = defaultdict(list)

next_user_id = 1
next_product_id = 1
next_review_id = 1
next_order_id = 1


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = next((u for u in users_db if u["id"] == user_id), None)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


def verify_admin(current_user: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def initialize_seed_data():
    global next_user_id, next_product_id, next_review_id
    
    admin_user = {
        "id": next_user_id,
        "username": "admin",
        "email": "admin@ecommerce.com",
        "password": hash_password("admin123"),
        "full_name": "Admin User",
        "role": UserRole.ADMIN,
        "created_at": datetime.utcnow().isoformat()
    }
    users_db.append(admin_user)
    next_user_id += 1
    
    customer_user = {
        "id": next_user_id,
        "username": "john_doe",
        "email": "john@example.com",
        "password": hash_password("password123"),
        "full_name": "John Doe",
        "role": UserRole.CUSTOMER,
        "created_at": datetime.utcnow().isoformat()
    }
    users_db.append(customer_user)
    next_user_id += 1
    
    sample_products = [
        {
            "id": next_product_id,
            "name": "Wireless Bluetooth Headphones",
            "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life",
            "price": 89.99,
            "category": "Electronics",
            "stock": 50,
            "image_url": "https://example.com/images/headphones.jpg",
            "created_at": datetime.utcnow().isoformat(),
            "rating": 4.5,
            "review_count": 2
        },
        {
            "id": next_product_id + 1,
            "name": "Smart Fitness Watch",
            "description": "Advanced fitness tracker with heart rate monitor, GPS, and sleep tracking",
            "price": 199.99,
            "category": "Electronics",
            "stock": 30,
            "image_url": "https://example.com/images/watch.jpg",
            "created_at": datetime.utcnow().isoformat(),
            "rating": 4.8,
            "review_count": 1
        },
        {
            "id": next_product_id + 2,
            "name": "Organic Cotton T-Shirt",
            "description": "Comfortable 100% organic cotton t-shirt available in multiple colors",
            "price": 24.99,
            "category": "Clothing",
            "stock": 100,
            "image_url": "https://example.com/images/tshirt.jpg",
            "created_at": datetime.utcnow().isoformat(),
            "rating": 4.2,
            "review_count": 1
        },
        {
            "id": next_product_id + 3,
            "name": "Stainless Steel Water Bottle",
            "description": "Insulated water bottle keeps drinks cold for 24 hours or hot for 12 hours",
            "price": 34.99,
            "category": "Home & Kitchen",
            "stock": 75,
            "image_url": "https://example.com/images/bottle.jpg",
            "created_at": datetime.utcnow().isoformat(),
            "rating": 4.7,
            "review_count": 0
        },
        {
            "id": next_product_id + 4,
            "name": "Yoga Mat with Carrying Strap",
            "description": "Non-slip, eco-friendly yoga mat perfect for home or studio practice",
            "price": 39.99,
            "category": "Sports & Outdoors",
            "stock": 60,
            "image_url": "https://example.com/images/yogamat.jpg",
            "created_at": datetime.utcnow().isoformat(),
            "rating": 0.0,
            "review_count": 0
        }
    ]
    products_db.extend(sample_products)
    next_product_id += 5
    
    sample_reviews = [
        {
            "id": next_review_id,
            "product_id": 1,
            "user_id": 2,
            "username": "john_doe",
            "rating": 5,
            "comment": "Amazing sound quality! Best headphones I've ever owned.",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": next_review_id + 1,
            "product_id": 1,
            "user_id": 2,
            "username": "john_doe",
            "rating": 4,
            "comment": "Great product, but a bit pricey.",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": next_review_id + 2,
            "product_id": 2,
            "user_id": 2,
            "username": "john_doe",
            "rating": 5,
            "comment": "Excellent fitness tracker! Tracks everything I need.",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": next_review_id + 3,
            "product_id": 3,
            "user_id": 2,
            "username": "john_doe",
            "rating": 4,
            "comment": "Very comfortable and soft fabric.",
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    reviews_db.extend(sample_reviews)
    next_review_id += 4


initialize_seed_data()


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister):
    global next_user_id
    
    if any(u["username"] == user_data.username for u in users_db):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if any(u["email"] == user_data.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = {
        "id": next_user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "role": UserRole.CUSTOMER,
        "created_at": datetime.utcnow().isoformat()
    }
    users_db.append(new_user)
    next_user_id += 1
    
    access_token = create_access_token({"user_id": new_user["id"]})
    
    user_response = User(
        id=new_user["id"],
        username=new_user["username"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        role=new_user["role"],
        created_at=new_user["created_at"]
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }


@app.post("/api/auth/login", response_model=TokenResponse)
def login_user(credentials: UserLogin):
    user = next((u for u in users_db if u["username"] == credentials.username), None)
    
    if not user or user["password"] != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token({"user_id": user["id"]})
    
    user_response = User(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        created_at=user["created_at"]
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }


@app.get("/api/auth/me", response_model=User)
def get_current_user(current_user: Dict[str, Any] = Depends(verify_token)):
    return User(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        created_at=current_user["created_at"]
    )


@app.get("/api/products", response_model=List[Product])
def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    filtered_products = products_db
    
    if category:
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]
    
    if search:
        search_lower = search.lower()
        filtered_products = [
            p for p in filtered_products
            if search_lower in p["name"].lower() or search_lower in p["description"].lower()
        ]
    
    return [Product(**p) for p in filtered_products[skip:skip + limit]]


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: int, current_user: Optional[Dict[str, Any]] = Depends(verify_token)):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if current_user:
        user_behavior_db[current_user["id"]].append(product_id)
    
    return Product(**product)


@app.post("/api/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, admin_user: Dict[str, Any] = Depends(verify_admin)):
    global next_product_id
    
    new_product = {
        "id": next_product_id,
        "name": product_data.name,
        "description": product_data.description,
        "price": product_data.price,
        "category": product_data.category,
        "stock": product_data.stock,
        "image_url": product_data.image_url,
        "created_at": datetime.utcnow().isoformat(),
        "rating": 0.0,
        "review_count": 0
    }
    products_db.append(new_product)
    next_product_id += 1
    
    return Product(**new_product)


@app.put("/api/products/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    admin_user: Dict[str, Any] = Depends(verify_admin)
):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        product[key] = value
    
    return Product(**product)


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, admin_user: Dict[str, Any] = Depends(verify_admin)):
    product_index = next((i for i, p in enumerate(products_db) if p["id"] == product_id), None)
    if product_index is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    products_db.pop(product_index)
    return None


@app.get("/api/products/{product_id}/reviews", response_model=List[Review])
def get_product_reviews(product_id: int):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_reviews = [r for r in reviews_db if r["product_id"] == product_id]
    return [Review(**r) for r in product_reviews]


@app.post("/api/reviews", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(review_data: ReviewCreate, current_user: Dict[str, Any] = Depends(verify_token)):
    global next_review_id
    
    product = next((p for p in products_db if p["id"] == review_data.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing_review = next(
        (r for r in reviews_db if r["product_id"] == review_data.product_id and r["user_id"] == current_user["id"]),
        None
    )
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    new_review = {
        "id": next_review_id,
        "product_id": review_data.product_id,
        "user_id": current_user["id"],
        "username": current_user["username"],
        "rating": review_data.rating,
        "comment": review_data.comment,
        "created_at": datetime.utcnow().isoformat()
    }
    reviews_db.append(new_review)
    next_review_id += 1
    
    product_reviews = [r for r in reviews_db if r["product_id"] == review_data.product_id]
    avg_rating = sum(r["rating"] for r in product_reviews) / len(product_reviews)
    product["rating"] = round(avg_rating, 1)
    product["review_count"] = len(product_reviews)
    
    return Review(**new_review)


@app.get("/api/cart", response_model=Cart)
def get_cart(current_user: Dict[str, Any] = Depends(verify_token)):
    user_cart = carts_db.get(current_user["id"])
    if not user_cart:
        user_cart = {
            "user_id": current_user["id"],
            "items": [],
            "updated_at": datetime.utcnow().isoformat()
        }
        carts_db[current_user["id"]] = user_cart
    
    return Cart(**user_cart)


@app.post("/api/cart/items", response_model=Cart)
def add_to_cart(cart_item: CartItem, current_user: Dict[str, Any] = Depends(verify_token)):
    product = next((p for p in products_db if p["id"] == cart_item.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["stock"] < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    user_cart = carts_db.get(current_user["id"])
    if not user_cart:
        user_cart = {
            "user_id": current_user["id"],
            "items": [],
            "updated_at": datetime.utcnow().isoformat()
        }
        carts_db[current_user["id"]] = user_cart
    
    existing_item = next((item for item in user_cart["items"] if item["product_id"] == cart_item.product_id), None)
    if existing_item:
        existing_item["quantity"] += cart_item.quantity
    else:
        user_cart["items"].append(cart_item.dict())
    
    user_cart["updated_at"] = datetime.utcnow().isoformat()
    
    return Cart(**user_cart)


@app.put("/api/cart/items/{product_id}", response_model=Cart)
def update_cart_item(
    product_id: int,
    quantity: int = Query(gt=0),
    current_user: Dict[str, Any] = Depends(verify_token)
):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["stock"] < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    user_cart = carts_db.get(current_user["id"])
    if not user_cart:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    cart_item = next((item for item in user_cart["items"] if item["product_id"] == product_id), None)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    cart_item["quantity"] = quantity
    user_cart["updated_at"] = datetime.utcnow().isoformat()
    
    return Cart(**user_cart)


@app.delete("/api/cart/items/{product_id}", response_model=Cart)
def remove_from_cart(product_id: int, current_user: Dict[str, Any] = Depends(verify_token)):
    user_cart = carts_db.get(current_user["id"])
    if not user_cart:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    user_cart["items"] = [item for item in user_cart["items"] if item["product_id"] != product_id]
    user_cart["updated_at"] = datetime.utcnow().isoformat()
    
    return Cart(**user_cart)


@app.delete("/api/cart", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(current_user: Dict[str, Any] = Depends(verify_token)):
    if current_user["id"] in carts_db:
        carts_db[current_user["id"]]["items"] = []
        carts_db[current_user["id"]]["updated_at"] = datetime.utcnow().isoformat()
    return None


@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, current_user: Dict[str, Any] = Depends(verify_token)):
    global next_order_id
    
    user_cart = carts_db.get(current_user["id"])
    if not user_cart or not user_cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    order_items = []
    total_amount = 0.0
    
    for cart_item in user_cart["items"]:
        product = next((p for p in products_db if p["id"] == cart_item["product_id"]), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {cart_item['product_id']} not found")
        
        if product["stock"] < cart_item["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product['name']}"
            )
        
        order_item = {
            "product_id": product["id"],
            "product_name": product["name"],
            "quantity": cart_item["quantity"],
            "price": product["price"]
        }
        order_items.append(order_item)
        total_amount += product["price"] * cart_item["quantity"]
        
        product["stock"] -= cart_item["quantity"]
    
    new_order = {
        "id": next_order_id,
        "user_id": current_user["id"],
        "items": order_items,
        "total_amount": round(total_amount, 2),
        "status": OrderStatus.PENDING,
        "shipping_address": order_data.shipping_address,
        "payment_method": order_data.payment_method,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    orders_db.append(new_order)
    next_order_id += 1
    
    carts_db[current_user["id"]]["items"] = []
    carts_db[current_user["id"]]["updated_at"] = datetime.utcnow().isoformat()
    
    return Order(**new_order)


@app.get("/api/orders", response_model=List[Order])
def get_orders(current_user: Dict[str, Any] = Depends(verify_token)):
    if current_user["role"] == UserRole.ADMIN:
        user_orders = orders_db
    else:
        user_orders = [o for o in orders_db if o["user_id"] == current_user["id"]]
    
    return [Order(**o) for o in user_orders]


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: int, current_user: Dict[str, Any] = Depends(verify_token)):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if current_user["role"] != UserRole.ADMIN and order["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return Order(**order)


@app.put("/api/orders/{order_id}/status", response_model=Order)
def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    admin_user: Dict[str, Any] = Depends(verify_admin)
):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order["status"] = new_status
    order["updated_at"] = datetime.utcnow().isoformat()
    
    return Order(**order)


@app.post("/api/payments/process", status_code=status.HTTP_200_OK)
def process_payment(payment_data: PaymentRequest, current_user: Dict[str, Any] = Depends(verify_token)):
    order = next((o for o in orders_db if o["id"] == payment_data.order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to pay for this order")
    
    if order["status"] != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Order cannot be paid")
    
    order["status"] = OrderStatus.PROCESSING
    order["updated_at"] = datetime.utcnow().isoformat()
    
    return {
        "success": True,
        "message": "Payment processed successfully",
        "order_id": order["id"],
        "transaction_id": secrets.token_hex(16)
    }


@app.get("/api/recommendations", response_model=List[Product])
def get_recommendations(current_user: Dict[str, Any] = Depends(verify_token)):
    viewed_products = user_behavior_db.get(current_user["id"], [])
    
    if not viewed_products:
        top_rated = sorted(products_db, key=lambda p: p["rating"], reverse=True)[:5]
        return [Product(**p) for p in top_rated]
    
    viewed_categories = [
        p["category"] for p in products_db
        if p["id"] in viewed_products
    ]
    
    if not viewed_categories:
        top_rated = sorted(products_db, key=lambda p: p["rating"], reverse=True)[:5]
        return [Product(**p) for p in top_rated]
    
    most_common_category = max(set(viewed_categories), key=viewed_categories.count)
    
    recommendations = [
        p for p in products_db
        if p["category"] == most_common_category and p["id"] not in viewed_products
    ]
    
    recommendations.sort(key=lambda p: p["rating"], reverse=True)
    
    return [Product(**p) for p in recommendations[:5]]


@app.get("/api/categories", response_model=List[str])
def get_categories():
    categories = list(set(p["category"] for p in products_db))
    return sorted(categories)


@app.get("/api/admin/stats")
def get_admin_stats(admin_user: Dict[str, Any] = Depends(verify_admin)):
    total_products = len(products_db)
    total_orders = len(orders_db)
    total_users = len([u for u in users_db if u["role"] == UserRole.CUSTOMER])
    total_revenue = sum(o["total_amount"] for o in orders_db if o["status"] != OrderStatus.CANCELLED)
    
    pending_orders = len([o for o in orders_db if o["status"] == OrderStatus.PENDING])
    processing_orders = len([o for o in orders_db if o["status"] == OrderStatus.PROCESSING])
    shipped_orders = len([o for o in orders_db if o["status"] == OrderStatus.SHIPPED])
    delivered_orders = len([o for o in orders_db if o["status"] == OrderStatus.DELIVERED])
    
    low_stock_products = [p for p in products_db if p["stock"] < 10]
    
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_revenue": round(total_revenue, 2),
        "order_status_breakdown": {
            "pending": pending_orders,
            "processing": processing_orders,
            "shipped": shipped_orders,
            "delivered": delivered_orders
        },
        "low_stock_products": len(low_stock_products),
        "low_stock_details": [
            {"id": p["id"], "name": p["name"], "stock": p["stock"]}
            for p in low_stock_products
        ]
    }