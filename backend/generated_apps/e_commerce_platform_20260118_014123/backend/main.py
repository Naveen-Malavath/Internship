from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import secrets
import hashlib
from enum import Enum

app = FastAPI(title="E-Commerce Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class User(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    created_at: str


class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: str
    password: str


class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: str
    rating: float
    reviews_count: int
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
    product_id: int
    quantity: int


class Cart(BaseModel):
    user_id: int
    items: List[CartItem]
    total: float
    updated_at: str


class CartAddItem(BaseModel):
    product_id: int
    quantity: int


class Review(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    comment: str
    user_name: str
    created_at: str


class ReviewCreate(BaseModel):
    product_id: int
    rating: int
    comment: str


class Order(BaseModel):
    id: int
    user_id: int
    items: List[Dict]
    total: float
    status: OrderStatus
    payment_status: PaymentStatus
    shipping_address: str
    created_at: str
    updated_at: str


class OrderCreate(BaseModel):
    shipping_address: str
    payment_method: str


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None


class Recommendation(BaseModel):
    product_id: int
    score: float
    reason: str


users_db = []
products_db = []
carts_db = {}
reviews_db = []
orders_db = []
tokens_db = {}
user_behavior_db = {}
next_user_id = 1
next_product_id = 1
next_review_id = 1
next_order_id = 1


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    token = credentials.credentials
    if token not in tokens_db:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return tokens_db[token]


def get_admin_user(current_user: Dict = Depends(get_current_user)) -> Dict:
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def init_seed_data():
    global next_user_id, next_product_id, next_review_id
    
    admin_password = hash_password("admin123")
    users_db.append({
        "id": next_user_id,
        "email": "admin@ecommerce.com",
        "password": admin_password,
        "full_name": "Admin User",
        "role": UserRole.ADMIN,
        "created_at": datetime.now().isoformat()
    })
    next_user_id += 1
    
    customer_password = hash_password("customer123")
    users_db.append({
        "id": next_user_id,
        "email": "customer@example.com",
        "password": customer_password,
        "full_name": "John Doe",
        "role": UserRole.CUSTOMER,
        "created_at": datetime.now().isoformat()
    })
    next_user_id += 1
    
    seed_products = [
        {
            "id": next_product_id,
            "name": "Wireless Bluetooth Headphones",
            "description": "Premium noise-cancelling headphones with 30-hour battery life",
            "price": 149.99,
            "category": "Electronics",
            "stock": 50,
            "image_url": "https://example.com/headphones.jpg",
            "rating": 4.5,
            "reviews_count": 124,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": next_product_id + 1,
            "name": "Smart Fitness Watch",
            "description": "Track your fitness goals with GPS and heart rate monitoring",
            "price": 199.99,
            "category": "Electronics",
            "stock": 30,
            "image_url": "https://example.com/watch.jpg",
            "rating": 4.7,
            "reviews_count": 89,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": next_product_id + 2,
            "name": "Leather Laptop Bag",
            "description": "Premium leather bag with padded laptop compartment",
            "price": 79.99,
            "category": "Accessories",
            "stock": 25,
            "image_url": "https://example.com/bag.jpg",
            "rating": 4.3,
            "reviews_count": 56,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": next_product_id + 3,
            "name": "Portable Power Bank 20000mAh",
            "description": "Fast charging power bank with dual USB ports",
            "price": 39.99,
            "category": "Electronics",
            "stock": 100,
            "image_url": "https://example.com/powerbank.jpg",
            "rating": 4.6,
            "reviews_count": 203,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": next_product_id + 4,
            "name": "Ergonomic Office Chair",
            "description": "Comfortable office chair with lumbar support and adjustable height",
            "price": 249.99,
            "category": "Furniture",
            "stock": 15,
            "image_url": "https://example.com/chair.jpg",
            "rating": 4.8,
            "reviews_count": 78,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    products_db.extend(seed_products)
    next_product_id += 5
    
    seed_reviews = [
        {
            "id": next_review_id,
            "product_id": 1,
            "user_id": 2,
            "rating": 5,
            "comment": "Excellent sound quality and very comfortable!",
            "user_name": "John Doe",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": next_review_id + 1,
            "product_id": 2,
            "user_id": 2,
            "rating": 4,
            "comment": "Great fitness tracker, battery life is amazing",
            "user_name": "John Doe",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": next_review_id + 2,
            "product_id": 4,
            "user_id": 2,
            "rating": 5,
            "comment": "Charges my phone super fast, highly recommended",
            "user_name": "John Doe",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    reviews_db.extend(seed_reviews)
    next_review_id += 3


@app.on_event("startup")
def startup_event():
    init_seed_data()


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
    global next_user_id
    
    for user in users_db:
        if user["email"] == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = {
        "id": next_user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "role": UserRole.CUSTOMER,
        "created_at": datetime.now().isoformat()
    }
    
    users_db.append(new_user)
    user_behavior_db[next_user_id] = {
        "viewed_products": [],
        "purchased_products": [],
        "categories_interest": {}
    }
    next_user_id += 1
    
    return User(
        id=new_user["id"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        role=new_user["role"],
        created_at=new_user["created_at"]
    )


@app.post("/api/auth/login")
def login_user(credentials: UserLogin):
    for user in users_db:
        if user["email"] == credentials.email:
            if verify_password(credentials.password, user["password"]):
                token = generate_token()
                tokens_db[token] = {
                    "id": user["id"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "role": user["role"]
                }
                return {
                    "access_token": token,
                    "token_type": "bearer",
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "full_name": user["full_name"],
                        "role": user["role"]
                    }
                }
    
    raise HTTPException(status_code=401, detail="Invalid email or password")


@app.get("/api/auth/me", response_model=User)
def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    for user in users_db:
        if user["id"] == current_user["id"]:
            return User(
                id=user["id"],
                email=user["email"],
                full_name=user["full_name"],
                role=user["role"],
                created_at=user["created_at"]
            )
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/api/products", response_model=List[Product])
def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None
):
    filtered_products = products_db.copy()
    
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
    
    if sort_by == "price_asc":
        filtered_products.sort(key=lambda x: x["price"])
    elif sort_by == "price_desc":
        filtered_products.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "rating":
        filtered_products.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "name":
        filtered_products.sort(key=lambda x: x["name"])
    
    return [Product(**p) for p in filtered_products]


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: int, current_user: Optional[Dict] = Depends(get_current_user)):
    for product in products_db:
        if product["id"] == product_id:
            if current_user:
                user_id = current_user["id"]
                if user_id not in user_behavior_db:
                    user_behavior_db[user_id] = {
                        "viewed_products": [],
                        "purchased_products": [],
                        "categories_interest": {}
                    }
                
                if product_id not in user_behavior_db[user_id]["viewed_products"]:
                    user_behavior_db[user_id]["viewed_products"].append(product_id)
                
                category = product["category"]
                if category not in user_behavior_db[user_id]["categories_interest"]:
                    user_behavior_db[user_id]["categories_interest"][category] = 0
                user_behavior_db[user_id]["categories_interest"][category] += 1
            
            return Product(**product)
    
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/api/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, admin: Dict = Depends(get_admin_user)):
    global next_product_id
    
    new_product = {
        "id": next_product_id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category": product.category,
        "stock": product.stock,
        "image_url": product.image_url,
        "rating": 0.0,
        "reviews_count": 0,
        "created_at": datetime.now().isoformat()
    }
    
    products_db.append(new_product)
    next_product_id += 1
    
    return Product(**new_product)


@app.put("/api/products/{product_id}", response_model=Product)
def update_product(product_id: int, product_update: ProductUpdate, admin: Dict = Depends(get_admin_user)):
    for product in products_db:
        if product["id"] == product_id:
            if product_update.name is not None:
                product["name"] = product_update.name
            if product_update.description is not None:
                product["description"] = product_update.description
            if product_update.price is not None:
                product["price"] = product_update.price
            if product_update.category is not None:
                product["category"] = product_update.category
            if product_update.stock is not None:
                product["stock"] = product_update.stock
            if product_update.image_url is not None:
                product["image_url"] = product_update.image_url
            
            return Product(**product)
    
    raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, admin: Dict = Depends(get_admin_user)):
    for i, product in enumerate(products_db):
        if product["id"] == product_id:
            products_db.pop(i)
            return
    
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/api/cart", response_model=Cart)
def get_cart(current_user: Dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    if user_id not in carts_db:
        return Cart(
            user_id=user_id,
            items=[],
            total=0.0,
            updated_at=datetime.now().isoformat()
        )
    
    cart = carts_db[user_id]
    total = 0.0
    
    for item in cart["items"]:
        product = next((p for p in products_db if p["id"] == item["product_id"]), None)
        if product:
            total += product["price"] * item["quantity"]
    
    cart["total"] = total
    cart["updated_at"] = datetime.now().isoformat()
    
    return Cart(**cart)


@app.post("/api/cart/items", response_model=Cart)
def add_to_cart(cart_item: CartAddItem, current_user: Dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    product = next((p for p in products_db if p["id"] == cart_item.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["stock"] < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    if user_id not in carts_db:
        carts_db[user_id] = {
            "user_id": user_id,
            "items": [],
            "total": 0.0,
            "updated_at": datetime.now().isoformat()
        }
    
    cart = carts_db[user_id]
    existing_item = next((item for item in cart["items"] if item["product_id"] == cart_item.product_id), None)
    
    if existing_item:
        existing_item["quantity"] += cart_item.quantity
    else:
        cart["items"].append({
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity
        })
    
    total = 0.0
    for item in cart["items"]:
        prod = next((p for p in products_db if p["id"] == item["product_id"]), None)
        if prod:
            total += prod["price"] * item["quantity"]
    
    cart["total"] = total
    cart["updated_at"] = datetime.now().isoformat()
    
    return Cart(**cart)


@app.delete("/api/cart/items/{product_id}", response_model=Cart)
def remove_from_cart(product_id: int, current_user: Dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    if user_id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    cart = carts_db[user_id]
    cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]
    
    total = 0.0
    for item in cart["items"]:
        product = next((p for p in products_db if p["id"] == item["product_id"]), None)
        if product:
            total += product["price"] * item["quantity"]
    
    cart["total"] = total
    cart["updated_at"] = datetime.now().isoformat()
    
    return Cart(**cart)


@app.delete("/api/cart", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(current_user: Dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    if user_id in carts_db:
        del carts_db[user_id]


@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, current_user: Dict = Depends(get_current_user)):
    global next_order_id
    
    user_id = current_user["id"]
    
    if user_id not in carts_db or not carts_db[user_id]["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart = carts_db[user_id]
    order_items = []
    total = 0.0
    
    for cart_item in cart["items"]:
        product = next((p for p in products_db if p["id"] == cart_item["product_id"]), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {cart_item['product_id']} not found")
        
        if product["stock"] < cart_item["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product['name']}"
            )
        
        item_total = product["price"] * cart_item["quantity"]
        total += item_total
        
        order_items.append({
            "product_id": product["id"],
            "product_name": product["name"],
            "quantity": cart_item["quantity"],
            "price": product["price"],
            "total": item_total
        })
        
        product["stock"] -= cart_item["quantity"]
    
    new_order = {
        "id": next_order_id,
        "user_id": user_id,
        "items": order_items,
        "total": total,
        "status": OrderStatus.PENDING,
        "payment_status": PaymentStatus.PENDING,
        "shipping_address": order_data.shipping_address,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    orders_db.append(new_order)
    next_order_id += 1
    
    if user_id not in user_behavior_db:
        user_behavior_db[user_id] = {
            "viewed_products": [],
            "purchased_products": [],
            "categories_interest": {}
        }
    
    for item in order_items:
        user_behavior_db[user_id]["purchased_products"].append(item["product_id"])
    
    del carts_db[user_id]
    
    return Order(**new_order)


@app.get("/api/orders", response_model=List[Order])
def get_orders(current_user: Dict = Depends(get_current_user)):
    user_id = current_user["id"]
    user_orders = [order for order in orders_db if order["user_id"] == user_id]
    return [Order(**order) for order in user_orders]


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: int, current_user: Dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    for order in orders_db:
        if order["id"] == order_id:
            if order["user_id"] != user_id and current_user["role"] != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail="Access denied")
            return Order(**order)
    
    raise HTTPException(status_code=404, detail="Order not found")


@app.put("/api/orders/{order_id}", response_model=Order)
def update_order(order_id: int, order_update: OrderUpdate, admin: Dict = Depends(get_admin_user)):
    for order in orders_db:
        if order["id"] == order_id:
            if order_update.status is not None:
                order["status"] = order_update.status
            if order_update.payment_status is not None:
                order["payment_status"] = order_update.payment_status
            
            order["updated_at"] = datetime.now().isoformat()
            return Order(**order)
    
    raise HTTPException(status_code=404, detail="Order not found")


@app.get("/api/products/{product_id}/reviews", response_model=List[Review])
def get_product_reviews(product_id: int):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_reviews = [review for review in reviews_db if review["product_id"] == product_id]
    return [Review(**review) for review in product_reviews]


@app.post("/api/reviews", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(review_data: ReviewCreate, current_user: Dict = Depends(get_current_user)):
    global next_review_id
    
    product = next((p for p in products_db if p["id"] == review_data.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    user_id = current_user["id"]
    existing_review = next(
        (r for r in reviews_db if r["product_id"] == review_data.product_id and r["user_id"] == user_id),
        None
    )
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    new_review = {
        "id": next_review_id,
        "product_id": review_data.product_id,
        "user_id": user_id,
        "rating": review_data.rating,
        "comment": review_data.comment,
        "user_name": current_user["full_name"],
        "created_at": datetime.now().isoformat()
    }
    
    reviews_db.append(new_review)
    next_review_id += 1
    
    product_reviews = [r for r in reviews_db if r["product_id"] == review_data.product_id]
    total_rating = sum(r["rating"] for r in product_reviews)
    product["rating"] = round(total_rating / len(product_reviews), 1)
    product["reviews_count"] = len(product_reviews)
    
    return Review(**new_review)


@app.get("/api/recommendations", response_model=List[Product])
def get_recommendations(current_user: Dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    if user_id not in user_behavior_db:
        top_rated = sorted(products_db, key=lambda x: x["rating"], reverse=True)[:5]
        return [Product(**p) for p in top_rated]
    
    behavior = user_behavior_db[user_id]
    viewed_ids = set(behavior["viewed_products"])
    purchased_ids = set(behavior["purchased_products"])
    
    recommendations = []
    
    if behavior["categories_interest"]:
        favorite_category = max(
            behavior["categories_interest"].items(),
            key=lambda x: x[1]
        )[0]
        
        category_products = [
            p for p in products_db
            if p["category"] == favorite_category
            and p["id"] not in viewed_ids
            and p["id"] not in purchased_ids
        ]
        
        recommendations.extend(sorted(category_products, key=lambda x: x["rating"], reverse=True)[:3])
    
    if purchased_ids:
        purchased_categories = set()
        for product in products_db:
            if product["id"] in purchased_ids:
                purchased_categories.add(product["category"])
        
        related_products = [
            p for p in products_db
            if p["category"] in purchased_categories
            and p["id"] not in purchased_ids
            and p["id"] not in viewed_ids
            and p not in recommendations
        ]
        
        recommendations.extend(sorted(related_products, key=lambda x: x["rating"], reverse=True)[:2])
    
    remaining_slots = 5 - len(recommendations)
    if remaining_slots > 0:
        other_products = [
            p for p in products_db
            if p not in recommendations
            and p["id"] not in viewed_ids
            and p["id"] not in purchased_ids
        ]
        
        recommendations.extend(sorted(other_products, key=lambda x: x["rating"], reverse=True)[:remaining_slots])
    
    return [Product(**p) for p in recommendations[:5]]


@app.get("/api/admin/dashboard")
def get_admin_dashboard(admin: Dict = Depends(get_admin_user)):
    total_revenue = sum(order["total"] for order in orders_db if order["payment_status"] == PaymentStatus.COMPLETED)
    
    pending_orders = [order for order in orders_db if order["status"] == OrderStatus.PENDING]
    
    low_stock_products = [p for p in products_db if p["stock"] < 10]
    
    top_rated_products = sorted(products_db, key=lambda x: x["rating"], reverse=True)[:5]
    
    category_sales = {}
    for order in orders_db:
        if order["payment_status"] == PaymentStatus.COMPLETED:
            for item in order["items"]:
                product = next((p for p in products_db if p["id"] == item["product_id"]), None)
                if product:
                    category = product["category"]
                    if category not in category_sales:
                        category_sales[category] = 0
                    category_sales[category] += item["total"]
    
    return {
        "total_users": len(users_db),
        "total_products": len(products_db),
        "total_orders": len(orders_db),
        "total_revenue": total_revenue,
        "pending_orders_count": len(pending_orders),
        "low_stock_products_count": len(low_stock_products),
        "low_stock_products": [{"id": p["id"], "name": p["name"], "stock": p["stock"]} for p in low_stock_products],
        "top_rated_products": [{"id": p["id"], "name": p["name"], "rating": p["rating"]} for p in top_rated_products],
        "category_sales": category_sales,
        "recent_orders": [
            {
                "id": order["id"],
                "user_id": order["user_id"],
                "total": order["total"],
                "status": order["status"],
                "created_at": order["created_at"]
            }
            for order in sorted(orders_db, key=lambda x: x["created_at"], reverse=True)[:10]
        ]
    }


@app.get("/api/categories", response_model=List[str])
def get_categories():
    categories = list(set(product["category"] for product in products_db))
    return sorted(categories)