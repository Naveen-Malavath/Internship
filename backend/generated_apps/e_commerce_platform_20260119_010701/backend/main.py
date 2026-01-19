from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import hashlib
import secrets
from collections import defaultdict

app = FastAPI(
    title="E-Commerce Platform API",
    description="A complete e-commerce platform with user management, products, cart, orders, and reviews",
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
    username: str
    email: str
    password: str
    full_name: str
    address: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    address: Optional[str] = None
    phone: Optional[str] = None
    created_at: str


class UserLogin(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    stock_quantity: int
    image_url: Optional[str] = None
    created_at: str
    average_rating: float = 0.0
    total_reviews: int = 0


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


class CartItem(BaseModel):
    product_id: int
    quantity: int


class CartItemResponse(BaseModel):
    product_id: int
    product_name: str
    product_price: float
    quantity: int
    subtotal: float


class CartResponse(BaseModel):
    user_id: int
    items: List[CartItemResponse]
    total: float


class OrderItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float
    subtotal: float


class Order(BaseModel):
    id: int
    user_id: int
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus
    payment_status: PaymentStatus
    shipping_address: str
    created_at: str
    updated_at: str


class OrderCreate(BaseModel):
    shipping_address: str
    payment_method: str


class Review(BaseModel):
    id: int
    product_id: int
    user_id: int
    username: str
    rating: int
    comment: str
    created_at: str


class ReviewCreate(BaseModel):
    product_id: int
    rating: int
    comment: str


class PaymentRequest(BaseModel):
    order_id: int
    payment_method: str
    card_number: Optional[str] = None


class PaymentResponse(BaseModel):
    payment_id: int
    order_id: int
    amount: float
    status: PaymentStatus
    transaction_date: str


users_db = []
products_db = []
carts_db = defaultdict(list)
orders_db = []
reviews_db = []
payments_db = []
sessions_db = {}
user_id_counter = 1
product_id_counter = 1
order_id_counter = 1
review_id_counter = 1
payment_id_counter = 1


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def get_user_by_token(token: str) -> Optional[dict]:
    user_id = sessions_db.get(token)
    if user_id:
        for user in users_db:
            if user["id"] == user_id:
                return user
    return None


def get_product_by_id(product_id: int) -> Optional[dict]:
    for product in products_db:
        if product["id"] == product_id:
            return product
    return None


def calculate_product_rating(product_id: int):
    product_reviews = [r for r in reviews_db if r["product_id"] == product_id]
    if product_reviews:
        avg_rating = sum(r["rating"] for r in product_reviews) / len(product_reviews)
        return round(avg_rating, 2), len(product_reviews)
    return 0.0, 0


users_db.append({
    "id": user_id_counter,
    "username": "admin",
    "email": "admin@ecommerce.com",
    "password": hash_password("admin123"),
    "full_name": "Admin User",
    "role": UserRole.ADMIN,
    "address": "123 Admin St, Admin City",
    "phone": "+1234567890",
    "created_at": datetime.now().isoformat()
})
user_id_counter += 1

users_db.append({
    "id": user_id_counter,
    "username": "john_doe",
    "email": "john@example.com",
    "password": hash_password("password123"),
    "full_name": "John Doe",
    "role": UserRole.CUSTOMER,
    "address": "456 Customer Ave, User City",
    "phone": "+1987654321",
    "created_at": datetime.now().isoformat()
})
user_id_counter += 1

products_db.extend([
    {
        "id": product_id_counter,
        "name": "Wireless Bluetooth Headphones",
        "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life",
        "price": 89.99,
        "category": "Electronics",
        "stock_quantity": 50,
        "image_url": "https://example.com/headphones.jpg",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": product_id_counter + 1,
        "name": "Smart Watch Pro",
        "description": "Feature-rich smartwatch with fitness tracking, heart rate monitor, and GPS",
        "price": 199.99,
        "category": "Electronics",
        "stock_quantity": 30,
        "image_url": "https://example.com/smartwatch.jpg",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": product_id_counter + 2,
        "name": "Leather Backpack",
        "description": "Premium leather backpack with laptop compartment and multiple pockets",
        "price": 79.99,
        "category": "Accessories",
        "stock_quantity": 25,
        "image_url": "https://example.com/backpack.jpg",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": product_id_counter + 3,
        "name": "Yoga Mat Premium",
        "description": "Extra thick non-slip yoga mat with carrying strap",
        "price": 34.99,
        "category": "Sports",
        "stock_quantity": 100,
        "image_url": "https://example.com/yogamat.jpg",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": product_id_counter + 4,
        "name": "Stainless Steel Water Bottle",
        "description": "Insulated water bottle keeps drinks cold for 24 hours, hot for 12 hours",
        "price": 24.99,
        "category": "Sports",
        "stock_quantity": 75,
        "image_url": "https://example.com/bottle.jpg",
        "created_at": datetime.now().isoformat()
    }
])
product_id_counter += 5

reviews_db.extend([
    {
        "id": review_id_counter,
        "product_id": 1,
        "user_id": 2,
        "username": "john_doe",
        "rating": 5,
        "comment": "Amazing sound quality and battery life!",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": review_id_counter + 1,
        "product_id": 2,
        "user_id": 2,
        "username": "john_doe",
        "rating": 4,
        "comment": "Great smartwatch, but a bit pricey",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": review_id_counter + 2,
        "product_id": 3,
        "user_id": 2,
        "username": "john_doe",
        "rating": 5,
        "comment": "Perfect for daily use and travel",
        "created_at": datetime.now().isoformat()
    }
])
review_id_counter += 3


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate):
    global user_id_counter
    
    for user in users_db:
        if user["username"] == user_data.username:
            raise HTTPException(status_code=400, detail="Username already exists")
        if user["email"] == user_data.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = {
        "id": user_id_counter,
        "username": user_data.username,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "role": UserRole.CUSTOMER,
        "address": user_data.address,
        "phone": user_data.phone,
        "created_at": datetime.now().isoformat()
    }
    users_db.append(new_user)
    user_id_counter += 1
    
    return UserResponse(
        id=new_user["id"],
        username=new_user["username"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        role=new_user["role"],
        address=new_user["address"],
        phone=new_user["phone"],
        created_at=new_user["created_at"]
    )


@app.post("/api/auth/login", response_model=LoginResponse)
def login_user(credentials: UserLogin):
    hashed_password = hash_password(credentials.password)
    
    for user in users_db:
        if user["username"] == credentials.username and user["password"] == hashed_password:
            token = generate_token()
            sessions_db[token] = user["id"]
            
            return LoginResponse(
                token=token,
                user=UserResponse(
                    id=user["id"],
                    username=user["username"],
                    email=user["email"],
                    full_name=user["full_name"],
                    role=user["role"],
                    address=user["address"],
                    phone=user["phone"],
                    created_at=user["created_at"]
                )
            )
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/api/products", response_model=List[Product])
def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None
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
    
    result = []
    for p in filtered_products:
        avg_rating, total_reviews = calculate_product_rating(p["id"])
        result.append(Product(
            id=p["id"],
            name=p["name"],
            description=p["description"],
            price=p["price"],
            category=p["category"],
            stock_quantity=p["stock_quantity"],
            image_url=p.get("image_url"),
            created_at=p["created_at"],
            average_rating=avg_rating,
            total_reviews=total_reviews
        ))
    
    return result


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    avg_rating, total_reviews = calculate_product_rating(product_id)
    
    return Product(
        id=product["id"],
        name=product["name"],
        description=product["description"],
        price=product["price"],
        category=product["category"],
        stock_quantity=product["stock_quantity"],
        image_url=product.get("image_url"),
        created_at=product["created_at"],
        average_rating=avg_rating,
        total_reviews=total_reviews
    )


@app.post("/api/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, token: str = Query(...)):
    global product_id_counter
    
    user = get_user_by_token(token)
    if not user or user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    new_product = {
        "id": product_id_counter,
        "name": product_data.name,
        "description": product_data.description,
        "price": product_data.price,
        "category": product_data.category,
        "stock_quantity": product_data.stock_quantity,
        "image_url": product_data.image_url,
        "created_at": datetime.now().isoformat()
    }
    products_db.append(new_product)
    product_id_counter += 1
    
    return Product(
        id=new_product["id"],
        name=new_product["name"],
        description=new_product["description"],
        price=new_product["price"],
        category=new_product["category"],
        stock_quantity=new_product["stock_quantity"],
        image_url=new_product.get("image_url"),
        created_at=new_product["created_at"],
        average_rating=0.0,
        total_reviews=0
    )


@app.put("/api/products/{product_id}", response_model=Product)
def update_product(product_id: int, product_data: ProductUpdate, token: str = Query(...)):
    user = get_user_by_token(token)
    if not user or user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    product = get_product_by_id(product_id)
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
    if product_data.stock_quantity is not None:
        product["stock_quantity"] = product_data.stock_quantity
    if product_data.image_url is not None:
        product["image_url"] = product_data.image_url
    
    avg_rating, total_reviews = calculate_product_rating(product_id)
    
    return Product(
        id=product["id"],
        name=product["name"],
        description=product["description"],
        price=product["price"],
        category=product["category"],
        stock_quantity=product["stock_quantity"],
        image_url=product.get("image_url"),
        created_at=product["created_at"],
        average_rating=avg_rating,
        total_reviews=total_reviews
    )


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, token: str = Query(...)):
    user = get_user_by_token(token)
    if not user or user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    for i, product in enumerate(products_db):
        if product["id"] == product_id:
            products_db.pop(i)
            return
    
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/api/cart", response_model=CartResponse)
def get_cart(token: str = Query(...)):
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    cart_items = carts_db.get(user["id"], [])
    items_response = []
    total = 0.0
    
    for cart_item in cart_items:
        product = get_product_by_id(cart_item["product_id"])
        if product:
            subtotal = product["price"] * cart_item["quantity"]
            items_response.append(CartItemResponse(
                product_id=product["id"],
                product_name=product["name"],
                product_price=product["price"],
                quantity=cart_item["quantity"],
                subtotal=subtotal
            ))
            total += subtotal
    
    return CartResponse(
        user_id=user["id"],
        items=items_response,
        total=round(total, 2)
    )


@app.post("/api/cart", response_model=CartResponse)
def add_to_cart(cart_item: CartItem, token: str = Query(...)):
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    product = get_product_by_id(cart_item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["stock_quantity"] < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    user_cart = carts_db[user["id"]]
    
    found = False
    for item in user_cart:
        if item["product_id"] == cart_item.product_id:
            item["quantity"] += cart_item.quantity
            found = True
            break
    
    if not found:
        user_cart.append({
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity
        })
    
    return get_cart(token=token)


@app.put("/api/cart/{product_id}", response_model=CartResponse)
def update_cart_item(product_id: int, quantity: int = Query(..., ge=0), token: str = Query(...)):
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user_cart = carts_db[user["id"]]
    
    if quantity == 0:
        carts_db[user["id"]] = [item for item in user_cart if item["product_id"] != product_id]
    else:
        product = get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product["stock_quantity"] < quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        
        found = False
        for item in user_cart:
            if item["product_id"] == product_id:
                item["quantity"] = quantity
                found = True
                break
        
        if not found:
            raise HTTPException(status_code=404, detail="Item not in cart")
    
    return get_cart(token=token)


@app.delete("/api/cart", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(token: str = Query(...)):
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    carts_db[user["id"]] = []


@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, token: str = Query(...)):
    global order_id_counter
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user_cart = carts_db.get(user["id"], [])
    if not user_cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    order_items = []
    total_amount = 0.0
    
    for cart_item in user_cart:
        product = get_product_by_id(cart_item["product_id"])
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {cart_item['product_id']} not found")
        
        if product["stock_quantity"] < cart_item["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product['name']}"
            )
        
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
    
    new_order = {
        "id": order_id_counter,
        "user_id": user["id"],
        "items": [item.dict() for item in order_items],
        "total_amount": round(total_amount, 2),
        "status": OrderStatus.PENDING,
        "payment_status": PaymentStatus.PENDING,
        "shipping_address": order_data.shipping_address,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    orders_db.append(new_order)
    order_id_counter += 1
    
    carts_db[user["id"]] = []
    
    return Order(**new_order)


@app.get("/api/orders", response_model=List[Order])
def get_orders(token: str = Query(...)):
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if user["role"] == UserRole.ADMIN:
        return [Order(**order) for order in orders_db]
    else:
        user_orders = [order for order in orders_db if order["user_id"] == user["id"]]
        return [Order(**order) for order in user_orders]


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: int, token: str = Query(...)):
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    for order in orders_db:
        if order["id"] == order_id:
            if user["role"] != UserRole.ADMIN and order["user_id"] != user["id"]:
                raise HTTPException(status_code=403, detail="Access denied")
            return Order(**order)
    
    raise HTTPException(status_code=404, detail="Order not found")


@app.put("/api/orders/{order_id}/status", response_model=Order)
def update_order_status(order_id: int, new_status: OrderStatus, token: str = Query(...)):
    user = get_user_by_token(token)
    if not user or user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    for order in orders_db:
        if order["id"] == order_id:
            order["status"] = new_status
            order["updated_at"] = datetime.now().isoformat()
            return Order(**order)
    
    raise HTTPException(status_code=404, detail="Order not found")


@app.post("/api/payments", response_model=PaymentResponse)
def process_payment(payment_data: PaymentRequest, token: str = Query(...)):
    global payment_id_counter
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    order = None
    for o in orders_db:
        if o["id"] == payment_data.order_id:
            order = o
            break
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if order["payment_status"] == PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Order already paid")
    
    payment_status = PaymentStatus.COMPLETED
    if payment_data.payment_method == "card" and not payment_data.card_number:
        payment_status = PaymentStatus.FAILED
    
    new_payment = {
        "id": payment_id_counter,
        "order_id": order["id"],
        "user_id": user["id"],
        "amount": order["total_amount"],
        "payment_method": payment_data.payment_method,
        "status": payment_status,
        "transaction_date": datetime.now().isoformat()
    }
    payments_db.append(new_payment)
    payment_id_counter += 1
    
    if payment_status == PaymentStatus.COMPLETED:
        order["payment_status"] = PaymentStatus.COMPLETED
        order["status"] = OrderStatus.PROCESSING
        order["updated_at"] = datetime.now().isoformat()
    else:
        order["payment_status"] = PaymentStatus.FAILED
        order["updated_at"] = datetime.now().isoformat()
    
    return PaymentResponse(
        payment_id=new_payment["id"],
        order_id=new_payment["order_id"],
        amount=new_payment["amount"],
        status=new_payment["status"],
        transaction_date=new_payment["transaction_date"]
    )


@app.post("/api/reviews", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(review_data: ReviewCreate, token: str = Query(...)):
    global review_id_counter
    
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    product = get_product_by_id(review_data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if not 1 <= review_data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    user_has_ordered = False
    for order in orders_db:
        if order["user_id"] == user["id"]:
            for item in order["items"]:
                if item["product_id"] == review_data.product_id:
                    user_has_ordered = True
                    break
        if user_has_ordered:
            break
    
    if not user_has_ordered:
        raise HTTPException(status_code=400, detail="You can only review products you have purchased")
    
    for review in reviews_db:
        if review["user_id"] == user["id"] and review["product_id"] == review_data.product_id:
            raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    new_review = {
        "id": review_id_counter,
        "product_id": review_data.product_id,
        "user_id": user["id"],
        "username": user["username"],
        "rating": review_data.rating,
        "comment": review_data.comment,
        "created_at": datetime.now().isoformat()
    }
    reviews_db.append(new_review)
    review_id_counter += 1
    
    return Review(**new_review)


@app.get("/api/reviews/product/{product_id}", response_model=List[Review])
def get_product_reviews(product_id: int):
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_reviews = [review for review in reviews_db if review["product_id"] == product_id]
    return [Review(**review) for review in product_reviews]


@app.get("/api/recommendations", response_model=List[Product])
def get_recommendations(token: str = Query(...), limit: int = Query(5, ge=1, le=20)):
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user_orders = [order for order in orders_db if order["user_id"] == user["id"]]
    
    if not user_orders:
        popular_products = sorted(
            products_db,
            key=lambda p: calculate_product_rating(p["id"])[0],
            reverse=True
        )[:limit]
        
        result = []
        for p in popular_products:
            avg_rating, total_reviews = calculate_product_rating(p["id"])
            result.append(Product(
                id=p["id"],
                name=p["name"],
                description=p["description"],
                price=p["price"],
                category=p["category"],
                stock_quantity=p["stock_quantity"],
                image_url=p.get("image_url"),
                created_at=p["created_at"],
                average_rating=avg_rating,
                total_reviews=total_reviews
            ))
        return result
    
    purchased_categories = set()
    purchased_product_ids = set()
    
    for order in user_orders:
        for item in order["items"]:
            purchased_product_ids.add(item["product_id"])
            product = get_product_by_id(item["product_id"])
            if product:
                purchased_categories.add(product["category"])
    
    recommended_products = []
    for product in products_db:
        if product["id"] not in purchased_product_ids and product["category"] in purchased_categories:
            recommended_products.append(product)
    
    recommended_products.sort(
        key=lambda p: calculate_product_rating(p["id"])[0],
        reverse=True
    )
    
    result = []
    for p in recommended_products[:limit]:
        avg_rating, total_reviews = calculate_product_rating(p["id"])
        result.append(Product(
            id=p["id"],
            name=p["name"],
            description=p["description"],
            price=p["price"],
            category=p["category"],
            stock_quantity=p["stock_quantity"],
            image_url=p.get("image_url"),
            created_at=p["created_at"],
            average_rating=avg_rating,
            total_reviews=total_reviews
        ))
    
    return result


@app.get("/api/categories", response_model=List[str])
def get_categories():
    categories = set()
    for product in products_db:
        categories.add(product["category"])
    return sorted(list(categories))


@app.get("/api/admin/stats")
def get_admin_stats(token: str = Query(...)):
    user = get_user_by_token(token)
    if not user or user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_revenue = sum(order["total_amount"] for order in orders_db if order["payment_status"] == PaymentStatus.COMPLETED)
    total_orders = len(orders_db)
    total_users = len([u for u in users_db if u["role"] == UserRole.CUSTOMER])
    total_products = len(products_db)
    
    orders_by_status = defaultdict(int)
    for order in orders_db:
        orders_by_status[order["status"]] += 1
    
    low_stock_products = [
        {"id": p["id"], "name": p["name"], "stock": p["stock_quantity"]}
        for p in products_db if p["stock_quantity"] < 10
    ]
    
    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "total_users": total_users,
        "total_products": total_products,
        "orders_by_status": dict(orders_by_status),
        "low_stock_products": low_stock_products
    }