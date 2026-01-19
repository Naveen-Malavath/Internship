from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets

app = FastAPI(title="E-Commerce Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


class User(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    is_admin: bool = False
    created_at: str


class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: str
    password: str


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: str
    rating: float = 0.0
    review_count: int = 0
    created_at: str


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None


class CartItem(BaseModel):
    product_id: str
    quantity: int


class Cart(BaseModel):
    user_id: str
    items: List[CartItem]
    updated_at: str


class Review(BaseModel):
    id: str
    product_id: str
    user_id: str
    username: str
    rating: int
    comment: str
    created_at: str


class ReviewCreate(BaseModel):
    product_id: str
    rating: int
    comment: str


class Order(BaseModel):
    id: str
    user_id: str
    items: List[Dict]
    total_amount: float
    status: str
    payment_method: str
    shipping_address: str
    created_at: str
    updated_at: str


class OrderCreate(BaseModel):
    payment_method: str
    shipping_address: str


class OrderStatus(BaseModel):
    status: str


users_db = []
products_db = []
carts_db = {}
reviews_db = []
orders_db = []
tokens_db = {}
passwords_db = {}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    user_id = tokens_db.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


seed_products = [
    {
        "id": str(uuid.uuid4()),
        "name": "Wireless Bluetooth Headphones",
        "description": "Premium noise-cancelling wireless headphones with 30-hour battery life",
        "price": 149.99,
        "category": "Electronics",
        "stock": 50,
        "image_url": "https://example.com/headphones.jpg",
        "rating": 4.5,
        "review_count": 127,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Smart Fitness Watch",
        "description": "Track your health and fitness with GPS, heart rate monitor, and sleep tracking",
        "price": 199.99,
        "category": "Electronics",
        "stock": 35,
        "image_url": "https://example.com/watch.jpg",
        "rating": 4.3,
        "review_count": 89,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Organic Cotton T-Shirt",
        "description": "Comfortable, sustainable, and stylish everyday t-shirt",
        "price": 29.99,
        "category": "Clothing",
        "stock": 100,
        "image_url": "https://example.com/tshirt.jpg",
        "rating": 4.7,
        "review_count": 234,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Stainless Steel Water Bottle",
        "description": "Insulated water bottle keeps drinks cold for 24 hours or hot for 12 hours",
        "price": 34.99,
        "category": "Home & Kitchen",
        "stock": 75,
        "image_url": "https://example.com/bottle.jpg",
        "rating": 4.8,
        "review_count": 312,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Yoga Mat Pro",
        "description": "Non-slip, eco-friendly yoga mat with extra cushioning",
        "price": 49.99,
        "category": "Sports",
        "stock": 60,
        "image_url": "https://example.com/yogamat.jpg",
        "rating": 4.6,
        "review_count": 178,
        "created_at": datetime.now().isoformat()
    }
]

products_db.extend(seed_products)

admin_id = str(uuid.uuid4())
admin_user = {
    "id": admin_id,
    "email": "admin@example.com",
    "username": "admin",
    "full_name": "Admin User",
    "is_admin": True,
    "created_at": datetime.now().isoformat()
}
users_db.append(admin_user)
passwords_db[admin_id] = hash_password("admin123")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "E-Commerce Platform API"
    }


@app.post("/api/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister):
    if any(u["email"] == user_data.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    if any(u["username"] == user_data.username for u in users_db):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "is_admin": False,
        "created_at": datetime.now().isoformat()
    }
    users_db.append(user)
    passwords_db[user_id] = hash_password(user_data.password)
    carts_db[user_id] = {"user_id": user_id, "items": [], "updated_at": datetime.now().isoformat()}
    
    return User(**user)


@app.post("/api/auth/login")
def login_user(credentials: UserLogin):
    user = next((u for u in users_db if u["email"] == credentials.email), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if passwords_db.get(user["id"]) != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = generate_token()
    tokens_db[token] = user["id"]
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": User(**user)
    }


@app.get("/api/auth/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/api/auth/logout")
def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token in tokens_db:
        del tokens_db[token]
    return {"message": "Successfully logged out"}


@app.get("/api/products", response_model=List[Product])
def get_products(category: Optional[str] = None, search: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None):
    filtered_products = products_db.copy()
    
    if category:
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]
    
    if search:
        search_lower = search.lower()
        filtered_products = [p for p in filtered_products if search_lower in p["name"].lower() or search_lower in p["description"].lower()]
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]
    
    return [Product(**p) for p in filtered_products]


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)


@app.post("/api/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, admin_user: User = Depends(get_admin_user)):
    product = {
        "id": str(uuid.uuid4()),
        "name": product_data.name,
        "description": product_data.description,
        "price": product_data.price,
        "category": product_data.category,
        "stock": product_data.stock,
        "image_url": product_data.image_url,
        "rating": 0.0,
        "review_count": 0,
        "created_at": datetime.now().isoformat()
    }
    products_db.append(product)
    return Product(**product)


@app.put("/api/products/{product_id}", response_model=Product)
def update_product(product_id: str, product_data: ProductUpdate, admin_user: User = Depends(get_admin_user)):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product_data.name is not None:
        product["name"] = product_data.name
    if product_data.description is not None:
        product["description"] = product_data.description
    if product_data.price is not None:
        product["price"] = product_data.price
    if product_data.category is not None:
        product["category"] = product_data.category
    if product_data.stock is not None:
        product["stock"] = product_data.stock
    if product_data.image_url is not None:
        product["image_url"] = product_data.image_url
    
    return Product(**product)


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, admin_user: User = Depends(get_admin_user)):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    products_db.remove(product)
    return None


@app.get("/api/cart", response_model=Cart)
def get_cart(current_user: User = Depends(get_current_user)):
    cart = carts_db.get(current_user.id)
    if not cart:
        cart = {"user_id": current_user.id, "items": [], "updated_at": datetime.now().isoformat()}
        carts_db[current_user.id] = cart
    return Cart(**cart)


@app.post("/api/cart/items", response_model=Cart)
def add_to_cart(cart_item: CartItem, current_user: User = Depends(get_current_user)):
    product = next((p for p in products_db if p["id"] == cart_item.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["stock"] < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    cart = carts_db.get(current_user.id)
    if not cart:
        cart = {"user_id": current_user.id, "items": [], "updated_at": datetime.now().isoformat()}
        carts_db[current_user.id] = cart
    
    existing_item = next((item for item in cart["items"] if item["product_id"] == cart_item.product_id), None)
    if existing_item:
        existing_item["quantity"] += cart_item.quantity
    else:
        cart["items"].append({"product_id": cart_item.product_id, "quantity": cart_item.quantity})
    
    cart["updated_at"] = datetime.now().isoformat()
    return Cart(**cart)


@app.put("/api/cart/items/{product_id}", response_model=Cart)
def update_cart_item(product_id: str, quantity: int, current_user: User = Depends(get_current_user)):
    if quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity must be non-negative")
    
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    cart = carts_db.get(current_user.id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    item = next((item for item in cart["items"] if item["product_id"] == product_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    if quantity == 0:
        cart["items"].remove(item)
    else:
        if product["stock"] < quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        item["quantity"] = quantity
    
    cart["updated_at"] = datetime.now().isoformat()
    return Cart(**cart)


@app.delete("/api/cart/items/{product_id}", response_model=Cart)
def remove_from_cart(product_id: str, current_user: User = Depends(get_current_user)):
    cart = carts_db.get(current_user.id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    item = next((item for item in cart["items"] if item["product_id"] == product_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    cart["items"].remove(item)
    cart["updated_at"] = datetime.now().isoformat()
    return Cart(**cart)


@app.delete("/api/cart", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(current_user: User = Depends(get_current_user)):
    cart = carts_db.get(current_user.id)
    if cart:
        cart["items"] = []
        cart["updated_at"] = datetime.now().isoformat()
    return None


@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, current_user: User = Depends(get_current_user)):
    cart = carts_db.get(current_user.id)
    if not cart or not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    order_items = []
    total_amount = 0.0
    
    for cart_item in cart["items"]:
        product = next((p for p in products_db if p["id"] == cart_item["product_id"]), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {cart_item['product_id']} not found")
        
        if product["stock"] < cart_item["quantity"]:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product['name']}")
        
        item_total = product["price"] * cart_item["quantity"]
        order_items.append({
            "product_id": product["id"],
            "product_name": product["name"],
            "quantity": cart_item["quantity"],
            "price": product["price"],
            "subtotal": item_total
        })
        total_amount += item_total
        product["stock"] -= cart_item["quantity"]
    
    order = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "items": order_items,
        "total_amount": total_amount,
        "status": "pending",
        "payment_method": order_data.payment_method,
        "shipping_address": order_data.shipping_address,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    orders_db.append(order)
    
    cart["items"] = []
    cart["updated_at"] = datetime.now().isoformat()
    
    return Order(**order)


@app.get("/api/orders", response_model=List[Order])
def get_orders(current_user: User = Depends(get_current_user)):
    user_orders = [o for o in orders_db if o["user_id"] == current_user.id]
    return [Order(**o) for o in user_orders]


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str, current_user: User = Depends(get_current_user)):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["user_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Order(**order)


@app.put("/api/orders/{order_id}/status", response_model=Order)
def update_order_status(order_id: str, status_data: OrderStatus, admin_user: User = Depends(get_admin_user)):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    if status_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    order["status"] = status_data.status
    order["updated_at"] = datetime.now().isoformat()
    
    return Order(**order)


@app.get("/api/admin/orders", response_model=List[Order])
def get_all_orders(admin_user: User = Depends(get_admin_user)):
    return [Order(**o) for o in orders_db]


@app.post("/api/reviews", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(review_data: ReviewCreate, current_user: User = Depends(get_current_user)):
    product = next((p for p in products_db if p["id"] == review_data.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    existing_review = next((r for r in reviews_db if r["product_id"] == review_data.product_id and r["user_id"] == current_user.id), None)
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    review = {
        "id": str(uuid.uuid4()),
        "product_id": review_data.product_id,
        "user_id": current_user.id,
        "username": current_user.username,
        "rating": review_data.rating,
        "comment": review_data.comment,
        "created_at": datetime.now().isoformat()
    }
    reviews_db.append(review)
    
    product_reviews = [r for r in reviews_db if r["product_id"] == review_data.product_id]
    total_rating = sum(r["rating"] for r in product_reviews)
    product["rating"] = round(total_rating / len(product_reviews), 1)
    product["review_count"] = len(product_reviews)
    
    return Review(**review)


@app.get("/api/products/{product_id}/reviews", response_model=List[Review])
def get_product_reviews(product_id: str):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_reviews = [r for r in reviews_db if r["product_id"] == product_id]
    return [Review(**r) for r in product_reviews]


@app.get("/api/recommendations", response_model=List[Product])
def get_recommendations(current_user: User = Depends(get_current_user)):
    user_orders = [o for o in orders_db if o["user_id"] == current_user.id]
    
    if not user_orders:
        top_rated = sorted(products_db, key=lambda p: p["rating"], reverse=True)[:5]
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
    
    recommendations.sort(key=lambda p: p["rating"], reverse=True)
    
    if len(recommendations) < 5:
        other_products = [p for p in products_db if p["id"] not in purchased_product_ids and p not in recommendations]
        other_products.sort(key=lambda p: p["rating"], reverse=True)
        recommendations.extend(other_products[:5-len(recommendations)])
    
    return [Product(**p) for p in recommendations[:5]]


@app.get("/api/categories")
def get_categories():
    categories = list(set(p["category"] for p in products_db))
    return {"categories": sorted(categories)}


@app.get("/api/stats")
def get_statistics(admin_user: User = Depends(get_admin_user)):
    total_products = len(products_db)
    total_orders = len(orders_db)
    total_revenue = sum(o["total_amount"] for o in orders_db)
    total_users = len([u for u in users_db if not u["is_admin"]])
    
    pending_orders = len([o for o in orders_db if o["status"] == "pending"])
    processing_orders = len([o for o in orders_db if o["status"] == "processing"])
    shipped_orders = len([o for o in orders_db if o["status"] == "shipped"])
    delivered_orders = len([o for o in orders_db if o["status"] == "delivered"])
    
    low_stock_products = [Product(**p) for p in products_db if p["stock"] < 10]
    
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "total_users": total_users,
        "order_status_breakdown": {
            "pending": pending_orders,
            "processing": processing_orders,
            "shipped": shipped_orders,
            "delivered": delivered_orders
        },
        "low_stock_products": low_stock_products,
        "total_reviews": len(reviews_db)
    }