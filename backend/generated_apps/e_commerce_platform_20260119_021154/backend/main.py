from fastapi import FastAPI, HTTPException, Query, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import hashlib
import secrets
from collections import defaultdict

app = FastAPI(title="E-Commerce Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

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
    role: UserRole = UserRole.CUSTOMER
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
    average_rating: float = 0.0
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
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None

class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class CartItemResponse(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int
    subtotal: float

class Cart(BaseModel):
    user_id: int
    items: List[CartItemResponse]
    total: float

class OrderItem(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int
    subtotal: float

class Order(BaseModel):
    id: int
    user_id: int
    items: List[OrderItem]
    total: float
    status: OrderStatus
    payment_status: PaymentStatus
    shipping_address: str
    created_at: str
    updated_at: str

class OrderCreate(BaseModel):
    shipping_address: str

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

class PaymentRequest(BaseModel):
    order_id: int
    payment_method: str
    card_number: Optional[str] = None

class PaymentResponse(BaseModel):
    payment_id: str
    order_id: int
    amount: float
    status: PaymentStatus
    processed_at: str

users_db: List[Dict] = []
products_db: List[Dict] = []
carts_db: Dict[int, List[Dict]] = defaultdict(list)
orders_db: List[Dict] = []
reviews_db: List[Dict] = []
sessions_db: Dict[str, Dict] = {}

next_user_id = 1
next_product_id = 1
next_order_id = 1
next_review_id = 1

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    sessions_db[token] = {
        "user_id": user_id,
        "created_at": datetime.now().isoformat()
    }
    return token

def get_current_user(authorization: Optional[str] = Header(None)) -> Dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    if token not in sessions_db:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    session = sessions_db[token]
    user = next((u for u in users_db if u["id"] == session["user_id"]), None)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

def get_admin_user(user: Dict = Depends(get_current_user)) -> Dict:
    if user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def calculate_product_rating(product_id: int):
    product_reviews = [r for r in reviews_db if r["product_id"] == product_id]
    if not product_reviews:
        return 0.0, 0
    
    total_rating = sum(r["rating"] for r in product_reviews)
    avg_rating = round(total_rating / len(product_reviews), 2)
    return avg_rating, len(product_reviews)

users_db.extend([
    {
        "id": 1,
        "username": "admin",
        "email": "admin@ecommerce.com",
        "password": hash_password("admin123"),
        "full_name": "Admin User",
        "role": UserRole.ADMIN,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": 2,
        "username": "john_doe",
        "email": "john@example.com",
        "password": hash_password("password123"),
        "full_name": "John Doe",
        "role": UserRole.CUSTOMER,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": 3,
        "username": "jane_smith",
        "email": "jane@example.com",
        "password": hash_password("password123"),
        "full_name": "Jane Smith",
        "role": UserRole.CUSTOMER,
        "created_at": datetime.now().isoformat()
    }
])
next_user_id = 4

products_db.extend([
    {
        "id": 1,
        "name": "Wireless Headphones",
        "description": "High-quality Bluetooth headphones with noise cancellation",
        "price": 99.99,
        "category": "Electronics",
        "stock": 50,
        "image_url": "https://example.com/headphones.jpg",
        "created_at": datetime.now().isoformat(),
        "average_rating": 4.5,
        "review_count": 12
    },
    {
        "id": 2,
        "name": "Smart Watch",
        "description": "Fitness tracker with heart rate monitor and GPS",
        "price": 199.99,
        "category": "Electronics",
        "stock": 30,
        "image_url": "https://example.com/smartwatch.jpg",
        "created_at": datetime.now().isoformat(),
        "average_rating": 4.2,
        "review_count": 8
    },
    {
        "id": 3,
        "name": "Running Shoes",
        "description": "Comfortable running shoes with excellent cushioning",
        "price": 79.99,
        "category": "Footwear",
        "stock": 100,
        "image_url": "https://example.com/shoes.jpg",
        "created_at": datetime.now().isoformat(),
        "average_rating": 4.8,
        "review_count": 25
    },
    {
        "id": 4,
        "name": "Laptop Backpack",
        "description": "Durable backpack with laptop compartment",
        "price": 49.99,
        "category": "Accessories",
        "stock": 75,
        "image_url": "https://example.com/backpack.jpg",
        "created_at": datetime.now().isoformat(),
        "average_rating": 4.3,
        "review_count": 15
    },
    {
        "id": 5,
        "name": "Coffee Maker",
        "description": "Programmable coffee maker with thermal carafe",
        "price": 89.99,
        "category": "Home & Kitchen",
        "stock": 40,
        "image_url": "https://example.com/coffeemaker.jpg",
        "created_at": datetime.now().isoformat(),
        "average_rating": 4.6,
        "review_count": 20
    }
])
next_product_id = 6

reviews_db.extend([
    {
        "id": 1,
        "product_id": 1,
        "user_id": 2,
        "username": "john_doe",
        "rating": 5,
        "comment": "Excellent sound quality and comfort!",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": 2,
        "product_id": 3,
        "user_id": 3,
        "username": "jane_smith",
        "rating": 5,
        "comment": "Best running shoes I've ever owned!",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": 3,
        "product_id": 2,
        "user_id": 2,
        "username": "john_doe",
        "rating": 4,
        "comment": "Good watch, battery could be better",
        "created_at": datetime.now().isoformat()
    }
])
next_review_id = 4

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "E-Commerce Platform API"
    }

@app.post("/api/auth/register", response_model=User, status_code=201)
def register_user(user_data: UserRegister):
    global next_user_id
    
    if any(u["username"] == user_data.username for u in users_db):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if any(u["email"] == user_data.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = {
        "id": next_user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "role": UserRole.CUSTOMER,
        "created_at": datetime.now().isoformat()
    }
    users_db.append(new_user)
    next_user_id += 1
    
    return User(**{k: v for k, v in new_user.items() if k != "password"})

@app.post("/api/auth/login")
def login_user(credentials: UserLogin):
    user = next((u for u in users_db if u["username"] == credentials.username), None)
    
    if not user or user["password"] != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_session(user["id"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": User(**{k: v for k, v in user.items() if k != "password"})
    }

@app.get("/api/auth/me", response_model=User)
def get_current_user_info(user: Dict = Depends(get_current_user)):
    return User(**{k: v for k, v in user.items() if k != "password"})

@app.post("/api/auth/logout")
def logout_user(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        if token in sessions_db:
            del sessions_db[token]
    
    return {"message": "Logged out successfully"}

@app.get("/api/products", response_model=List[Product])
def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query(None, regex="^(price_asc|price_desc|rating|newest)$")
):
    filtered_products = products_db.copy()
    
    if category:
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]
    
    if search:
        search_lower = search.lower()
        filtered_products = [
            p for p in filtered_products
            if search_lower in p["name"].lower() or search_lower in p["description"].lower()
        ]
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]
    
    if sort_by == "price_asc":
        filtered_products.sort(key=lambda x: x["price"])
    elif sort_by == "price_desc":
        filtered_products.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "rating":
        filtered_products.sort(key=lambda x: x["average_rating"], reverse=True)
    elif sort_by == "newest":
        filtered_products.sort(key=lambda x: x["created_at"], reverse=True)
    
    return [Product(**p) for p in filtered_products]

@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@app.post("/api/products", response_model=Product, status_code=201)
def create_product(product_data: ProductCreate, admin: Dict = Depends(get_admin_user)):
    global next_product_id
    
    new_product = {
        "id": next_product_id,
        "name": product_data.name,
        "description": product_data.description,
        "price": product_data.price,
        "category": product_data.category,
        "stock": product_data.stock,
        "image_url": product_data.image_url,
        "created_at": datetime.now().isoformat(),
        "average_rating": 0.0,
        "review_count": 0
    }
    products_db.append(new_product)
    next_product_id += 1
    
    return Product(**new_product)

@app.put("/api/products/{product_id}", response_model=Product)
def update_product(product_id: int, product_data: ProductUpdate, admin: Dict = Depends(get_admin_user)):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        product[key] = value
    
    return Product(**product)

@app.delete("/api/products/{product_id}", status_code=204)
def delete_product(product_id: int, admin: Dict = Depends(get_admin_user)):
    global products_db
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    products_db = [p for p in products_db if p["id"] != product_id]
    return None

@app.get("/api/categories")
def get_categories():
    categories = list(set(p["category"] for p in products_db))
    return {"categories": categories}

@app.get("/api/cart", response_model=Cart)
def get_cart(user: Dict = Depends(get_current_user)):
    user_cart = carts_db.get(user["id"], [])
    cart_items = []
    total = 0.0
    
    for cart_item in user_cart:
        product = next((p for p in products_db if p["id"] == cart_item["product_id"]), None)
        if product:
            subtotal = product["price"] * cart_item["quantity"]
            cart_items.append(CartItemResponse(
                product_id=product["id"],
                product_name=product["name"],
                price=product["price"],
                quantity=cart_item["quantity"],
                subtotal=subtotal
            ))
            total += subtotal
    
    return Cart(user_id=user["id"], items=cart_items, total=round(total, 2))

@app.post("/api/cart", response_model=Cart)
def add_to_cart(cart_item: CartItem, user: Dict = Depends(get_current_user)):
    product = next((p for p in products_db if p["id"] == cart_item.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["stock"] < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    user_cart = carts_db[user["id"]]
    existing_item = next((item for item in user_cart if item["product_id"] == cart_item.product_id), None)
    
    if existing_item:
        new_quantity = existing_item["quantity"] + cart_item.quantity
        if product["stock"] < new_quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        existing_item["quantity"] = new_quantity
    else:
        user_cart.append({
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity
        })
    
    return get_cart(user)

@app.put("/api/cart/{product_id}", response_model=Cart)
def update_cart_item(product_id: int, cart_item: CartItem, user: Dict = Depends(get_current_user)):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["stock"] < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    user_cart = carts_db[user["id"]]
    existing_item = next((item for item in user_cart if item["product_id"] == product_id), None)
    
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    existing_item["quantity"] = cart_item.quantity
    
    return get_cart(user)

@app.delete("/api/cart/{product_id}", response_model=Cart)
def remove_from_cart(product_id: int, user: Dict = Depends(get_current_user)):
    user_cart = carts_db[user["id"]]
    carts_db[user["id"]] = [item for item in user_cart if item["product_id"] != product_id]
    return get_cart(user)

@app.delete("/api/cart", response_model=Cart)
def clear_cart(user: Dict = Depends(get_current_user)):
    carts_db[user["id"]] = []
    return get_cart(user)

@app.post("/api/orders", response_model=Order, status_code=201)
def create_order(order_data: OrderCreate, user: Dict = Depends(get_current_user)):
    global next_order_id
    
    user_cart = carts_db.get(user["id"], [])
    if not user_cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    order_items = []
    total = 0.0
    
    for cart_item in user_cart:
        product = next((p for p in products_db if p["id"] == cart_item["product_id"]), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {cart_item['product_id']} not found")
        
        if product["stock"] < cart_item["quantity"]:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product['name']}")
        
        subtotal = product["price"] * cart_item["quantity"]
        order_items.append({
            "product_id": product["id"],
            "product_name": product["name"],
            "price": product["price"],
            "quantity": cart_item["quantity"],
            "subtotal": subtotal
        })
        total += subtotal
        
        product["stock"] -= cart_item["quantity"]
    
    new_order = {
        "id": next_order_id,
        "user_id": user["id"],
        "items": order_items,
        "total": round(total, 2),
        "status": OrderStatus.PENDING,
        "payment_status": PaymentStatus.PENDING,
        "shipping_address": order_data.shipping_address,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    orders_db.append(new_order)
    next_order_id += 1
    
    carts_db[user["id"]] = []
    
    return Order(**new_order)

@app.get("/api/orders", response_model=List[Order])
def get_orders(user: Dict = Depends(get_current_user)):
    user_orders = [o for o in orders_db if o["user_id"] == user["id"]]
    user_orders.sort(key=lambda x: x["created_at"], reverse=True)
    return [Order(**o) for o in user_orders]

@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: int, user: Dict = Depends(get_current_user)):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["user_id"] != user["id"] and user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return Order(**order)

@app.put("/api/orders/{order_id}/status", response_model=Order)
def update_order_status(order_id: int, status: OrderStatus, admin: Dict = Depends(get_admin_user)):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order["status"] = status
    order["updated_at"] = datetime.now().isoformat()
    
    return Order(**order)

@app.post("/api/orders/{order_id}/cancel", response_model=Order)
def cancel_order(order_id: int, user: Dict = Depends(get_current_user)):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this order")
    
    if order["status"] not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
        raise HTTPException(status_code=400, detail="Cannot cancel order in current status")
    
    order["status"] = OrderStatus.CANCELLED
    order["updated_at"] = datetime.now().isoformat()
    
    for item in order["items"]:
        product = next((p for p in products_db if p["id"] == item["product_id"]), None)
        if product:
            product["stock"] += item["quantity"]
    
    return Order(**order)

@app.post("/api/payments", response_model=PaymentResponse)
def process_payment(payment_request: PaymentRequest, user: Dict = Depends(get_current_user)):
    order = next((o for o in orders_db if o["id"] == payment_request.order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to pay for this order")
    
    if order["payment_status"] == PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Order already paid")
    
    payment_id = secrets.token_urlsafe(16)
    order["payment_status"] = PaymentStatus.COMPLETED
    order["status"] = OrderStatus.PROCESSING
    order["updated_at"] = datetime.now().isoformat()
    
    return PaymentResponse(
        payment_id=payment_id,
        order_id=order["id"],
        amount=order["total"],
        status=PaymentStatus.COMPLETED,
        processed_at=datetime.now().isoformat()
    )

@app.get("/api/products/{product_id}/reviews", response_model=List[Review])
def get_product_reviews(product_id: int):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_reviews = [r for r in reviews_db if r["product_id"] == product_id]
    product_reviews.sort(key=lambda x: x["created_at"], reverse=True)
    return [Review(**r) for r in product_reviews]

@app.post("/api/reviews", response_model=Review, status_code=201)
def create_review(review_data: ReviewCreate, user: Dict = Depends(get_current_user)):
    global next_review_id
    
    product = next((p for p in products_db if p["id"] == review_data.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    user_orders = [o for o in orders_db if o["user_id"] == user["id"] and o["payment_status"] == PaymentStatus.COMPLETED]
    has_purchased = any(
        any(item["product_id"] == review_data.product_id for item in order["items"])
        for order in user_orders
    )
    
    if not has_purchased:
        raise HTTPException(status_code=400, detail="You must purchase this product before reviewing")
    
    existing_review = next((r for r in reviews_db if r["product_id"] == review_data.product_id and r["user_id"] == user["id"]), None)
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    new_review = {
        "id": next_review_id,
        "product_id": review_data.product_id,
        "user_id": user["id"],
        "username": user["username"],
        "rating": review_data.rating,
        "comment": review_data.comment,
        "created_at": datetime.now().isoformat()
    }
    reviews_db.append(new_review)
    next_review_id += 1
    
    avg_rating, review_count = calculate_product_rating(review_data.product_id)
    product["average_rating"] = avg_rating
    product["review_count"] = review_count
    
    return Review(**new_review)

@app.delete("/api/reviews/{review_id}", status_code=204)
def delete_review(review_id: int, user: Dict = Depends(get_current_user)):
    global reviews_db
    review = next((r for r in reviews_db if r["id"] == review_id), None)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review["user_id"] != user["id"] and user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")
    
    product_id = review["product_id"]
    reviews_db = [r for r in reviews_db if r["id"] != review_id]
    
    product = next((p for p in products_db if p["id"] == product_id), None)
    if product:
        avg_rating, review_count = calculate_product_rating(product_id)
        product["average_rating"] = avg_rating
        product["review_count"] = review_count
    
    return None

@app.get("/api/recommendations", response_model=List[Product])
def get_recommendations(user: Dict = Depends(get_current_user)):
    user_orders = [o for o in orders_db if o["user_id"] == user["id"]]
    
    if not user_orders:
        top_rated = sorted(products_db, key=lambda x: (x["average_rating"], x["review_count"]), reverse=True)[:5]
        return [Product(**p) for p in top_rated]
    
    purchased_categories = set()
    for order in user_orders:
        for item in order["items"]:
            product = next((p for p in products_db if p["id"] == item["product_id"]), None)
            if product:
                purchased_categories.add(product["category"])
    
    purchased_product_ids = set()
    for order in user_orders:
        for item in order["items"]:
            purchased_product_ids.add(item["product_id"])
    
    recommendations = []
    for product in products_db:
        if product["id"] not in purchased_product_ids and product["category"] in purchased_categories:
            recommendations.append(product)
    
    recommendations.sort(key=lambda x: (x["average_rating"], x["review_count"]), reverse=True)
    
    if len(recommendations) < 5:
        other_products = [p for p in products_db if p["id"] not in purchased_product_ids and p not in recommendations]
        other_products.sort(key=lambda x: (x["average_rating"], x["review_count"]), reverse=True)
        recommendations.extend(other_products[:5 - len(recommendations)])
    
    return [Product(**p) for p in recommendations[:5]]

@app.get("/api/admin/dashboard")
def get_admin_dashboard(admin: Dict = Depends(get_admin_user)):
    total_users = len([u for u in users_db if u["role"] == UserRole.CUSTOMER])
    total_products = len(products_db)
    total_orders = len(orders_db)
    
    total_revenue = sum(o["total"] for o in orders_db if o["payment_status"] == PaymentStatus.COMPLETED)
    
    pending_orders = len([o for o in orders_db if o["status"] == OrderStatus.PENDING])
    
    low_stock_products = [p for p in products_db if p["stock"] < 10]
    
    recent_orders = sorted(orders_db, key=lambda x: x["created_at"], reverse=True)[:10]
    
    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "pending_orders": pending_orders,
        "low_stock_products": [Product(**p) for p in low_stock_products],
        "recent_orders": [Order(**o) for o in recent_orders]
    }

@app.get("/api/admin/orders", response_model=List[Order])
def get_all_orders(admin: Dict = Depends(get_admin_user)):
    all_orders = sorted(orders_db, key=lambda x: x["created_at"], reverse=True)
    return [Order(**o) for o in all_orders]

@app.get("/api/admin/users", response_model=List[User])
def get_all_users(admin: Dict = Depends(get_admin_user)):
    all_users = [User(**{k: v for k, v in u.items() if k != "password"}) for u in users_db]
    return all_users