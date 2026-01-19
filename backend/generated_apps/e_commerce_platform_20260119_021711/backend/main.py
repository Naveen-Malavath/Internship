from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

app = FastAPI(title="E-Commerce Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"

class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"

class User(BaseModel):
    id: int
    email: str
    name: str
    role: UserRole
    created_at: str
    address: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: UserRole = UserRole.customer
    address: Optional[str] = None
    phone: Optional[str] = None

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: Optional[str] = None
    rating: float = 0.0
    reviews_count: int = 0
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
    product_id: int
    quantity: int
    price: float

class Cart(BaseModel):
    id: int
    user_id: int
    items: List[CartItem]
    total: float
    updated_at: str

class CartItemAdd(BaseModel):
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
    user_id: int
    rating: int
    comment: str

class Order(BaseModel):
    id: int
    user_id: int
    items: List[CartItem]
    total: float
    status: OrderStatus
    payment_status: PaymentStatus
    shipping_address: str
    created_at: str
    updated_at: str

class OrderCreate(BaseModel):
    user_id: int
    shipping_address: str

class Payment(BaseModel):
    id: int
    order_id: int
    amount: float
    status: PaymentStatus
    payment_method: str
    transaction_id: str
    created_at: str

class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str

users_db: List[User] = []
products_db: List[Product] = []
carts_db: List[Cart] = []
reviews_db: List[Review] = []
orders_db: List[Order] = []
payments_db: List[Payment] = []

user_id_counter = 1
product_id_counter = 1
cart_id_counter = 1
review_id_counter = 1
order_id_counter = 1
payment_id_counter = 1

current_time = datetime.now().isoformat()

users_db.extend([
    User(id=1, email="john@example.com", name="John Doe", role=UserRole.customer, created_at=current_time, address="123 Main St, New York, NY", phone="555-0101"),
    User(id=2, email="jane@example.com", name="Jane Smith", role=UserRole.customer, created_at=current_time, address="456 Oak Ave, Los Angeles, CA", phone="555-0102"),
    User(id=3, email="admin@example.com", name="Admin User", role=UserRole.admin, created_at=current_time, address="789 Admin Blvd, San Francisco, CA", phone="555-0103"),
    User(id=4, email="mike@example.com", name="Mike Johnson", role=UserRole.customer, created_at=current_time, address="321 Pine St, Chicago, IL", phone="555-0104"),
    User(id=5, email="sarah@example.com", name="Sarah Williams", role=UserRole.customer, created_at=current_time, address="654 Elm St, Houston, TX", phone="555-0105"),
])
user_id_counter = 6

products_db.extend([
    Product(id=1, name="Wireless Headphones", description="High-quality Bluetooth headphones with noise cancellation", price=129.99, category="Electronics", stock=50, image_url="https://example.com/headphones.jpg", rating=4.5, reviews_count=23, created_at=current_time),
    Product(id=2, name="Smart Watch", description="Fitness tracker with heart rate monitor and GPS", price=249.99, category="Electronics", stock=30, image_url="https://example.com/smartwatch.jpg", rating=4.7, reviews_count=45, created_at=current_time),
    Product(id=3, name="Running Shoes", description="Comfortable athletic shoes for daily running", price=89.99, category="Sports", stock=100, image_url="https://example.com/shoes.jpg", rating=4.3, reviews_count=67, created_at=current_time),
    Product(id=4, name="Laptop Backpack", description="Durable backpack with padded laptop compartment", price=49.99, category="Accessories", stock=75, image_url="https://example.com/backpack.jpg", rating=4.6, reviews_count=34, created_at=current_time),
    Product(id=5, name="Coffee Maker", description="Programmable coffee maker with thermal carafe", price=79.99, category="Home", stock=40, image_url="https://example.com/coffeemaker.jpg", rating=4.4, reviews_count=56, created_at=current_time),
    Product(id=6, name="Yoga Mat", description="Non-slip exercise mat for yoga and fitness", price=29.99, category="Sports", stock=120, image_url="https://example.com/yogamat.jpg", rating=4.8, reviews_count=89, created_at=current_time),
    Product(id=7, name="Wireless Mouse", description="Ergonomic wireless mouse with precision tracking", price=24.99, category="Electronics", stock=150, image_url="https://example.com/mouse.jpg", rating=4.2, reviews_count=112, created_at=current_time),
    Product(id=8, name="Water Bottle", description="Insulated stainless steel water bottle", price=19.99, category="Sports", stock=200, image_url="https://example.com/bottle.jpg", rating=4.7, reviews_count=145, created_at=current_time),
    Product(id=9, name="Desk Lamp", description="LED desk lamp with adjustable brightness", price=39.99, category="Home", stock=60, image_url="https://example.com/lamp.jpg", rating=4.5, reviews_count=78, created_at=current_time),
    Product(id=10, name="Phone Case", description="Protective case for smartphones", price=14.99, category="Accessories", stock=300, image_url="https://example.com/case.jpg", rating=4.1, reviews_count=203, created_at=current_time),
])
product_id_counter = 11

carts_db.extend([
    Cart(id=1, user_id=1, items=[CartItem(product_id=1, quantity=1, price=129.99), CartItem(product_id=3, quantity=2, price=89.99)], total=309.97, updated_at=current_time),
    Cart(id=2, user_id=2, items=[CartItem(product_id=2, quantity=1, price=249.99)], total=249.99, updated_at=current_time),
])
cart_id_counter = 3

reviews_db.extend([
    Review(id=1, product_id=1, user_id=1, rating=5, comment="Excellent sound quality and comfortable to wear!", user_name="John Doe", created_at=current_time),
    Review(id=2, product_id=1, user_id=2, rating=4, comment="Great headphones but a bit pricey", user_name="Jane Smith", created_at=current_time),
    Review(id=3, product_id=2, user_id=1, rating=5, comment="Perfect fitness tracker, very accurate", user_name="John Doe", created_at=current_time),
    Review(id=4, product_id=3, user_id=4, rating=4, comment="Very comfortable for long runs", user_name="Mike Johnson", created_at=current_time),
    Review(id=5, product_id=6, user_id=5, rating=5, comment="Best yoga mat I've ever owned!", user_name="Sarah Williams", created_at=current_time),
])
review_id_counter = 6

orders_db.extend([
    Order(id=1, user_id=1, items=[CartItem(product_id=5, quantity=1, price=79.99)], total=79.99, status=OrderStatus.delivered, payment_status=PaymentStatus.completed, shipping_address="123 Main St, New York, NY", created_at=current_time, updated_at=current_time),
    Order(id=2, user_id=2, items=[CartItem(product_id=6, quantity=2, price=29.99), CartItem(product_id=8, quantity=1, price=19.99)], total=79.97, status=OrderStatus.shipped, payment_status=PaymentStatus.completed, shipping_address="456 Oak Ave, Los Angeles, CA", created_at=current_time, updated_at=current_time),
    Order(id=3, user_id=4, items=[CartItem(product_id=7, quantity=1, price=24.99)], total=24.99, status=OrderStatus.processing, payment_status=PaymentStatus.completed, shipping_address="321 Pine St, Chicago, IL", created_at=current_time, updated_at=current_time),
])
order_id_counter = 4

payments_db.extend([
    Payment(id=1, order_id=1, amount=79.99, status=PaymentStatus.completed, payment_method="credit_card", transaction_id="TXN123456", created_at=current_time),
    Payment(id=2, order_id=2, amount=79.97, status=PaymentStatus.completed, payment_method="paypal", transaction_id="TXN123457", created_at=current_time),
    Payment(id=3, order_id=3, amount=24.99, status=PaymentStatus.completed, payment_method="credit_card", transaction_id="TXN123458", created_at=current_time),
])
payment_id_counter = 4

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "data_counts": {
            "users": len(users_db),
            "products": len(products_db),
            "carts": len(carts_db),
            "reviews": len(reviews_db),
            "orders": len(orders_db),
            "payments": len(payments_db)
        }
    }

@app.get("/api/users", response_model=List[User])
def get_users():
    return users_db

@app.get("/api/users/{user_id}", response_model=User)
def get_user(user_id: int):
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/users", response_model=User, status_code=201)
def create_user(user_data: UserCreate):
    global user_id_counter
    existing_user = next((u for u in users_db if u.email == user_data.email), None)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        id=user_id_counter,
        email=user_data.email,
        name=user_data.name,
        role=user_data.role,
        address=user_data.address,
        phone=user_data.phone,
        created_at=datetime.now().isoformat()
    )
    users_db.append(new_user)
    user_id_counter += 1
    
    new_cart = Cart(
        id=cart_id_counter,
        user_id=new_user.id,
        items=[],
        total=0.0,
        updated_at=datetime.now().isoformat()
    )
    carts_db.append(new_cart)
    
    return new_user

@app.get("/api/products", response_model=List[Product])
def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(None, regex="^(price|rating|name)$")
):
    filtered_products = products_db
    
    if category:
        filtered_products = [p for p in filtered_products if p.category.lower() == category.lower()]
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p.price >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p.price <= max_price]
    
    if search:
        search_lower = search.lower()
        filtered_products = [p for p in filtered_products if search_lower in p.name.lower() or search_lower in p.description.lower()]
    
    if sort_by:
        if sort_by == "price":
            filtered_products = sorted(filtered_products, key=lambda x: x.price)
        elif sort_by == "rating":
            filtered_products = sorted(filtered_products, key=lambda x: x.rating, reverse=True)
        elif sort_by == "name":
            filtered_products = sorted(filtered_products, key=lambda x: x.name)
    
    return filtered_products

@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/api/products", response_model=Product, status_code=201)
def create_product(product_data: ProductCreate):
    global product_id_counter
    new_product = Product(
        id=product_id_counter,
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category,
        stock=product_data.stock,
        image_url=product_data.image_url,
        rating=0.0,
        reviews_count=0,
        created_at=datetime.now().isoformat()
    )
    products_db.append(new_product)
    product_id_counter += 1
    return new_product

@app.put("/api/products/{product_id}", response_model=Product)
def update_product(product_id: int, product_data: ProductUpdate):
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.description is not None:
        product.description = product_data.description
    if product_data.price is not None:
        product.price = product_data.price
    if product_data.category is not None:
        product.category = product_data.category
    if product_data.stock is not None:
        product.stock = product_data.stock
    if product_data.image_url is not None:
        product.image_url = product_data.image_url
    
    return product

@app.delete("/api/products/{product_id}", status_code=204)
def delete_product(product_id: int):
    global products_db
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    products_db = [p for p in products_db if p.id != product_id]
    return None

@app.get("/api/categories", response_model=List[str])
def get_categories():
    categories = list(set(p.category for p in products_db))
    return sorted(categories)

@app.get("/api/carts/{user_id}", response_model=Cart)
def get_cart(user_id: int):
    cart = next((c for c in carts_db if c.user_id == user_id), None)
    if not cart:
        global cart_id_counter
        new_cart = Cart(
            id=cart_id_counter,
            user_id=user_id,
            items=[],
            total=0.0,
            updated_at=datetime.now().isoformat()
        )
        carts_db.append(new_cart)
        cart_id_counter += 1
        return new_cart
    return cart

@app.post("/api/carts/{user_id}/items", response_model=Cart)
def add_to_cart(user_id: int, item_data: CartItemAdd):
    cart = next((c for c in carts_db if c.user_id == user_id), None)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    product = next((p for p in products_db if p.id == item_data.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < item_data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    existing_item = next((item for item in cart.items if item.product_id == item_data.product_id), None)
    if existing_item:
        existing_item.quantity += item_data.quantity
    else:
        new_item = CartItem(
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price=product.price
        )
        cart.items.append(new_item)
    
    cart.total = sum(item.price * item.quantity for item in cart.items)
    cart.updated_at = datetime.now().isoformat()
    
    return cart

@app.put("/api/carts/{user_id}/items/{product_id}", response_model=Cart)
def update_cart_item(user_id: int, product_id: int, quantity: int):
    cart = next((c for c in carts_db if c.user_id == user_id), None)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart_item = next((item for item in cart.items if item.product_id == product_id), None)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if quantity <= 0:
        cart.items = [item for item in cart.items if item.product_id != product_id]
    else:
        if product.stock < quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        cart_item.quantity = quantity
    
    cart.total = sum(item.price * item.quantity for item in cart.items)
    cart.updated_at = datetime.now().isoformat()
    
    return cart

@app.delete("/api/carts/{user_id}/items/{product_id}", response_model=Cart)
def remove_from_cart(user_id: int, product_id: int):
    cart = next((c for c in carts_db if c.user_id == user_id), None)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart.items = [item for item in cart.items if item.product_id != product_id]
    cart.total = sum(item.price * item.quantity for item in cart.items)
    cart.updated_at = datetime.now().isoformat()
    
    return cart

@app.delete("/api/carts/{user_id}", status_code=204)
def clear_cart(user_id: int):
    cart = next((c for c in carts_db if c.user_id == user_id), None)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart.items = []
    cart.total = 0.0
    cart.updated_at = datetime.now().isoformat()
    return None

@app.get("/api/reviews/product/{product_id}", response_model=List[Review])
def get_product_reviews(product_id: int):
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return [r for r in reviews_db if r.product_id == product_id]

@app.post("/api/reviews", response_model=Review, status_code=201)
def create_review(review_data: ReviewCreate):
    global review_id_counter
    
    product = next((p for p in products_db if p.id == review_data.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    user = next((u for u in users_db if u.id == review_data.user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    new_review = Review(
        id=review_id_counter,
        product_id=review_data.product_id,
        user_id=review_data.user_id,
        rating=review_data.rating,
        comment=review_data.comment,
        user_name=user.name,
        created_at=datetime.now().isoformat()
    )
    reviews_db.append(new_review)
    review_id_counter += 1
    
    product_reviews = [r for r in reviews_db if r.product_id == review_data.product_id]
    product.reviews_count = len(product_reviews)
    product.rating = sum(r.rating for r in product_reviews) / len(product_reviews)
    
    return new_review

@app.get("/api/orders", response_model=List[Order])
def get_all_orders():
    return orders_db

@app.get("/api/orders/user/{user_id}", response_model=List[Order])
def get_user_orders(user_id: int):
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return [o for o in orders_db if o.user_id == user_id]

@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    order = next((o for o in orders_db if o.id == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/api/orders", response_model=Order, status_code=201)
def create_order(order_data: OrderCreate):
    global order_id_counter
    
    user = next((u for u in users_db if u.id == order_data.user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    cart = next((c for c in carts_db if c.user_id == order_data.user_id), None)
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    for item in cart.items:
        product = next((p for p in products_db if p.id == item.product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
    
    for item in cart.items:
        product = next((p for p in products_db if p.id == item.product_id), None)
        product.stock -= item.quantity
    
    new_order = Order(
        id=order_id_counter,
        user_id=order_data.user_id,
        items=cart.items.copy(),
        total=cart.total,
        status=OrderStatus.pending,
        payment_status=PaymentStatus.pending,
        shipping_address=order_data.shipping_address,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    orders_db.append(new_order)
    order_id_counter += 1
    
    cart.items = []
    cart.total = 0.0
    cart.updated_at = datetime.now().isoformat()
    
    return new_order

@app.put("/api/orders/{order_id}/status", response_model=Order)
def update_order_status(order_id: int, status: OrderStatus):
    order = next((o for o in orders_db if o.id == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    order.updated_at = datetime.now().isoformat()
    
    return order

@app.post("/api/payments", response_model=Payment, status_code=201)
def create_payment(payment_data: PaymentCreate):
    global payment_id_counter
    
    order = next((o for o in orders_db if o.id == payment_data.order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.payment_status == PaymentStatus.completed:
        raise HTTPException(status_code=400, detail="Order already paid")
    
    new_payment = Payment(
        id=payment_id_counter,
        order_id=payment_data.order_id,
        amount=order.total,
        status=PaymentStatus.completed,
        payment_method=payment_data.payment_method,
        transaction_id=f"TXN{payment_id_counter}{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=datetime.now().isoformat()
    )
    payments_db.append(new_payment)
    payment_id_counter += 1
    
    order.payment_status = PaymentStatus.completed
    order.status = OrderStatus.processing
    order.updated_at = datetime.now().isoformat()
    
    return new_payment

@app.get("/api/payments/order/{order_id}", response_model=Payment)
def get_order_payment(order_id: int):
    payment = next((p for p in payments_db if p.order_id == order_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.get("/api/recommendations/{user_id}", response_model=List[Product])
def get_recommendations(user_id: int, limit: int = 5):
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_orders = [o for o in orders_db if o.user_id == user_id]
    
    if not user_orders:
        return sorted(products_db, key=lambda x: x.rating, reverse=True)[:limit]
    
    purchased_categories = set()
    for order in user_orders:
        for item in order.items:
            product = next((p for p in products_db if p.id == item.product_id), None)
            if product:
                purchased_categories.add(product.category)
    
    recommended = [p for p in products_db if p.category in purchased_categories]
    recommended = sorted(recommended, key=lambda x: x.rating, reverse=True)
    
    if len(recommended) < limit:
        other_products = [p for p in products_db if p.category not in purchased_categories]
        other_products = sorted(other_products, key=lambda x: x.rating, reverse=True)
        recommended.extend(other_products[:limit - len(recommended)])
    
    return recommended[:limit]

@app.get("/api/stats/admin")
def get_admin_stats():
    total_revenue = sum(o.total for o in orders_db if o.payment_status == PaymentStatus.completed)
    total_orders = len(orders_db)
    total_users = len([u for u in users_db if u.role == UserRole.customer])
    total_products = len(products_db)
    
    pending_orders = len([o for o in orders_db if o.status == OrderStatus.pending])
    processing_orders = len([o for o in orders_db if o.status == OrderStatus.processing])
    shipped_orders = len([o for o in orders_db if o.status == OrderStatus.shipped])
    delivered_orders = len([o for o in orders_db if o.status == OrderStatus.delivered])
    
    low_stock_products = [p for p in products_db if p.stock < 20]
    
    top_products = sorted(products_db, key=lambda x: x.reviews_count, reverse=True)[:5]
    
    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "total_users": total_users,
        "total_products": total_products,
        "order_status_breakdown": {
            "pending": pending_orders,
            "processing": processing_orders,
            "shipped": shipped_orders,
            "delivered": delivered_orders
        },
        "low_stock_products": len(low_stock_products),
        "top_products": [{"id": p.id, "name": p.name, "reviews_count": p.reviews_count} for p in top_products]
    }

@app.get("/")
def root():
    return {
        "message": "E-Commerce Platform API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "users": "/api/users",
            "products": "/api/products",
            "carts": "/api/carts/{user_id}",
            "reviews": "/api/reviews",
            "orders": "/api/orders",
            "payments": "/api/payments",
            "recommendations": "/api/recommendations/{user_id}",
            "admin_stats": "/api/stats/admin",
            "docs": "/docs"
        }
    }