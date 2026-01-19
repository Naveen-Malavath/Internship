from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import uuid
from collections import defaultdict

app = FastAPI(
    title="E-Commerce Platform",
    description="Complete e-commerce backend with user management, products, cart, and orders",
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


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class User(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    role: UserRole
    created_at: str


class UserResponse(BaseModel):
    user: User
    token: str


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


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: Optional[str] = None
    average_rating: float
    review_count: int
    created_at: str


class ReviewCreate(BaseModel):
    product_id: str
    rating: int
    comment: str


class Review(BaseModel):
    id: str
    product_id: str
    user_id: str
    user_name: str
    rating: int
    comment: str
    created_at: str


class CartItem(BaseModel):
    product_id: str
    quantity: int


class CartItemResponse(BaseModel):
    product_id: str
    product_name: str
    price: float
    quantity: int
    subtotal: float


class Cart(BaseModel):
    user_id: str
    items: List[CartItemResponse]
    total: float


class CheckoutRequest(BaseModel):
    payment_method: str
    shipping_address: str


class OrderItem(BaseModel):
    product_id: str
    product_name: str
    price: float
    quantity: int
    subtotal: float


class Order(BaseModel):
    id: str
    user_id: str
    items: List[OrderItem]
    total: float
    status: OrderStatus
    payment_status: PaymentStatus
    payment_method: str
    shipping_address: str
    created_at: str
    updated_at: str


class RecommendationResponse(BaseModel):
    product_id: str
    product_name: str
    price: float
    category: str
    reason: str


users_db = {}
products_db = {}
reviews_db = {}
carts_db = {}
orders_db = {}
tokens_db = {}
user_views_db = defaultdict(list)
user_purchases_db = defaultdict(list)


def generate_id():
    return str(uuid.uuid4())


def get_current_timestamp():
    return datetime.utcnow().isoformat()


def verify_token(token: str) -> Optional[str]:
    return tokens_db.get(token)


def calculate_product_rating(product_id: str) -> tuple:
    product_reviews = [r for r in reviews_db.values() if r["product_id"] == product_id]
    if not product_reviews:
        return 0.0, 0
    total_rating = sum(r["rating"] for r in product_reviews)
    count = len(product_reviews)
    return round(total_rating / count, 2), count


users_db["user1"] = {
    "id": "user1",
    "email": "john@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "address": "123 Main St, New York, NY 10001",
    "role": UserRole.CUSTOMER,
    "created_at": get_current_timestamp()
}

users_db["admin1"] = {
    "id": "admin1",
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "Admin User",
    "phone": "+1987654321",
    "address": "456 Admin Blvd, New York, NY 10002",
    "role": UserRole.ADMIN,
    "created_at": get_current_timestamp()
}

users_db["user2"] = {
    "id": "user2",
    "email": "jane@example.com",
    "password": "password456",
    "full_name": "Jane Smith",
    "phone": "+1122334455",
    "address": "789 Oak Ave, Los Angeles, CA 90001",
    "role": UserRole.CUSTOMER,
    "created_at": get_current_timestamp()
}

products_db["prod1"] = {
    "id": "prod1",
    "name": "Wireless Bluetooth Headphones",
    "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life",
    "price": 79.99,
    "category": "Electronics",
    "stock": 50,
    "image_url": "https://example.com/headphones.jpg",
    "created_at": get_current_timestamp()
}

products_db["prod2"] = {
    "id": "prod2",
    "name": "Smart Fitness Watch",
    "description": "Track your health and fitness with this advanced smartwatch featuring heart rate monitoring",
    "price": 149.99,
    "category": "Electronics",
    "stock": 30,
    "image_url": "https://example.com/watch.jpg",
    "created_at": get_current_timestamp()
}

products_db["prod3"] = {
    "id": "prod3",
    "name": "Organic Cotton T-Shirt",
    "description": "Comfortable and eco-friendly t-shirt made from 100% organic cotton",
    "price": 24.99,
    "category": "Clothing",
    "stock": 100,
    "image_url": "https://example.com/tshirt.jpg",
    "created_at": get_current_timestamp()
}

products_db["prod4"] = {
    "id": "prod4",
    "name": "Stainless Steel Water Bottle",
    "description": "Insulated water bottle keeps drinks cold for 24 hours or hot for 12 hours",
    "price": 29.99,
    "category": "Home & Kitchen",
    "stock": 75,
    "image_url": "https://example.com/bottle.jpg",
    "created_at": get_current_timestamp()
}

products_db["prod5"] = {
    "id": "prod5",
    "name": "Yoga Mat Premium",
    "description": "Non-slip yoga mat with extra cushioning for comfort during workouts",
    "price": 39.99,
    "category": "Sports",
    "stock": 60,
    "image_url": "https://example.com/yogamat.jpg",
    "created_at": get_current_timestamp()
}

reviews_db["rev1"] = {
    "id": "rev1",
    "product_id": "prod1",
    "user_id": "user1",
    "user_name": "John Doe",
    "rating": 5,
    "comment": "Amazing sound quality and very comfortable to wear!",
    "created_at": get_current_timestamp()
}

reviews_db["rev2"] = {
    "id": "rev2",
    "product_id": "prod1",
    "user_id": "user2",
    "user_name": "Jane Smith",
    "rating": 4,
    "comment": "Great headphones but a bit pricey",
    "created_at": get_current_timestamp()
}

reviews_db["rev3"] = {
    "id": "rev3",
    "product_id": "prod2",
    "user_id": "user1",
    "user_name": "John Doe",
    "rating": 5,
    "comment": "Perfect for tracking my workouts!",
    "created_at": get_current_timestamp()
}

reviews_db["rev4"] = {
    "id": "rev4",
    "product_id": "prod3",
    "user_id": "user2",
    "user_name": "Jane Smith",
    "rating": 5,
    "comment": "Very soft and comfortable. Love it!",
    "created_at": get_current_timestamp()
}

tokens_db["token_user1"] = "user1"
tokens_db["token_admin1"] = "admin1"
tokens_db["token_user2"] = "user2"


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": get_current_timestamp(),
        "service": "e-commerce-api"
    }


@app.post("/api/auth/register", response_model=UserResponse)
def register_user(user_data: UserCreate):
    for user in users_db.values():
        if user["email"] == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = generate_id()
    token = f"token_{user_id}"
    
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "password": user_data.password,
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "address": user_data.address,
        "role": UserRole.CUSTOMER,
        "created_at": get_current_timestamp()
    }
    
    users_db[user_id] = new_user
    tokens_db[token] = user_id
    
    user_response = User(**{k: v for k, v in new_user.items() if k != "password"})
    
    return UserResponse(user=user_response, token=token)


@app.post("/api/auth/login", response_model=UserResponse)
def login_user(credentials: UserLogin):
    for user in users_db.values():
        if user["email"] == credentials.email and user["password"] == credentials.password:
            token = f"token_{user['id']}"
            tokens_db[token] = user["id"]
            
            user_response = User(**{k: v for k, v in user.items() if k != "password"})
            return UserResponse(user=user_response, token=token)
    
    raise HTTPException(status_code=401, detail="Invalid email or password")


@app.get("/api/users/me", response_model=User)
def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = users_db[user_id]
    return User(**{k: v for k, v in user.items() if k != "password"})


@app.get("/api/products", response_model=List[Product])
def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query(None, regex="^(price_asc|price_desc|rating|newest)$")
):
    products = list(products_db.values())
    
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    
    if search:
        search_lower = search.lower()
        products = [
            p for p in products 
            if search_lower in p["name"].lower() or search_lower in p["description"].lower()
        ]
    
    if min_price is not None:
        products = [p for p in products if p["price"] >= min_price]
    
    if max_price is not None:
        products = [p for p in products if p["price"] <= max_price]
    
    result = []
    for p in products:
        avg_rating, review_count = calculate_product_rating(p["id"])
        result.append(Product(
            **p,
            average_rating=avg_rating,
            review_count=review_count
        ))
    
    if sort_by == "price_asc":
        result.sort(key=lambda x: x.price)
    elif sort_by == "price_desc":
        result.sort(key=lambda x: x.price, reverse=True)
    elif sort_by == "rating":
        result.sort(key=lambda x: x.average_rating, reverse=True)
    elif sort_by == "newest":
        result.sort(key=lambda x: x.created_at, reverse=True)
    
    return result


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str, authorization: Optional[str] = Header(None)):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if authorization:
        token = authorization.replace("Bearer ", "")
        user_id = verify_token(token)
        if user_id:
            user_views_db[user_id].append({
                "product_id": product_id,
                "timestamp": get_current_timestamp()
            })
    
    product = products_db[product_id]
    avg_rating, review_count = calculate_product_rating(product_id)
    
    return Product(
        **product,
        average_rating=avg_rating,
        review_count=review_count
    )


@app.post("/api/products", response_model=Product)
def create_product(product_data: ProductCreate, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if users_db[user_id]["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    product_id = generate_id()
    new_product = {
        "id": product_id,
        **product_data.dict(),
        "created_at": get_current_timestamp()
    }
    
    products_db[product_id] = new_product
    
    return Product(**new_product, average_rating=0.0, review_count=0)


@app.put("/api/products/{product_id}", response_model=Product)
def update_product(product_id: str, product_data: ProductUpdate, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if users_db[user_id]["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = products_db[product_id]
    update_data = product_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        product[key] = value
    
    avg_rating, review_count = calculate_product_rating(product_id)
    
    return Product(**product, average_rating=avg_rating, review_count=review_count)


@app.delete("/api/products/{product_id}")
def delete_product(product_id: str, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if users_db[user_id]["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    del products_db[product_id]
    
    return {"message": "Product deleted successfully"}


@app.get("/api/products/{product_id}/reviews", response_model=List[Review])
def get_product_reviews(product_id: str):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_reviews = [
        Review(**review) 
        for review in reviews_db.values() 
        if review["product_id"] == product_id
    ]
    
    return product_reviews


@app.post("/api/reviews", response_model=Review)
def create_review(review_data: ReviewCreate, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if review_data.product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    review_id = generate_id()
    user = users_db[user_id]
    
    new_review = {
        "id": review_id,
        "product_id": review_data.product_id,
        "user_id": user_id,
        "user_name": user["full_name"],
        "rating": review_data.rating,
        "comment": review_data.comment,
        "created_at": get_current_timestamp()
    }
    
    reviews_db[review_id] = new_review
    
    return Review(**new_review)


@app.get("/api/cart", response_model=Cart)
def get_cart(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    cart_items = carts_db.get(user_id, [])
    items_response = []
    total = 0.0
    
    for item in cart_items:
        if item["product_id"] in products_db:
            product = products_db[item["product_id"]]
            subtotal = product["price"] * item["quantity"]
            items_response.append(CartItemResponse(
                product_id=item["product_id"],
                product_name=product["name"],
                price=product["price"],
                quantity=item["quantity"],
                subtotal=subtotal
            ))
            total += subtotal
    
    return Cart(user_id=user_id, items=items_response, total=round(total, 2))


@app.post("/api/cart", response_model=Cart)
def add_to_cart(cart_item: CartItem, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if cart_item.product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = products_db[cart_item.product_id]
    
    if cart_item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    if cart_item.quantity > product["stock"]:
        raise HTTPException(status_code=400, detail="Not enough stock available")
    
    if user_id not in carts_db:
        carts_db[user_id] = []
    
    cart = carts_db[user_id]
    existing_item = None
    
    for item in cart:
        if item["product_id"] == cart_item.product_id:
            existing_item = item
            break
    
    if existing_item:
        new_quantity = existing_item["quantity"] + cart_item.quantity
        if new_quantity > product["stock"]:
            raise HTTPException(status_code=400, detail="Not enough stock available")
        existing_item["quantity"] = new_quantity
    else:
        cart.append({
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity
        })
    
    return get_cart(authorization=authorization)


@app.put("/api/cart/{product_id}", response_model=Cart)
def update_cart_item(product_id: str, quantity: int, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity cannot be negative")
    
    product = products_db[product_id]
    
    if quantity > product["stock"]:
        raise HTTPException(status_code=400, detail="Not enough stock available")
    
    if user_id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    cart = carts_db[user_id]
    item_found = False
    
    for item in cart:
        if item["product_id"] == product_id:
            if quantity == 0:
                cart.remove(item)
            else:
                item["quantity"] = quantity
            item_found = True
            break
    
    if not item_found:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    return get_cart(authorization=authorization)


@app.delete("/api/cart/{product_id}")
def remove_from_cart(product_id: str, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if user_id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    cart = carts_db[user_id]
    item_found = False
    
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            item_found = True
            break
    
    if not item_found:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    return {"message": "Item removed from cart"}


@app.post("/api/checkout", response_model=Order)
def checkout(checkout_data: CheckoutRequest, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if user_id not in carts_db or not carts_db[user_id]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart = carts_db[user_id]
    order_items = []
    total = 0.0
    
    for cart_item in cart:
        product_id = cart_item["product_id"]
        quantity = cart_item["quantity"]
        
        if product_id not in products_db:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        
        product = products_db[product_id]
        
        if quantity > product["stock"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough stock for {product['name']}"
            )
        
        subtotal = product["price"] * quantity
        order_items.append(OrderItem(
            product_id=product_id,
            product_name=product["name"],
            price=product["price"],
            quantity=quantity,
            subtotal=subtotal
        ))
        total += subtotal
        
        product["stock"] -= quantity
    
    order_id = generate_id()
    timestamp = get_current_timestamp()
    
    new_order = {
        "id": order_id,
        "user_id": user_id,
        "items": [item.dict() for item in order_items],
        "total": round(total, 2),
        "status": OrderStatus.PENDING,
        "payment_status": PaymentStatus.COMPLETED,
        "payment_method": checkout_data.payment_method,
        "shipping_address": checkout_data.shipping_address,
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    orders_db[order_id] = new_order
    
    for item in order_items:
        user_purchases_db[user_id].append({
            "product_id": item.product_id,
            "timestamp": timestamp
        })
    
    carts_db[user_id] = []
    
    return Order(**new_order)


@app.get("/api/orders", response_model=List[Order])
def get_user_orders(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_orders = [
        Order(**order)
        for order in orders_db.values()
        if order["user_id"] == user_id
    ]
    
    user_orders.sort(key=lambda x: x.created_at, reverse=True)
    
    return user_orders


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    if order["user_id"] != user_id and users_db[user_id]["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Order(**order)


@app.put("/api/orders/{order_id}/status", response_model=Order)
def update_order_status(
    order_id: str, 
    status: OrderStatus, 
    authorization: str = Header(...)
):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if users_db[user_id]["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    order["status"] = status
    order["updated_at"] = get_current_timestamp()
    
    return Order(**order)


@app.get("/api/admin/orders", response_model=List[Order])
def get_all_orders(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if users_db[user_id]["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    all_orders = [Order(**order) for order in orders_db.values()]
    all_orders.sort(key=lambda x: x.created_at, reverse=True)
    
    return all_orders


@app.get("/api/recommendations", response_model=List[RecommendationResponse])
def get_recommendations(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    recommendations = []
    
    user_purchases = user_purchases_db.get(user_id, [])
    purchased_products = {p["product_id"] for p in user_purchases}
    
    user_views = user_views_db.get(user_id, [])
    viewed_products = {v["product_id"] for v in user_views}
    
    if purchased_products:
        purchased_categories = {
            products_db[pid]["category"] 
            for pid in purchased_products 
            if pid in products_db
        }
        
        for product in products_db.values():
            if (product["id"] not in purchased_products and 
                product["category"] in purchased_categories):
                recommendations.append(RecommendationResponse(
                    product_id=product["id"],
                    product_name=product["name"],
                    price=product["price"],
                    category=product["category"],
                    reason="Based on your previous purchases"
                ))
    
    if viewed_products and len(recommendations) < 5:
        viewed_categories = {
            products_db[pid]["category"] 
            for pid in viewed_products 
            if pid in products_db
        }
        
        for product in products_db.values():
            if (product["id"] not in purchased_products and 
                product["id"] not in viewed_products and
                product["category"] in viewed_categories):
                exists = any(r.product_id == product["id"] for r in recommendations)
                if not exists:
                    recommendations.append(RecommendationResponse(
                        product_id=product["id"],
                        product_name=product["name"],
                        price=product["price"],
                        category=product["category"],
                        reason="Based on products you viewed"
                    ))
    
    if len(recommendations) < 5:
        top_rated = []
        for product in products_db.values():
            if product["id"] not in purchased_products:
                avg_rating, review_count = calculate_product_rating(product["id"])
                if review_count > 0:
                    top_rated.append((product, avg_rating))
        
        top_rated.sort(key=lambda x: x[1], reverse=True)
        
        for product, rating in top_rated:
            exists = any(r.product_id == product["id"] for r in recommendations)
            if not exists:
                recommendations.append(RecommendationResponse(
                    product_id=product["id"],
                    product_name=product["name"],
                    price=product["price"],
                    category=product["category"],
                    reason="Highly rated by customers"
                ))
    
    return recommendations[:5]


@app.get("/api/categories", response_model=List[str])
def get_categories():
    categories = set()
    for product in products_db.values():
        categories.add(product["category"])
    return sorted(list(categories))


@app.get("/api/admin/dashboard")
def get_dashboard_stats(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if users_db[user_id]["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_products = len(products_db)
    total_orders = len(orders_db)
    total_users = len([u for u in users_db.values() if u["role"] == UserRole.CUSTOMER])
    total_reviews = len(reviews_db)
    
    total_revenue = sum(order["total"] for order in orders_db.values())
    
    low_stock_products = [
        {"id": p["id"], "name": p["name"], "stock": p["stock"]}
        for p in products_db.values()
        if p["stock"] < 10
    ]
    
    recent_orders = sorted(
        [Order(**order) for order in orders_db.values()],
        key=lambda x: x.created_at,
        reverse=True
    )[:5]
    
    order_status_counts = {}
    for order in orders_db.values():
        status = order["status"]
        order_status_counts[status] = order_status_counts.get(status, 0) + 1
    
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_reviews": total_reviews,
        "total_revenue": round(total_revenue, 2),
        "low_stock_products": low_stock_products,
        "recent_orders": recent_orders,
        "order_status_counts": order_status_counts
    }