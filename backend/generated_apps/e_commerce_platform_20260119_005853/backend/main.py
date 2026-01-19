from fastapi import FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import uuid
import hashlib
from collections import defaultdict

app = FastAPI(title="E-Commerce Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class User(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    is_admin: bool = False
    created_at: str


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: Optional[str] = None
    average_rating: float = 0.0
    total_reviews: int = 0
    created_at: str


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: Optional[str] = None


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
    total: float


class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float


class Order(BaseModel):
    id: str
    user_id: str
    items: List[OrderItem]
    total: float
    status: str
    payment_method: str
    shipping_address: str
    created_at: str


class OrderCreate(BaseModel):
    payment_method: str
    shipping_address: str


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


class PaymentProcess(BaseModel):
    card_number: str
    expiry: str
    cvv: str
    amount: float


class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float


users_db = []
sessions_db = {}
products_db = []
carts_db = {}
orders_db = []
reviews_db = []
user_behavior_db = defaultdict(list)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_id() -> str:
    return str(uuid.uuid4())


def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user_id = sessions_db.get(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)


def calculate_cart_total(items: List[CartItem]) -> float:
    total = 0.0
    for item in items:
        product = next((p for p in products_db if p["id"] == item.product_id), None)
        if product:
            total += product["price"] * item.quantity
    return round(total, 2)


def get_product_recommendations(user_id: str) -> List[Product]:
    user_views = user_behavior_db.get(user_id, [])
    if not user_views:
        return [Product(**p) for p in products_db[:3]]
    
    viewed_categories = [p["category"] for p in products_db if p["id"] in user_views]
    
    recommendations = []
    for product in products_db:
        if product["id"] not in user_views and product["category"] in viewed_categories:
            recommendations.append(Product(**product))
    
    if len(recommendations) < 3:
        for product in products_db:
            if product["id"] not in user_views and Product(**product) not in recommendations:
                recommendations.append(Product(**product))
    
    return recommendations[:5]


admin_user = {
    "id": generate_id(),
    "email": "admin@ecommerce.com",
    "password": hash_password("admin123"),
    "full_name": "Admin User",
    "phone": "+1234567890",
    "is_admin": True,
    "created_at": datetime.now().isoformat()
}
users_db.append(admin_user)

seed_products = [
    {
        "id": generate_id(),
        "name": "Wireless Headphones",
        "description": "High-quality Bluetooth headphones with noise cancellation",
        "price": 99.99,
        "category": "Electronics",
        "stock": 50,
        "image_url": "https://example.com/headphones.jpg",
        "average_rating": 4.5,
        "total_reviews": 120,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": generate_id(),
        "name": "Smart Watch",
        "description": "Feature-rich smartwatch with fitness tracking",
        "price": 199.99,
        "category": "Electronics",
        "stock": 30,
        "image_url": "https://example.com/smartwatch.jpg",
        "average_rating": 4.7,
        "total_reviews": 85,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": generate_id(),
        "name": "Running Shoes",
        "description": "Comfortable running shoes for all terrains",
        "price": 79.99,
        "category": "Sports",
        "stock": 100,
        "image_url": "https://example.com/shoes.jpg",
        "average_rating": 4.3,
        "total_reviews": 200,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": generate_id(),
        "name": "Coffee Maker",
        "description": "Automatic coffee maker with programmable features",
        "price": 149.99,
        "category": "Home",
        "stock": 25,
        "image_url": "https://example.com/coffee.jpg",
        "average_rating": 4.6,
        "total_reviews": 150,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": generate_id(),
        "name": "Yoga Mat",
        "description": "Non-slip yoga mat with carrying strap",
        "price": 29.99,
        "category": "Sports",
        "stock": 75,
        "image_url": "https://example.com/yoga.jpg",
        "average_rating": 4.4,
        "total_reviews": 95,
        "created_at": datetime.now().isoformat()
    }
]
products_db.extend(seed_products)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "users": len(users_db),
        "products": len(products_db),
        "orders": len(orders_db)
    }


@app.post("/api/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister):
    if any(u["email"] == user_data.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = {
        "id": generate_id(),
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "is_admin": False,
        "created_at": datetime.now().isoformat()
    }
    users_db.append(user)
    
    return User(**{k: v for k, v in user.items() if k != "password"})


@app.post("/api/auth/login")
def login_user(credentials: UserLogin):
    user = next((u for u in users_db if u["email"] == credentials.email), None)
    
    if not user or user["password"] != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = generate_id()
    sessions_db[token] = user["id"]
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": User(**{k: v for k, v in user.items() if k != "password"})
    }


@app.get("/api/auth/me", response_model=User)
def get_current_user_info(authorization: Optional[str] = Header(None)):
    return get_current_user(authorization)


@app.get("/api/products", response_model=List[Product])
def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = None
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
    
    return [Product(**p) for p in filtered_products]


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str, authorization: Optional[str] = Header(None)):
    product = next((p for p in products_db if p["id"] == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if authorization and authorization.startswith("Bearer "):
        try:
            user = get_current_user(authorization)
            if product_id not in user_behavior_db[user.id]:
                user_behavior_db[user.id].append(product_id)
        except:
            pass
    
    return Product(**product)


@app.post("/api/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    product = {
        "id": generate_id(),
        "name": product_data.name,
        "description": product_data.description,
        "price": product_data.price,
        "category": product_data.category,
        "stock": product_data.stock,
        "image_url": product_data.image_url,
        "average_rating": 0.0,
        "total_reviews": 0,
        "created_at": datetime.now().isoformat()
    }
    products_db.append(product)
    
    return Product(**product)


@app.put("/api/products/{product_id}", response_model=Product)
def update_product(product_id: str, product_data: ProductUpdate, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
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
def delete_product(product_id: str, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    product = next((p for p in products_db if p["id"] == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    products_db.remove(product)
    return None


@app.get("/api/cart", response_model=Cart)
def get_cart(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    cart = carts_db.get(user.id, {"user_id": user.id, "items": []})
    total = calculate_cart_total(cart["items"])
    
    return Cart(user_id=cart["user_id"], items=cart["items"], total=total)


@app.post("/api/cart/items", response_model=Cart)
def add_to_cart(cart_item: CartItem, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    product = next((p for p in products_db if p["id"] == cart_item.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["stock"] < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    if user.id not in carts_db:
        carts_db[user.id] = {"user_id": user.id, "items": []}
    
    existing_item = next((item for item in carts_db[user.id]["items"] if item.product_id == cart_item.product_id), None)
    
    if existing_item:
        existing_item.quantity += cart_item.quantity
    else:
        carts_db[user.id]["items"].append(cart_item)
    
    total = calculate_cart_total(carts_db[user.id]["items"])
    
    return Cart(user_id=user.id, items=carts_db[user.id]["items"], total=total)


@app.put("/api/cart/items/{product_id}", response_model=Cart)
def update_cart_item(product_id: str, quantity: int, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    if user.id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    item = next((item for item in carts_db[user.id]["items"] if item.product_id == product_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    product = next((p for p in products_db if p["id"] == product_id), None)
    if product["stock"] < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    item.quantity = quantity
    
    total = calculate_cart_total(carts_db[user.id]["items"])
    
    return Cart(user_id=user.id, items=carts_db[user.id]["items"], total=total)


@app.delete("/api/cart/items/{product_id}", response_model=Cart)
def remove_from_cart(product_id: str, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    if user.id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    carts_db[user.id]["items"] = [item for item in carts_db[user.id]["items"] if item.product_id != product_id]
    
    total = calculate_cart_total(carts_db[user.id]["items"])
    
    return Cart(user_id=user.id, items=carts_db[user.id]["items"], total=total)


@app.delete("/api/cart", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    if user.id in carts_db:
        carts_db[user.id]["items"] = []
    
    return None


@app.post("/api/payment/process", response_model=PaymentResponse)
def process_payment(payment: PaymentProcess, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    if len(payment.card_number) != 16:
        raise HTTPException(status_code=400, detail="Invalid card number")
    
    transaction = {
        "transaction_id": generate_id(),
        "status": "completed",
        "amount": payment.amount
    }
    
    return PaymentResponse(**transaction)


@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    if user.id not in carts_db or not carts_db[user.id]["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    order_items = []
    total = 0.0
    
    for cart_item in carts_db[user.id]["items"]:
        product = next((p for p in products_db if p["id"] == cart_item.product_id), None)
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {cart_item.product_id} not found")
        
        if product["stock"] < cart_item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product['name']}")
        
        product["stock"] -= cart_item.quantity
        
        order_item = OrderItem(
            product_id=cart_item.product_id,
            product_name=product["name"],
            quantity=cart_item.quantity,
            price=product["price"]
        )
        order_items.append(order_item)
        total += product["price"] * cart_item.quantity
    
    order = {
        "id": generate_id(),
        "user_id": user.id,
        "items": order_items,
        "total": round(total, 2),
        "status": "pending",
        "payment_method": order_data.payment_method,
        "shipping_address": order_data.shipping_address,
        "created_at": datetime.now().isoformat()
    }
    
    orders_db.append(order)
    carts_db[user.id]["items"] = []
    
    return Order(**order)


@app.get("/api/orders", response_model=List[Order])
def get_orders(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    user_orders = [o for o in orders_db if o["user_id"] == user.id]
    
    return [Order(**o) for o in user_orders]


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    order = next((o for o in orders_db if o["id"] == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["user_id"] != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Order(**order)


@app.put("/api/orders/{order_id}/status", response_model=Order)
def update_order_status(order_id: str, new_status: str, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    order = next((o for o in orders_db if o["id"] == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    order["status"] = new_status
    
    return Order(**order)


@app.get("/api/admin/orders", response_model=List[Order])
def get_all_orders(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return [Order(**o) for o in orders_db]


@app.get("/api/products/{product_id}/reviews", response_model=List[Review])
def get_product_reviews(product_id: str):
    product = next((p for p in products_db if p["id"] == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_reviews = [r for r in reviews_db if r["product_id"] == product_id]
    
    return [Review(**r) for r in product_reviews]


@app.post("/api/reviews", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(review_data: ReviewCreate, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    product = next((p for p in products_db if p["id"] == review_data.product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    user_order = any(
        o["user_id"] == user.id and any(item.product_id == review_data.product_id for item in o["items"])
        for o in orders_db
    )
    
    if not user_order:
        raise HTTPException(status_code=400, detail="You must purchase this product before reviewing")
    
    existing_review = next((r for r in reviews_db if r["product_id"] == review_data.product_id and r["user_id"] == user.id), None)
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    review = {
        "id": generate_id(),
        "product_id": review_data.product_id,
        "user_id": user.id,
        "user_name": user.full_name,
        "rating": review_data.rating,
        "comment": review_data.comment,
        "created_at": datetime.now().isoformat()
    }
    
    reviews_db.append(review)
    
    product_reviews = [r for r in reviews_db if r["product_id"] == review_data.product_id]
    total_rating = sum(r["rating"] for r in product_reviews)
    product["average_rating"] = round(total_rating / len(product_reviews), 1)
    product["total_reviews"] = len(product_reviews)
    
    return Review(**review)


@app.get("/api/recommendations", response_model=List[Product])
def get_recommendations(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    recommendations = get_product_recommendations(user.id)
    
    return recommendations


@app.get("/api/categories")
def get_categories():
    categories = list(set(p["category"] for p in products_db))
    
    return {
        "categories": [
            {
                "name": cat,
                "count": len([p for p in products_db if p["category"] == cat])
            }
            for cat in categories
        ]
    }


@app.get("/api/admin/stats")
def get_admin_stats(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_revenue = sum(o["total"] for o in orders_db)
    total_orders = len(orders_db)
    total_products = len(products_db)
    total_users = len([u for u in users_db if not u["is_admin"]])
    
    low_stock_products = [Product(**p) for p in products_db if p["stock"] < 10]
    
    recent_orders = sorted(orders_db, key=lambda x: x["created_at"], reverse=True)[:5]
    
    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "total_products": total_products,
        "total_users": total_users,
        "low_stock_products": low_stock_products,
        "recent_orders": [Order(**o) for o in recent_orders]
    }