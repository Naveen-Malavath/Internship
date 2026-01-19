from fastapi import FastAPI, HTTPException, Depends, Header
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

class User(BaseModel):
    id: str
    email: str
    name: str
    password_hash: str
    is_admin: bool = False
    created_at: str

class UserRegister(BaseModel):
    email: str
    name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    is_admin: bool
    created_at: str

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: str
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

class CartItemAdd(BaseModel):
    product_id: str
    quantity: int

class Review(BaseModel):
    id: str
    product_id: str
    user_id: str
    rating: int
    comment: str
    created_at: str

class ReviewCreate(BaseModel):
    product_id: str
    rating: int
    comment: str

class ReviewResponse(BaseModel):
    id: str
    product_id: str
    user_id: str
    user_name: str
    rating: int
    comment: str
    created_at: str

class Order(BaseModel):
    id: str
    user_id: str
    items: List[CartItem]
    total_amount: float
    status: str
    payment_method: str
    shipping_address: str
    created_at: str
    updated_at: str

class OrderCreate(BaseModel):
    payment_method: str
    shipping_address: str

class OrderResponse(BaseModel):
    id: str
    user_id: str
    items: List[Dict]
    total_amount: float
    status: str
    payment_method: str
    shipping_address: str
    created_at: str
    updated_at: str

users_db: List[User] = []
products_db: List[Product] = []
carts_db: Dict[str, Cart] = {}
reviews_db: List[Review] = []
orders_db: List[Order] = []
sessions_db: Dict[str, str] = {}
user_views_db: Dict[str, List[str]] = defaultdict(list)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user_id = sessions_db.get(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

admin_user = User(
    id="admin-001",
    email="admin@ecommerce.com",
    name="Admin User",
    password_hash=hash_password("admin123"),
    is_admin=True,
    created_at=datetime.now().isoformat()
)
users_db.append(admin_user)

products_db.extend([
    Product(
        id="prod-001",
        name="Wireless Headphones",
        description="High-quality wireless headphones with noise cancellation",
        price=199.99,
        category="Electronics",
        stock=50,
        image_url="https://example.com/headphones.jpg",
        created_at=datetime.now().isoformat()
    ),
    Product(
        id="prod-002",
        name="Smart Watch",
        description="Fitness tracking smart watch with heart rate monitor",
        price=299.99,
        category="Electronics",
        stock=30,
        image_url="https://example.com/smartwatch.jpg",
        created_at=datetime.now().isoformat()
    ),
    Product(
        id="prod-003",
        name="Running Shoes",
        description="Comfortable running shoes for daily exercise",
        price=89.99,
        category="Sports",
        stock=100,
        image_url="https://example.com/shoes.jpg",
        created_at=datetime.now().isoformat()
    ),
    Product(
        id="prod-004",
        name="Yoga Mat",
        description="Non-slip yoga mat for home workouts",
        price=29.99,
        category="Sports",
        stock=75,
        image_url="https://example.com/yogamat.jpg",
        created_at=datetime.now().isoformat()
    ),
    Product(
        id="prod-005",
        name="Coffee Maker",
        description="Programmable coffee maker with 12-cup capacity",
        price=79.99,
        category="Home",
        stock=40,
        image_url="https://example.com/coffee.jpg",
        created_at=datetime.now().isoformat()
    )
])

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "users": len(users_db),
        "products": len(products_db),
        "orders": len(orders_db)
    }

@app.post("/api/auth/register", response_model=UserResponse)
def register_user(user_data: UserRegister):
    if any(u.email == user_data.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        id=f"user-{uuid.uuid4().hex[:8]}",
        email=user_data.email,
        name=user_data.name,
        password_hash=hash_password(user_data.password),
        is_admin=False,
        created_at=datetime.now().isoformat()
    )
    users_db.append(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        is_admin=user.is_admin,
        created_at=user.created_at
    )

@app.post("/api/auth/login")
def login_user(credentials: UserLogin):
    user = next((u for u in users_db if u.email == credentials.email), None)
    
    if not user or user.password_hash != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = uuid.uuid4().hex
    sessions_db[token] = user.id
    
    return {
        "token": token,
        "user": UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            is_admin=user.is_admin,
            created_at=user.created_at
        )
    }

@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at
    )

@app.post("/api/auth/logout")
def logout_user(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "")
        if token in sessions_db:
            del sessions_db[token]
    return {"message": "Logged out successfully"}

@app.get("/api/products", response_model=List[Product])
def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    filtered_products = products_db
    
    if category:
        filtered_products = [p for p in filtered_products if p.category.lower() == category.lower()]
    
    if search:
        search_lower = search.lower()
        filtered_products = [
            p for p in filtered_products 
            if search_lower in p.name.lower() or search_lower in p.description.lower()
        ]
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p.price >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p.price <= max_price]
    
    return filtered_products

@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str, authorization: Optional[str] = Header(None)):
    product = next((p for p in products_db if p.id == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if authorization:
        token = authorization.replace("Bearer ", "")
        user_id = sessions_db.get(token)
        if user_id:
            user_views_db[user_id].append(product_id)
    
    return product

@app.post("/api/products", response_model=Product)
def create_product(product_data: ProductCreate, admin: User = Depends(get_admin_user)):
    product = Product(
        id=f"prod-{uuid.uuid4().hex[:8]}",
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category,
        stock=product_data.stock,
        image_url=product_data.image_url,
        created_at=datetime.now().isoformat()
    )
    products_db.append(product)
    return product

@app.put("/api/products/{product_id}", response_model=Product)
def update_product(product_id: str, product_data: ProductUpdate, admin: User = Depends(get_admin_user)):
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

@app.delete("/api/products/{product_id}")
def delete_product(product_id: str, admin: User = Depends(get_admin_user)):
    product = next((p for p in products_db if p.id == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    products_db.remove(product)
    return {"message": "Product deleted successfully"}

@app.get("/api/cart", response_model=Cart)
def get_cart(current_user: User = Depends(get_current_user)):
    if current_user.id not in carts_db:
        carts_db[current_user.id] = Cart(
            user_id=current_user.id,
            items=[],
            updated_at=datetime.now().isoformat()
        )
    return carts_db[current_user.id]

@app.post("/api/cart/items")
def add_to_cart(cart_item: CartItemAdd, current_user: User = Depends(get_current_user)):
    product = next((p for p in products_db if p.id == cart_item.product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    if current_user.id not in carts_db:
        carts_db[current_user.id] = Cart(
            user_id=current_user.id,
            items=[],
            updated_at=datetime.now().isoformat()
        )
    
    cart = carts_db[current_user.id]
    existing_item = next((item for item in cart.items if item.product_id == cart_item.product_id), None)
    
    if existing_item:
        existing_item.quantity += cart_item.quantity
    else:
        cart.items.append(CartItem(product_id=cart_item.product_id, quantity=cart_item.quantity))
    
    cart.updated_at = datetime.now().isoformat()
    
    return {"message": "Item added to cart", "cart": cart}

@app.put("/api/cart/items/{product_id}")
def update_cart_item(product_id: str, quantity: int, current_user: User = Depends(get_current_user)):
    if current_user.id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart = carts_db[current_user.id]
    item = next((item for item in cart.items if item.product_id == product_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    product = next((p for p in products_db if p.id == product_id), None)
    
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    item.quantity = quantity
    cart.updated_at = datetime.now().isoformat()
    
    return {"message": "Cart updated", "cart": cart}

@app.delete("/api/cart/items/{product_id}")
def remove_from_cart(product_id: str, current_user: User = Depends(get_current_user)):
    if current_user.id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart = carts_db[current_user.id]
    cart.items = [item for item in cart.items if item.product_id != product_id]
    cart.updated_at = datetime.now().isoformat()
    
    return {"message": "Item removed from cart", "cart": cart}

@app.delete("/api/cart")
def clear_cart(current_user: User = Depends(get_current_user)):
    if current_user.id in carts_db:
        carts_db[current_user.id].items = []
        carts_db[current_user.id].updated_at = datetime.now().isoformat()
    
    return {"message": "Cart cleared"}

@app.post("/api/orders", response_model=OrderResponse)
def create_order(order_data: OrderCreate, current_user: User = Depends(get_current_user)):
    if current_user.id not in carts_db or not carts_db[current_user.id].items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart = carts_db[current_user.id]
    total_amount = 0.0
    order_items = []
    
    for cart_item in cart.items:
        product = next((p for p in products_db if p.id == cart_item.product_id), None)
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {cart_item.product_id} not found")
        
        if product.stock < cart_item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
        
        product.stock -= cart_item.quantity
        total_amount += product.price * cart_item.quantity
        order_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": cart_item.quantity,
            "price": product.price,
            "subtotal": product.price * cart_item.quantity
        })
    
    order = Order(
        id=f"order-{uuid.uuid4().hex[:8]}",
        user_id=current_user.id,
        items=cart.items,
        total_amount=total_amount,
        status="pending",
        payment_method=order_data.payment_method,
        shipping_address=order_data.shipping_address,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    orders_db.append(order)
    
    carts_db[current_user.id].items = []
    carts_db[current_user.id].updated_at = datetime.now().isoformat()
    
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        items=order_items,
        total_amount=order.total_amount,
        status=order.status,
        payment_method=order.payment_method,
        shipping_address=order.shipping_address,
        created_at=order.created_at,
        updated_at=order.updated_at
    )

@app.get("/api/orders", response_model=List[OrderResponse])
def get_orders(current_user: User = Depends(get_current_user)):
    user_orders = [o for o in orders_db if o.user_id == current_user.id]
    
    response_orders = []
    for order in user_orders:
        order_items = []
        for cart_item in order.items:
            product = next((p for p in products_db if p.id == cart_item.product_id), None)
            if product:
                order_items.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "quantity": cart_item.quantity,
                    "price": product.price,
                    "subtotal": product.price * cart_item.quantity
                })
        
        response_orders.append(OrderResponse(
            id=order.id,
            user_id=order.user_id,
            items=order_items,
            total_amount=order.total_amount,
            status=order.status,
            payment_method=order.payment_method,
            shipping_address=order.shipping_address,
            created_at=order.created_at,
            updated_at=order.updated_at
        ))
    
    return response_orders

@app.get("/api/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, current_user: User = Depends(get_current_user)):
    order = next((o for o in orders_db if o.id == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    order_items = []
    for cart_item in order.items:
        product = next((p for p in products_db if p.id == cart_item.product_id), None)
        if product:
            order_items.append({
                "product_id": product.id,
                "product_name": product.name,
                "quantity": cart_item.quantity,
                "price": product.price,
                "subtotal": product.price * cart_item.quantity
            })
    
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        items=order_items,
        total_amount=order.total_amount,
        status=order.status,
        payment_method=order.payment_method,
        shipping_address=order.shipping_address,
        created_at=order.created_at,
        updated_at=order.updated_at
    )

@app.put("/api/orders/{order_id}/status")
def update_order_status(order_id: str, status: str, admin: User = Depends(get_admin_user)):
    valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
    
    order = next((o for o in orders_db if o.id == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    order.updated_at = datetime.now().isoformat()
    
    return {"message": "Order status updated", "order_id": order_id, "status": status}

@app.post("/api/reviews", response_model=ReviewResponse)
def create_review(review_data: ReviewCreate, current_user: User = Depends(get_current_user)):
    product = next((p for p in products_db if p.id == review_data.product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    existing_review = next(
        (r for r in reviews_db if r.product_id == review_data.product_id and r.user_id == current_user.id),
        None
    )
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    review = Review(
        id=f"review-{uuid.uuid4().hex[:8]}",
        product_id=review_data.product_id,
        user_id=current_user.id,
        rating=review_data.rating,
        comment=review_data.comment,
        created_at=datetime.now().isoformat()
    )
    reviews_db.append(review)
    
    return ReviewResponse(
        id=review.id,
        product_id=review.product_id,
        user_id=review.user_id,
        user_name=current_user.name,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at
    )

@app.get("/api/products/{product_id}/reviews", response_model=List[ReviewResponse])
def get_product_reviews(product_id: str):
    product = next((p for p in products_db if p.id == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_reviews = [r for r in reviews_db if r.product_id == product_id]
    
    response_reviews = []
    for review in product_reviews:
        user = next((u for u in users_db if u.id == review.user_id), None)
        response_reviews.append(ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            user_name=user.name if user else "Unknown User",
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at
        ))
    
    return response_reviews

@app.get("/api/recommendations", response_model=List[Product])
def get_recommendations(current_user: User = Depends(get_current_user)):
    if current_user.id not in user_views_db or not user_views_db[current_user.id]:
        return products_db[:5]
    
    viewed_product_ids = user_views_db[current_user.id]
    viewed_products = [p for p in products_db if p.id in viewed_product_ids]
    
    if not viewed_products:
        return products_db[:5]
    
    categories = list(set(p.category for p in viewed_products))
    
    recommended_products = [
        p for p in products_db 
        if p.category in categories and p.id not in viewed_product_ids
    ]
    
    if len(recommended_products) < 5:
        other_products = [p for p in products_db if p.id not in viewed_product_ids and p not in recommended_products]
        recommended_products.extend(other_products[:5 - len(recommended_products)])
    
    return recommended_products[:5]

@app.get("/api/admin/dashboard")
def get_admin_dashboard(admin: User = Depends(get_admin_user)):
    total_revenue = sum(order.total_amount for order in orders_db)
    
    category_sales = defaultdict(float)
    for order in orders_db:
        for item in order.items:
            product = next((p for p in products_db if p.id == item.product_id), None)
            if product:
                category_sales[product.category] += product.price * item.quantity
    
    low_stock_products = [p for p in products_db if p.stock < 10]
    
    recent_orders = sorted(orders_db, key=lambda x: x.created_at, reverse=True)[:10]
    
    return {
        "total_users": len(users_db),
        "total_products": len(products_db),
        "total_orders": len(orders_db),
        "total_revenue": total_revenue,
        "category_sales": dict(category_sales),
        "low_stock_products": [
            {"id": p.id, "name": p.name, "stock": p.stock}
            for p in low_stock_products
        ],
        "recent_orders": [
            {"id": o.id, "user_id": o.user_id, "total": o.total_amount, "status": o.status}
            for o in recent_orders
        ]
    }

@app.get("/api/admin/orders", response_model=List[OrderResponse])
def get_all_orders(admin: User = Depends(get_admin_user)):
    response_orders = []
    for order in orders_db:
        order_items = []
        for cart_item in order.items:
            product = next((p for p in products_db if p.id == cart_item.product_id), None)
            if product:
                order_items.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "quantity": cart_item.quantity,
                    "price": product.price,
                    "subtotal": product.price * cart_item.quantity
                })
        
        response_orders.append(OrderResponse(
            id=order.id,
            user_id=order.user_id,
            items=order_items,
            total_amount=order.total_amount,
            status=order.status,
            payment_method=order.payment_method,
            shipping_address=order.shipping_address,
            created_at=order.created_at,
            updated_at=order.updated_at
        ))
    
    return response_orders

@app.get("/api/categories")
def get_categories():
    categories = list(set(p.category for p in products_db))
    category_counts = {cat: len([p for p in products_db if p.category == cat]) for cat in categories}
    
    return {
        "categories": [
            {"name": cat, "count": count}
            for cat, count in category_counts.items()
        ]
    }