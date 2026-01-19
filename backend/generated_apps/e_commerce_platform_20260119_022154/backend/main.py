from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import uuid

app = FastAPI(
    title="E-Commerce Platform",
    description="A modern e-commerce platform with product catalog, shopping cart, and order management",
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


class User(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    created_at: str


class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: Optional[UserRole] = UserRole.CUSTOMER


class UserLogin(BaseModel):
    email: str
    password: str


class Category(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category_id: str
    stock: int
    image_url: Optional[str] = None
    created_at: str
    average_rating: Optional[float] = 0.0
    total_reviews: Optional[int] = 0


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category_id: str
    stock: int
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[str] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None


class CartItem(BaseModel):
    id: str
    user_id: str
    product_id: str
    quantity: int
    added_at: str


class CartItemCreate(BaseModel):
    product_id: str
    quantity: int


class CartItemUpdate(BaseModel):
    quantity: int


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
    status: OrderStatus
    payment_status: PaymentStatus
    shipping_address: str
    created_at: str
    updated_at: str


class OrderCreate(BaseModel):
    shipping_address: str
    payment_method: str


class Payment(BaseModel):
    id: str
    order_id: str
    amount: float
    payment_method: str
    status: PaymentStatus
    transaction_id: Optional[str] = None
    created_at: str


users_db: List[User] = []
categories_db: List[Category] = []
products_db: List[Product] = []
cart_items_db: List[CartItem] = []
reviews_db: List[Review] = []
orders_db: List[Order] = []
payments_db: List[Payment] = []


def seed_data():
    now = datetime.utcnow().isoformat()
    
    users_db.append(User(
        id="user-1",
        email="john@example.com",
        name="John Doe",
        role=UserRole.CUSTOMER,
        created_at=now
    ))
    users_db.append(User(
        id="user-2",
        email="admin@example.com",
        name="Admin User",
        role=UserRole.ADMIN,
        created_at=now
    ))
    users_db.append(User(
        id="user-3",
        email="jane@example.com",
        name="Jane Smith",
        role=UserRole.CUSTOMER,
        created_at=now
    ))
    
    categories_db.append(Category(
        id="cat-1",
        name="Electronics",
        description="Electronic devices and accessories"
    ))
    categories_db.append(Category(
        id="cat-2",
        name="Clothing",
        description="Fashion and apparel"
    ))
    categories_db.append(Category(
        id="cat-3",
        name="Home & Garden",
        description="Home improvement and garden supplies"
    ))
    categories_db.append(Category(
        id="cat-4",
        name="Sports",
        description="Sports equipment and accessories"
    ))
    
    products_db.append(Product(
        id="prod-1",
        name="Wireless Headphones",
        description="Premium noise-cancelling wireless headphones with 30-hour battery life",
        price=199.99,
        category_id="cat-1",
        stock=50,
        image_url="https://example.com/headphones.jpg",
        created_at=now,
        average_rating=4.5,
        total_reviews=12
    ))
    products_db.append(Product(
        id="prod-2",
        name="Smart Watch",
        description="Fitness tracking smartwatch with heart rate monitor",
        price=299.99,
        category_id="cat-1",
        stock=30,
        image_url="https://example.com/smartwatch.jpg",
        created_at=now,
        average_rating=4.8,
        total_reviews=25
    ))
    products_db.append(Product(
        id="prod-3",
        name="Running Shoes",
        description="Lightweight running shoes with superior cushioning",
        price=89.99,
        category_id="cat-4",
        stock=100,
        image_url="https://example.com/shoes.jpg",
        created_at=now,
        average_rating=4.3,
        total_reviews=8
    ))
    products_db.append(Product(
        id="prod-4",
        name="Cotton T-Shirt",
        description="Comfortable 100% cotton t-shirt available in multiple colors",
        price=24.99,
        category_id="cat-2",
        stock=200,
        image_url="https://example.com/tshirt.jpg",
        created_at=now,
        average_rating=4.0,
        total_reviews=15
    ))
    products_db.append(Product(
        id="prod-5",
        name="Yoga Mat",
        description="Non-slip yoga mat with carrying strap",
        price=39.99,
        category_id="cat-4",
        stock=75,
        image_url="https://example.com/yogamat.jpg",
        created_at=now,
        average_rating=4.7,
        total_reviews=20
    ))
    products_db.append(Product(
        id="prod-6",
        name="Laptop Backpack",
        description="Durable laptop backpack with USB charging port",
        price=49.99,
        category_id="cat-1",
        stock=60,
        image_url="https://example.com/backpack.jpg",
        created_at=now,
        average_rating=4.4,
        total_reviews=18
    ))
    products_db.append(Product(
        id="prod-7",
        name="Garden Tool Set",
        description="Complete 10-piece garden tool set with carrying case",
        price=79.99,
        category_id="cat-3",
        stock=40,
        image_url="https://example.com/gardentool.jpg",
        created_at=now,
        average_rating=4.6,
        total_reviews=10
    ))
    products_db.append(Product(
        id="prod-8",
        name="Wireless Mouse",
        description="Ergonomic wireless mouse with precision tracking",
        price=29.99,
        category_id="cat-1",
        stock=150,
        image_url="https://example.com/mouse.jpg",
        created_at=now,
        average_rating=4.2,
        total_reviews=30
    ))
    
    reviews_db.append(Review(
        id="rev-1",
        product_id="prod-1",
        user_id="user-1",
        user_name="John Doe",
        rating=5,
        comment="Excellent sound quality and very comfortable!",
        created_at=now
    ))
    reviews_db.append(Review(
        id="rev-2",
        product_id="prod-1",
        user_id="user-3",
        user_name="Jane Smith",
        rating=4,
        comment="Great headphones but a bit pricey",
        created_at=now
    ))
    reviews_db.append(Review(
        id="rev-3",
        product_id="prod-2",
        user_id="user-1",
        user_name="John Doe",
        rating=5,
        comment="Love the fitness tracking features!",
        created_at=now
    ))
    reviews_db.append(Review(
        id="rev-4",
        product_id="prod-5",
        user_id="user-3",
        user_name="Jane Smith",
        rating=5,
        comment="Perfect for my daily yoga practice",
        created_at=now
    ))


seed_data()


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "users": len(users_db),
            "products": len(products_db),
            "categories": len(categories_db),
            "orders": len(orders_db),
            "reviews": len(reviews_db)
        }
    }


@app.post("/api/users/register", response_model=User, status_code=201)
def register_user(user_data: UserCreate):
    for user in users_db:
        if user.email == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        id=f"user-{uuid.uuid4()}",
        email=user_data.email,
        name=user_data.name,
        role=user_data.role,
        created_at=datetime.utcnow().isoformat()
    )
    users_db.append(new_user)
    return new_user


@app.post("/api/users/login")
def login_user(login_data: UserLogin):
    for user in users_db:
        if user.email == login_data.email:
            return {
                "user": user,
                "token": f"demo-token-{user.id}",
                "message": "Login successful"
            }
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/api/users", response_model=List[User])
def get_users():
    return users_db


@app.get("/api/users/{user_id}", response_model=User)
def get_user(user_id: str):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/api/categories", response_model=List[Category])
def get_categories():
    return categories_db


@app.get("/api/categories/{category_id}", response_model=Category)
def get_category(category_id: str):
    for category in categories_db:
        if category.id == category_id:
            return category
    raise HTTPException(status_code=404, detail="Category not found")


@app.get("/api/products", response_model=List[Product])
def get_products(
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None
):
    filtered_products = products_db
    
    if category_id:
        filtered_products = [p for p in filtered_products if p.category_id == category_id]
    
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
    
    if min_rating is not None:
        filtered_products = [p for p in filtered_products if p.average_rating >= min_rating]
    
    return filtered_products


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    for product in products_db:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/api/products", response_model=Product, status_code=201)
def create_product(product_data: ProductCreate):
    category_exists = any(cat.id == product_data.category_id for cat in categories_db)
    if not category_exists:
        raise HTTPException(status_code=400, detail="Invalid category_id")
    
    new_product = Product(
        id=f"prod-{uuid.uuid4()}",
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category_id=product_data.category_id,
        stock=product_data.stock,
        image_url=product_data.image_url,
        created_at=datetime.utcnow().isoformat(),
        average_rating=0.0,
        total_reviews=0
    )
    products_db.append(new_product)
    return new_product


@app.put("/api/products/{product_id}", response_model=Product)
def update_product(product_id: str, product_data: ProductUpdate):
    for i, product in enumerate(products_db):
        if product.id == product_id:
            update_dict = product_data.dict(exclude_unset=True)
            
            if "category_id" in update_dict:
                category_exists = any(cat.id == update_dict["category_id"] for cat in categories_db)
                if not category_exists:
                    raise HTTPException(status_code=400, detail="Invalid category_id")
            
            updated_product = product.copy(update=update_dict)
            products_db[i] = updated_product
            return updated_product
    raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/api/products/{product_id}")
def delete_product(product_id: str):
    for i, product in enumerate(products_db):
        if product.id == product_id:
            products_db.pop(i)
            return {"message": "Product deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/api/cart/{user_id}", response_model=List[Dict])
def get_cart(user_id: str):
    user_exists = any(u.id == user_id for u in users_db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_cart = [item for item in cart_items_db if item.user_id == user_id]
    
    cart_with_details = []
    for item in user_cart:
        product = next((p for p in products_db if p.id == item.product_id), None)
        if product:
            cart_with_details.append({
                "cart_item_id": item.id,
                "product": product,
                "quantity": item.quantity,
                "subtotal": product.price * item.quantity,
                "added_at": item.added_at
            })
    
    return cart_with_details


@app.post("/api/cart/{user_id}", response_model=CartItem, status_code=201)
def add_to_cart(user_id: str, cart_data: CartItemCreate):
    user_exists = any(u.id == user_id for u in users_db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    product = next((p for p in products_db if p.id == cart_data.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < cart_data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    existing_item = next(
        (item for item in cart_items_db 
         if item.user_id == user_id and item.product_id == cart_data.product_id),
        None
    )
    
    if existing_item:
        new_quantity = existing_item.quantity + cart_data.quantity
        if product.stock < new_quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        existing_item.quantity = new_quantity
        return existing_item
    
    new_cart_item = CartItem(
        id=f"cart-{uuid.uuid4()}",
        user_id=user_id,
        product_id=cart_data.product_id,
        quantity=cart_data.quantity,
        added_at=datetime.utcnow().isoformat()
    )
    cart_items_db.append(new_cart_item)
    return new_cart_item


@app.put("/api/cart/{user_id}/{cart_item_id}", response_model=CartItem)
def update_cart_item(user_id: str, cart_item_id: str, update_data: CartItemUpdate):
    for i, item in enumerate(cart_items_db):
        if item.id == cart_item_id and item.user_id == user_id:
            product = next((p for p in products_db if p.id == item.product_id), None)
            if product and product.stock < update_data.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            
            item.quantity = update_data.quantity
            cart_items_db[i] = item
            return item
    raise HTTPException(status_code=404, detail="Cart item not found")


@app.delete("/api/cart/{user_id}/{cart_item_id}")
def remove_from_cart(user_id: str, cart_item_id: str):
    for i, item in enumerate(cart_items_db):
        if item.id == cart_item_id and item.user_id == user_id:
            cart_items_db.pop(i)
            return {"message": "Item removed from cart"}
    raise HTTPException(status_code=404, detail="Cart item not found")


@app.delete("/api/cart/{user_id}")
def clear_cart(user_id: str):
    global cart_items_db
    cart_items_db = [item for item in cart_items_db if item.user_id != user_id]
    return {"message": "Cart cleared successfully"}


@app.get("/api/reviews/product/{product_id}", response_model=List[Review])
def get_product_reviews(product_id: str):
    product_exists = any(p.id == product_id for p in products_db)
    if not product_exists:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return [review for review in reviews_db if review.product_id == product_id]


@app.post("/api/reviews", response_model=Review, status_code=201)
def create_review(user_id: str, review_data: ReviewCreate):
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    product = next((p for p in products_db if p.id == review_data.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    existing_review = next(
        (r for r in reviews_db 
         if r.product_id == review_data.product_id and r.user_id == user_id),
        None
    )
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    new_review = Review(
        id=f"rev-{uuid.uuid4()}",
        product_id=review_data.product_id,
        user_id=user_id,
        user_name=user.name,
        rating=review_data.rating,
        comment=review_data.comment,
        created_at=datetime.utcnow().isoformat()
    )
    reviews_db.append(new_review)
    
    product_reviews = [r for r in reviews_db if r.product_id == review_data.product_id]
    total_rating = sum(r.rating for r in product_reviews)
    avg_rating = total_rating / len(product_reviews)
    
    for i, p in enumerate(products_db):
        if p.id == review_data.product_id:
            p.average_rating = round(avg_rating, 2)
            p.total_reviews = len(product_reviews)
            products_db[i] = p
            break
    
    return new_review


class SimpleOrderCreate(BaseModel):
    """Simple order creation model for demo apps"""
    userId: Optional[str] = "user-1"  # Default user for demo
    items: List[dict]
    total: float
    status: Optional[str] = "pending"
    shipping_address: Optional[str] = "123 Demo Street"


@app.post("/api/orders", response_model=Order, status_code=201)
def create_order_simple(order_data: SimpleOrderCreate):
    """Create order without user_id in path (for demo apps)"""
    now = datetime.utcnow().isoformat()
    
    # Convert items to OrderItem format
    order_items = []
    for item in order_data.items:
        order_items.append(OrderItem(
            product_id=str(item.get("id", "")),
            product_name=item.get("name", "Unknown Product"),
            quantity=item.get("quantity", 1),
            price=item.get("price", 0),
            subtotal=item.get("price", 0) * item.get("quantity", 1)
        ))
    
    new_order = Order(
        id=f"order-{uuid.uuid4()}",
        user_id=order_data.userId,
        items=order_items,
        total_amount=order_data.total,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        shipping_address=order_data.shipping_address,
        created_at=now,
        updated_at=now
    )
    orders_db.append(new_order)
    return new_order


@app.post("/api/orders/user/{user_id}", response_model=Order, status_code=201)
def create_order_for_user(user_id: str, order_data: OrderCreate):
    """Create order with user_id in path (original pattern)"""
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_cart = [item for item in cart_items_db if item.user_id == user_id]
    if not user_cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    order_items = []
    total_amount = 0.0
    
    for cart_item in user_cart:
        product = next((p for p in products_db if p.id == cart_item.product_id), None)
        if not product:
            continue
        
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock for product: {product.name}"
            )
        
        subtotal = product.price * cart_item.quantity
        order_items.append(OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=cart_item.quantity,
            price=product.price,
            subtotal=subtotal
        ))
        total_amount += subtotal
        
        for i, p in enumerate(products_db):
            if p.id == product.id:
                p.stock -= cart_item.quantity
                products_db[i] = p
                break
    
    now = datetime.utcnow().isoformat()
    new_order = Order(
        id=f"order-{uuid.uuid4()}",
        user_id=user_id,
        items=order_items,
        total_amount=round(total_amount, 2),
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        shipping_address=order_data.shipping_address,
        created_at=now,
        updated_at=now
    )
    orders_db.append(new_order)
    
    payment = Payment(
        id=f"payment-{uuid.uuid4()}",
        order_id=new_order.id,
        amount=new_order.total_amount,
        payment_method=order_data.payment_method,
        status=PaymentStatus.COMPLETED,
        transaction_id=f"txn-{uuid.uuid4()}",
        created_at=now
    )
    payments_db.append(payment)
    
    new_order.payment_status = PaymentStatus.COMPLETED
    new_order.status = OrderStatus.PROCESSING
    
    global cart_items_db
    cart_items_db = [item for item in cart_items_db if item.user_id != user_id]
    
    return new_order


@app.get("/api/orders", response_model=List[Order])
def get_all_orders():
    """Get all orders (for demo apps without authentication)"""
    return orders_db


@app.get("/api/orders/user/{user_id}", response_model=List[Order])
def get_user_orders(user_id: str):
    """Get orders for a specific user"""
    user_exists = any(u.id == user_id for u in users_db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    return [order for order in orders_db if order.user_id == user_id]


@app.get("/api/orders/detail/{order_id}", response_model=Order)
def get_order_detail(order_id: str):
    for order in orders_db:
        if order.id == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")


@app.put("/api/orders/{order_id}/status")
def update_order_status(order_id: str, status: OrderStatus):
    for i, order in enumerate(orders_db):
        if order.id == order_id:
            order.status = status
            order.updated_at = datetime.utcnow().isoformat()
            orders_db[i] = order
            return {"message": "Order status updated", "order": order}
    raise HTTPException(status_code=404, detail="Order not found")


@app.get("/api/admin/orders", response_model=List[Order])
def get_all_orders():
    return orders_db


@app.get("/api/admin/statistics")
def get_statistics():
    total_revenue = sum(order.total_amount for order in orders_db)
    completed_orders = [o for o in orders_db if o.status == OrderStatus.DELIVERED]
    
    product_sales = {}
    for order in orders_db:
        for item in order.items:
            if item.product_id not in product_sales:
                product_sales[item.product_id] = {
                    "product_name": item.product_name,
                    "quantity_sold": 0,
                    "revenue": 0.0
                }
            product_sales[item.product_id]["quantity_sold"] += item.quantity
            product_sales[item.product_id]["revenue"] += item.subtotal
    
    return {
        "total_users": len(users_db),
        "total_products": len(products_db),
        "total_orders": len(orders_db),
        "total_revenue": round(total_revenue, 2),
        "completed_orders": len(completed_orders),
        "average_order_value": round(total_revenue / len(orders_db), 2) if orders_db else 0,
        "total_reviews": len(reviews_db),
        "product_sales": list(product_sales.values())[:5]
    }


@app.get("/api/recommendations/{user_id}", response_model=List[Product])
def get_recommendations(user_id: str):
    user_exists = any(u.id == user_id for u in users_db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_orders = [order for order in orders_db if order.user_id == user_id]
    
    if not user_orders:
        top_rated = sorted(products_db, key=lambda p: p.average_rating, reverse=True)[:5]
        return top_rated
    
    purchased_categories = set()
    for order in user_orders:
        for item in order.items:
            product = next((p for p in products_db if p.id == item.product_id), None)
            if product:
                purchased_categories.add(product.category_id)
    
    recommendations = [
        p for p in products_db 
        if p.category_id in purchased_categories and p.stock > 0
    ]
    
    recommendations_sorted = sorted(
        recommendations, 
        key=lambda p: (p.average_rating, p.total_reviews), 
        reverse=True
    )[:5]
    
    if len(recommendations_sorted) < 5:
        additional = [p for p in products_db if p not in recommendations_sorted and p.stock > 0]
        additional_sorted = sorted(
            additional, 
            key=lambda p: p.average_rating, 
            reverse=True
        )
        recommendations_sorted.extend(additional_sorted[:5 - len(recommendations_sorted)])
    
    return recommendations_sorted


@app.get("/api/search")
def search(q: str = Query(..., min_length=1)):
    results = {
        "products": [],
        "categories": []
    }
    
    query_lower = q.lower()
    
    for product in products_db:
        if query_lower in product.name.lower() or query_lower in product.description.lower():
            results["products"].append(product)
    
    for category in categories_db:
        if query_lower in category.name.lower():
            results["categories"].append(category)
    
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)