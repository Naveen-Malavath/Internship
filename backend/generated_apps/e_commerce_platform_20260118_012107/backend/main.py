from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets
from enum import Enum

app = FastAPI(
    title="E-Commerce Platform",
    description="Complete e-commerce platform with user management, products, cart, orders, and reviews",
    version="1.0.0"
)

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

class UserRegistration(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    created_at: str

class AuthResponse(BaseModel):
    token: str
    user: UserResponse

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock_quantity: int
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: str
    updated_at: str

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock_quantity: int
    image_url: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class CartItem(BaseModel):
    product_id: str
    quantity: int

class CartItemResponse(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float
    subtotal: float

class CartResponse(BaseModel):
    user_id: str
    items: List[CartItemResponse]
    total: float

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float
    subtotal: float

class Order(BaseModel):
    id: str
    user_id: str
    items: List[OrderItem]
    total_amount: float
    status: str
    payment_status: str
    shipping_address: str
    created_at: str
    updated_at: str

class OrderCreate(BaseModel):
    shipping_address: str
    payment_method: str

class Review(BaseModel):
    id: str
    product_id: str
    user_id: str
    user_name: str
    rating: int
    comment: str
    created_at: str

class ReviewCreate(BaseModel):
    product_id: str
    rating: int
    comment: str

class ProductStats(BaseModel):
    total_products: int
    total_value: float
    low_stock_count: int
    out_of_stock_count: int

class OrderStats(BaseModel):
    total_orders: int
    pending_orders: int
    total_revenue: float

class UserStats(BaseModel):
    total_users: int
    total_customers: int
    total_admins: int

class DashboardStats(BaseModel):
    product_stats: ProductStats
    order_stats: OrderStats
    user_stats: UserStats

users_db = []
products_db = []
carts_db = {}
orders_db = []
reviews_db = []
sessions_db = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_urlsafe(32)

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

def get_admin_user(authorization: Optional[str] = Header(None)) -> dict:
    user = get_current_user(authorization)
    if user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

admin_user = {
    "id": str(uuid.uuid4()),
    "email": "admin@ecommerce.com",
    "password": hash_password("admin123"),
    "full_name": "Admin User",
    "phone": "+1234567890",
    "role": UserRole.ADMIN,
    "created_at": datetime.utcnow().isoformat()
}
users_db.append(admin_user)

sample_products = [
    {
        "id": str(uuid.uuid4()),
        "name": "Wireless Headphones",
        "description": "Premium noise-cancelling wireless headphones with 30-hour battery life",
        "price": 199.99,
        "category": "Electronics",
        "stock_quantity": 50,
        "image_url": "https://example.com/headphones.jpg",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Smart Watch",
        "description": "Fitness tracking smartwatch with heart rate monitor and GPS",
        "price": 299.99,
        "category": "Electronics",
        "stock_quantity": 30,
        "image_url": "https://example.com/smartwatch.jpg",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Laptop Backpack",
        "description": "Durable waterproof backpack with padded laptop compartment",
        "price": 49.99,
        "category": "Accessories",
        "stock_quantity": 100,
        "image_url": "https://example.com/backpack.jpg",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Mechanical Keyboard",
        "description": "RGB mechanical gaming keyboard with blue switches",
        "price": 129.99,
        "category": "Electronics",
        "stock_quantity": 25,
        "image_url": "https://example.com/keyboard.jpg",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Water Bottle",
        "description": "Insulated stainless steel water bottle, 32oz capacity",
        "price": 24.99,
        "category": "Accessories",
        "stock_quantity": 5,
        "image_url": "https://example.com/bottle.jpg",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
]
products_db.extend(sample_products)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "E-Commerce Platform"
    }

@app.post("/api/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegistration):
    if any(u["email"] == user_data.email for u in users_db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "role": UserRole.CUSTOMER,
        "created_at": datetime.utcnow().isoformat()
    }
    users_db.append(user)
    
    token = generate_token()
    sessions_db[token] = user_id
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        phone=user["phone"],
        role=user["role"],
        created_at=user["created_at"]
    )
    
    return AuthResponse(token=token, user=user_response)

@app.post("/api/auth/login", response_model=AuthResponse)
def login_user(credentials: UserLogin):
    user = next((u for u in users_db if u["email"] == credentials.email), None)
    
    if not user or user["password"] != hash_password(credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    token = generate_token()
    sessions_db[token] = user["id"]
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        phone=user["phone"],
        role=user["role"],
        created_at=user["created_at"]
    )
    
    return AuthResponse(token=token, user=user_response)

@app.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "")
        if token in sessions_db:
            del sessions_db[token]
    return None

@app.get("/api/users/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        phone=current_user["phone"],
        role=current_user["role"],
        created_at=current_user["created_at"]
    )

@app.get("/api/products", response_model=List[Product])
def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None
):
    filtered_products = [p for p in products_db if p["is_active"]]
    
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
    
    if in_stock is not None and in_stock:
        filtered_products = [p for p in filtered_products if p["stock_quantity"] > 0]
    
    return [Product(**p) for p in filtered_products]

@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    product = next((p for p in products_db if p["id"] == product_id and p["is_active"]), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return Product(**product)

@app.post("/api/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, admin_user: dict = Depends(get_admin_user)):
    product_id = str(uuid.uuid4())
    product = {
        "id": product_id,
        "name": product_data.name,
        "description": product_data.description,
        "price": product_data.price,
        "category": product_data.category,
        "stock_quantity": product_data.stock_quantity,
        "image_url": product_data.image_url,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    products_db.append(product)
    return Product(**product)

@app.put("/api/products/{product_id}", response_model=Product)
def update_product(product_id: str, product_data: ProductUpdate, admin_user: dict = Depends(get_admin_user)):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if product_data.name is not None:
        product["name"] = product_data.name
    if product_data.description is not None:
        product["description"] = product_data.description
    if product_data.price is not None:
        product["price"] = product_data.price
    if product_data.category is not None:
        product["category"] = product_data.category
    if product_data.stock_quantity is not None:
        product["stock_quantity"] = product_data.stock_quantity
    if product_data.image_url is not None:
        product["image_url"] = product_data.image_url
    if product_data.is_active is not None:
        product["is_active"] = product_data.is_active
    
    product["updated_at"] = datetime.utcnow().isoformat()
    return Product(**product)

@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, admin_user: dict = Depends(get_admin_user)):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    product["is_active"] = False
    product["updated_at"] = datetime.utcnow().isoformat()
    return None

@app.get("/api/cart", response_model=CartResponse)
def get_cart(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    cart_items = carts_db.get(user_id, [])
    
    response_items = []
    total = 0.0
    
    for cart_item in cart_items:
        product = next((p for p in products_db if p["id"] == cart_item["product_id"]), None)
        if product:
            subtotal = product["price"] * cart_item["quantity"]
            response_items.append(CartItemResponse(
                product_id=product["id"],
                product_name=product["name"],
                quantity=cart_item["quantity"],
                price=product["price"],
                subtotal=subtotal
            ))
            total += subtotal
    
    return CartResponse(user_id=user_id, items=response_items, total=total)

@app.post("/api/cart/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(cart_item: CartItem, current_user: dict = Depends(get_current_user)):
    product = next((p for p in products_db if p["id"] == cart_item.product_id and p["is_active"]), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if product["stock_quantity"] < cart_item.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock")
    
    user_id = current_user["id"]
    if user_id not in carts_db:
        carts_db[user_id] = []
    
    existing_item = next((item for item in carts_db[user_id] if item["product_id"] == cart_item.product_id), None)
    
    if existing_item:
        new_quantity = existing_item["quantity"] + cart_item.quantity
        if product["stock_quantity"] < new_quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock")
        existing_item["quantity"] = new_quantity
    else:
        carts_db[user_id].append({"product_id": cart_item.product_id, "quantity": cart_item.quantity})
    
    return get_cart(current_user)

@app.put("/api/cart/items/{product_id}", response_model=CartResponse)
def update_cart_item(product_id: str, cart_item: CartItem, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    if user_id not in carts_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart is empty")
    
    product = next((p for p in products_db if p["id"] == product_id and p["is_active"]), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if product["stock_quantity"] < cart_item.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock")
    
    existing_item = next((item for item in carts_db[user_id] if item["product_id"] == product_id), None)
    if not existing_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not in cart")
    
    existing_item["quantity"] = cart_item.quantity
    
    return get_cart(current_user)

@app.delete("/api/cart/items/{product_id}", response_model=CartResponse)
def remove_from_cart(product_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    if user_id not in carts_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart is empty")
    
    carts_db[user_id] = [item for item in carts_db[user_id] if item["product_id"] != product_id]
    
    return get_cart(current_user)

@app.delete("/api/cart", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    if user_id in carts_db:
        carts_db[user_id] = []
    return None

@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    cart_items = carts_db.get(user_id, [])
    
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")
    
    order_items = []
    total_amount = 0.0
    
    for cart_item in cart_items:
        product = next((p for p in products_db if p["id"] == cart_item["product_id"]), None)
        if not product or not product["is_active"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product {cart_item['product_id']} not available")
        
        if product["stock_quantity"] < cart_item["quantity"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for {product['name']}")
        
        subtotal = product["price"] * cart_item["quantity"]
        order_items.append(OrderItem(
            product_id=product["id"],
            product_name=product["name"],
            quantity=cart_item["quantity"],
            price=product["price"],
            subtotal=subtotal
        ))
        total_amount += subtotal
        
        product["stock_quantity"] -= cart_item["quantity"]
    
    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "user_id": user_id,
        "items": [item.dict() for item in order_items],
        "total_amount": total_amount,
        "status": OrderStatus.PENDING,
        "payment_status": PaymentStatus.PENDING,
        "shipping_address": order_data.shipping_address,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    orders_db.append(order)
    
    carts_db[user_id] = []
    
    return Order(**order)

@app.get("/api/orders", response_model=List[Order])
def get_orders(current_user: dict = Depends(get_current_user)):
    user_orders = [order for order in orders_db if order["user_id"] == current_user["id"]]
    return [Order(**order) for order in user_orders]

@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if order["user_id"] != current_user["id"] and current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return Order(**order)

@app.put("/api/orders/{order_id}/status", response_model=Order)
def update_order_status(order_id: str, status_update: dict, admin_user: dict = Depends(get_admin_user)):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    new_status = status_update.get("status")
    if new_status and new_status in [s.value for s in OrderStatus]:
        order["status"] = new_status
        order["updated_at"] = datetime.utcnow().isoformat()
    
    return Order(**order)

@app.get("/api/products/{product_id}/reviews", response_model=List[Review])
def get_product_reviews(product_id: str):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    product_reviews = [r for r in reviews_db if r["product_id"] == product_id]
    return [Review(**review) for review in product_reviews]

@app.post("/api/reviews", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(review_data: ReviewCreate, current_user: dict = Depends(get_current_user)):
    product = next((p for p in products_db if p["id"] == review_data.product_id), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be between 1 and 5")
    
    user_has_ordered = any(
        order["user_id"] == current_user["id"] and 
        any(item["product_id"] == review_data.product_id for item in order["items"])
        for order in orders_db
    )
    
    if not user_has_ordered:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can only review products you have purchased")
    
    review_id = str(uuid.uuid4())
    review = {
        "id": review_id,
        "product_id": review_data.product_id,
        "user_id": current_user["id"],
        "user_name": current_user["full_name"],
        "rating": review_data.rating,
        "comment": review_data.comment,
        "created_at": datetime.utcnow().isoformat()
    }
    reviews_db.append(review)
    
    return Review(**review)

@app.get("/api/recommendations", response_model=List[Product])
def get_recommendations(current_user: dict = Depends(get_current_user)):
    user_orders = [order for order in orders_db if order["user_id"] == current_user["id"]]
    
    purchased_categories = set()
    for order in user_orders:
        for item in order["items"]:
            product = next((p for p in products_db if p["id"] == item["product_id"]), None)
            if product:
                purchased_categories.add(product["category"])
    
    if not purchased_categories:
        recommended = [p for p in products_db if p["is_active"]][:5]
        return [Product(**p) for p in recommended]
    
    recommended_products = [
        p for p in products_db 
        if p["is_active"] and p["category"] in purchased_categories
    ]
    
    purchased_product_ids = set()
    for order in user_orders:
        for item in order["items"]:
            purchased_product_ids.add(item["product_id"])
    
    recommended_products = [p for p in recommended_products if p["id"] not in purchased_product_ids]
    
    recommended_products.sort(key=lambda x: x["price"], reverse=True)
    
    return [Product(**p) for p in recommended_products[:5]]

@app.get("/api/admin/dashboard", response_model=DashboardStats)
def get_dashboard_stats(admin_user: dict = Depends(get_admin_user)):
    active_products = [p for p in products_db if p["is_active"]]
    
    total_value = sum(p["price"] * p["stock_quantity"] for p in active_products)
    low_stock = sum(1 for p in active_products if 0 < p["stock_quantity"] <= 10)
    out_of_stock = sum(1 for p in active_products if p["stock_quantity"] == 0)
    
    product_stats = ProductStats(
        total_products=len(active_products),
        total_value=total_value,
        low_stock_count=low_stock,
        out_of_stock_count=out_of_stock
    )
    
    total_orders = len(orders_db)
    pending_orders = sum(1 for o in orders_db if o["status"] == OrderStatus.PENDING)
    total_revenue = sum(o["total_amount"] for o in orders_db if o["payment_status"] == PaymentStatus.COMPLETED)
    
    order_stats = OrderStats(
        total_orders=total_orders,
        pending_orders=pending_orders,
        total_revenue=total_revenue
    )
    
    total_users = len(users_db)
    total_customers = sum(1 for u in users_db if u["role"] == UserRole.CUSTOMER)
    total_admins = sum(1 for u in users_db if u["role"] == UserRole.ADMIN)
    
    user_stats = UserStats(
        total_users=total_users,
        total_customers=total_customers,
        total_admins=total_admins
    )
    
    return DashboardStats(
        product_stats=product_stats,
        order_stats=order_stats,
        user_stats=user_stats
    )

@app.get("/api/admin/orders", response_model=List[Order])
def get_all_orders(admin_user: dict = Depends(get_admin_user)):
    return [Order(**order) for order in orders_db]

@app.get("/api/categories", response_model=List[str])
def get_categories():
    categories = set(p["category"] for p in products_db if p["is_active"])
    return sorted(list(categories))

@app.get("/api/products/{product_id}/rating")
def get_product_rating(product_id: str):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    product_reviews = [r for r in reviews_db if r["product_id"] == product_id]
    
    if not product_reviews:
        return {
            "product_id": product_id,
            "average_rating": 0.0,
            "total_reviews": 0
        }
    
    total_rating = sum(r["rating"] for r in product_reviews)
    average_rating = total_rating / len(product_reviews)
    
    return {
        "product_id": product_id,
        "average_rating": round(average_rating, 2),
        "total_reviews": len(product_reviews)
    }