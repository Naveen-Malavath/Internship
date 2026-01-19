from fastapi import FastAPI, HTTPException, Query, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import uuid

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
    id: str
    email: str
    password: str
    full_name: str
    role: UserRole
    address: Optional[str] = None
    phone: Optional[str] = None
    created_at: str


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    address: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    address: Optional[str] = None
    phone: Optional[str] = None
    created_at: str


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: Optional[str] = None
    rating: float = 0.0
    review_count: int = 0
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


class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float


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


class PaymentRequest(BaseModel):
    order_id: str
    payment_method: str
    card_number: Optional[str] = None


class Recommendation(BaseModel):
    product_id: str
    product_name: str
    reason: str
    score: float


users_db: List[User] = []
products_db: List[Product] = []
reviews_db: List[Review] = []
carts_db: Dict[str, Cart] = {}
orders_db: List[Order] = []
sessions_db: Dict[str, str] = {}
user_views_db: Dict[str, List[str]] = {}


def init_seed_data():
    seed_users = [
        User(
            id="user1",
            email="admin@shop.com",
            password="admin123",
            full_name="Admin User",
            role=UserRole.admin,
            address="123 Admin St, City",
            phone="+1234567890",
            created_at=datetime.now().isoformat()
        ),
        User(
            id="user2",
            email="john@example.com",
            password="pass123",
            full_name="John Doe",
            role=UserRole.customer,
            address="456 Customer Ave, Town",
            phone="+1987654321",
            created_at=datetime.now().isoformat()
        ),
        User(
            id="user3",
            email="jane@example.com",
            password="pass456",
            full_name="Jane Smith",
            role=UserRole.customer,
            address="789 Buyer Blvd, Village",
            phone="+1122334455",
            created_at=datetime.now().isoformat()
        )
    ]
    users_db.extend(seed_users)
    
    seed_products = [
        Product(
            id="prod1",
            name="Wireless Bluetooth Headphones",
            description="High-quality wireless headphones with noise cancellation and 30-hour battery life",
            price=79.99,
            category="Electronics",
            stock=50,
            image_url="https://example.com/headphones.jpg",
            rating=4.5,
            review_count=128,
            created_at=datetime.now().isoformat()
        ),
        Product(
            id="prod2",
            name="Smart Fitness Watch",
            description="Track your fitness goals with heart rate monitor, GPS, and waterproof design",
            price=149.99,
            category="Electronics",
            stock=30,
            image_url="https://example.com/watch.jpg",
            rating=4.3,
            review_count=89,
            created_at=datetime.now().isoformat()
        ),
        Product(
            id="prod3",
            name="Ergonomic Office Chair",
            description="Comfortable office chair with lumbar support and adjustable height",
            price=299.99,
            category="Furniture",
            stock=20,
            image_url="https://example.com/chair.jpg",
            rating=4.7,
            review_count=245,
            created_at=datetime.now().isoformat()
        ),
        Product(
            id="prod4",
            name="Stainless Steel Water Bottle",
            description="Eco-friendly 32oz insulated water bottle keeps drinks cold for 24 hours",
            price=24.99,
            category="Home & Kitchen",
            stock=100,
            image_url="https://example.com/bottle.jpg",
            rating=4.6,
            review_count=312,
            created_at=datetime.now().isoformat()
        ),
        Product(
            id="prod5",
            name="Yoga Mat Premium",
            description="Non-slip exercise mat with extra cushioning for yoga and fitness",
            price=39.99,
            category="Sports",
            stock=75,
            image_url="https://example.com/yogamat.jpg",
            rating=4.4,
            review_count=156,
            created_at=datetime.now().isoformat()
        )
    ]
    products_db.extend(seed_products)
    
    seed_reviews = [
        Review(
            id="rev1",
            product_id="prod1",
            user_id="user2",
            user_name="John Doe",
            rating=5,
            comment="Amazing sound quality and battery life!",
            created_at=datetime.now().isoformat()
        ),
        Review(
            id="rev2",
            product_id="prod1",
            user_id="user3",
            user_name="Jane Smith",
            rating=4,
            comment="Great headphones but a bit heavy for long use",
            created_at=datetime.now().isoformat()
        ),
        Review(
            id="rev3",
            product_id="prod3",
            user_id="user2",
            user_name="John Doe",
            rating=5,
            comment="Best office chair I've ever owned. My back thanks me!",
            created_at=datetime.now().isoformat()
        )
    ]
    reviews_db.extend(seed_reviews)


init_seed_data()


def verify_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = authorization.replace("Bearer ", "")
    user_id = sessions_db.get(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_id


def verify_admin(authorization: Optional[str] = Header(None)) -> str:
    user_id = verify_token(authorization)
    user = next((u for u in users_db if u.id == user_id), None)
    
    if not user or user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user_id


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "E-Commerce Platform API"
    }


@app.post("/api/auth/register", response_model=UserResponse)
def register_user(user_data: UserCreate):
    if any(u.email == user_data.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=UserRole.customer,
        address=user_data.address,
        phone=user_data.phone,
        created_at=datetime.now().isoformat()
    )
    
    users_db.append(new_user)
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        address=new_user.address,
        phone=new_user.phone,
        created_at=new_user.created_at
    )


@app.post("/api/auth/login")
def login_user(credentials: UserLogin):
    user = next((u for u in users_db if u.email == credentials.email and u.password == credentials.password), None)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = str(uuid.uuid4())
    sessions_db[token] = user.id
    
    return {
        "token": token,
        "user": UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            address=user.address,
            phone=user.phone,
            created_at=user.created_at
        )
    }


@app.get("/api/users/me", response_model=UserResponse)
def get_current_user(user_id: str = Depends(verify_token)):
    user = next((u for u in users_db if u.id == user_id), None)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        address=user.address,
        phone=user.phone,
        created_at=user.created_at
    )


@app.get("/api/products", response_model=List[Product])
def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(None, regex="^(price_asc|price_desc|rating|newest)$")
):
    filtered_products = products_db.copy()
    
    if category:
        filtered_products = [p for p in filtered_products if p.category.lower() == category.lower()]
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p.price >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p.price <= max_price]
    
    if search:
        search_lower = search.lower()
        filtered_products = [
            p for p in filtered_products 
            if search_lower in p.name.lower() or search_lower in p.description.lower()
        ]
    
    if sort_by == "price_asc":
        filtered_products.sort(key=lambda x: x.price)
    elif sort_by == "price_desc":
        filtered_products.sort(key=lambda x: x.price, reverse=True)
    elif sort_by == "rating":
        filtered_products.sort(key=lambda x: x.rating, reverse=True)
    elif sort_by == "newest":
        filtered_products.sort(key=lambda x: x.created_at, reverse=True)
    
    return filtered_products


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str, authorization: Optional[str] = Header(None)):
    product = next((p for p in products_db if p.id == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if authorization:
        try:
            user_id = verify_token(authorization)
            if user_id not in user_views_db:
                user_views_db[user_id] = []
            if product_id not in user_views_db[user_id]:
                user_views_db[user_id].append(product_id)
        except:
            pass
    
    return product


@app.post("/api/products", response_model=Product)
def create_product(product_data: ProductCreate, user_id: str = Depends(verify_admin)):
    product_id = str(uuid.uuid4())
    new_product = Product(
        id=product_id,
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category,
        stock=product_data.stock,
        image_url=product_data.image_url,
        rating=0.0,
        review_count=0,
        created_at=datetime.now().isoformat()
    )
    
    products_db.append(new_product)
    return new_product


@app.put("/api/products/{product_id}", response_model=Product)
def update_product(product_id: str, product_data: ProductUpdate, user_id: str = Depends(verify_admin)):
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
def delete_product(product_id: str, user_id: str = Depends(verify_admin)):
    product_idx = next((i for i, p in enumerate(products_db) if p.id == product_id), None)
    
    if product_idx is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    products_db.pop(product_idx)
    return {"message": "Product deleted successfully"}


@app.get("/api/products/{product_id}/reviews", response_model=List[Review])
def get_product_reviews(product_id: str):
    product = next((p for p in products_db if p.id == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_reviews = [r for r in reviews_db if r.product_id == product_id]
    return product_reviews


@app.post("/api/reviews", response_model=Review)
def create_review(review_data: ReviewCreate, user_id: str = Depends(verify_token)):
    product = next((p for p in products_db if p.id == review_data.product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    user = next((u for u in users_db if u.id == user_id), None)
    
    review_id = str(uuid.uuid4())
    new_review = Review(
        id=review_id,
        product_id=review_data.product_id,
        user_id=user_id,
        user_name=user.full_name if user else "Anonymous",
        rating=review_data.rating,
        comment=review_data.comment,
        created_at=datetime.now().isoformat()
    )
    
    reviews_db.append(new_review)
    
    product_reviews = [r for r in reviews_db if r.product_id == review_data.product_id]
    total_rating = sum(r.rating for r in product_reviews)
    product.rating = round(total_rating / len(product_reviews), 1)
    product.review_count = len(product_reviews)
    
    return new_review


@app.get("/api/cart", response_model=Cart)
def get_cart(user_id: str = Depends(verify_token)):
    if user_id not in carts_db:
        carts_db[user_id] = Cart(
            user_id=user_id,
            items=[],
            updated_at=datetime.now().isoformat()
        )
    
    return carts_db[user_id]


@app.post("/api/cart/items")
def add_to_cart(item_data: CartItemAdd, user_id: str = Depends(verify_token)):
    product = next((p for p in products_db if p.id == item_data.product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < item_data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    if user_id not in carts_db:
        carts_db[user_id] = Cart(
            user_id=user_id,
            items=[],
            updated_at=datetime.now().isoformat()
        )
    
    cart = carts_db[user_id]
    existing_item = next((item for item in cart.items if item.product_id == item_data.product_id), None)
    
    if existing_item:
        existing_item.quantity += item_data.quantity
    else:
        cart.items.append(CartItem(product_id=item_data.product_id, quantity=item_data.quantity))
    
    cart.updated_at = datetime.now().isoformat()
    
    return {"message": "Item added to cart", "cart": cart}


@app.put("/api/cart/items/{product_id}")
def update_cart_item(product_id: str, quantity: int, user_id: str = Depends(verify_token)):
    if user_id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    cart = carts_db[user_id]
    item = next((item for item in cart.items if item.product_id == product_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    product = next((p for p in products_db if p.id == product_id), None)
    
    if product and product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    if quantity <= 0:
        cart.items.remove(item)
    else:
        item.quantity = quantity
    
    cart.updated_at = datetime.now().isoformat()
    
    return {"message": "Cart updated", "cart": cart}


@app.delete("/api/cart/items/{product_id}")
def remove_from_cart(product_id: str, user_id: str = Depends(verify_token)):
    if user_id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    cart = carts_db[user_id]
    item = next((item for item in cart.items if item.product_id == product_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    cart.items.remove(item)
    cart.updated_at = datetime.now().isoformat()
    
    return {"message": "Item removed from cart"}


@app.delete("/api/cart")
def clear_cart(user_id: str = Depends(verify_token)):
    if user_id in carts_db:
        carts_db[user_id].items = []
        carts_db[user_id].updated_at = datetime.now().isoformat()
    
    return {"message": "Cart cleared"}


@app.post("/api/orders", response_model=Order)
def create_order(order_data: OrderCreate, user_id: str = Depends(verify_token)):
    if user_id not in carts_db or not carts_db[user_id].items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart = carts_db[user_id]
    order_items = []
    total_amount = 0.0
    
    for cart_item in cart.items:
        product = next((p for p in products_db if p.id == cart_item.product_id), None)
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {cart_item.product_id} not found")
        
        if product.stock < cart_item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
        
        order_item = OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=cart_item.quantity,
            price=product.price
        )
        order_items.append(order_item)
        total_amount += product.price * cart_item.quantity
        
        product.stock -= cart_item.quantity
    
    order_id = str(uuid.uuid4())
    new_order = Order(
        id=order_id,
        user_id=user_id,
        items=order_items,
        total_amount=round(total_amount, 2),
        status=OrderStatus.pending,
        payment_status=PaymentStatus.pending,
        shipping_address=order_data.shipping_address,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    orders_db.append(new_order)
    carts_db[user_id].items = []
    
    return new_order


@app.get("/api/orders", response_model=List[Order])
def get_orders(user_id: str = Depends(verify_token)):
    user_orders = [o for o in orders_db if o.user_id == user_id]
    return sorted(user_orders, key=lambda x: x.created_at, reverse=True)


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str, user_id: str = Depends(verify_token)):
    order = next((o for o in orders_db if o.id == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    user = next((u for u in users_db if u.id == user_id), None)
    
    if order.user_id != user_id and (not user or user.role != UserRole.admin):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return order


@app.put("/api/orders/{order_id}/status")
def update_order_status(order_id: str, status: OrderStatus, user_id: str = Depends(verify_admin)):
    order = next((o for o in orders_db if o.id == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    order.updated_at = datetime.now().isoformat()
    
    return {"message": "Order status updated", "order": order}


@app.post("/api/payments")
def process_payment(payment_data: PaymentRequest, user_id: str = Depends(verify_token)):
    order = next((o for o in orders_db if o.id == payment_data.order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if order.payment_status == PaymentStatus.completed:
        raise HTTPException(status_code=400, detail="Order already paid")
    
    if not payment_data.payment_method:
        raise HTTPException(status_code=400, detail="Payment method required")
    
    order.payment_status = PaymentStatus.completed
    order.status = OrderStatus.processing
    order.updated_at = datetime.now().isoformat()
    
    return {
        "message": "Payment processed successfully",
        "order_id": order.id,
        "amount": order.total_amount,
        "payment_status": order.payment_status
    }


@app.get("/api/admin/orders", response_model=List[Order])
def get_all_orders(user_id: str = Depends(verify_admin)):
    return sorted(orders_db, key=lambda x: x.created_at, reverse=True)


@app.get("/api/admin/statistics")
def get_statistics(user_id: str = Depends(verify_admin)):
    total_products = len(products_db)
    total_orders = len(orders_db)
    total_users = len([u for u in users_db if u.role == UserRole.customer])
    
    total_revenue = sum(o.total_amount for o in orders_db if o.payment_status == PaymentStatus.completed)
    
    pending_orders = len([o for o in orders_db if o.status == OrderStatus.pending])
    completed_orders = len([o for o in orders_db if o.status == OrderStatus.delivered])
    
    low_stock_products = [p for p in products_db if p.stock < 10]
    
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_revenue": round(total_revenue, 2),
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "low_stock_count": len(low_stock_products),
        "low_stock_products": low_stock_products
    }


@app.get("/api/recommendations", response_model=List[Recommendation])
def get_recommendations(user_id: str = Depends(verify_token), limit: int = 5):
    if user_id not in user_views_db or not user_views_db[user_id]:
        top_rated = sorted(products_db, key=lambda x: x.rating, reverse=True)[:limit]
        return [
            Recommendation(
                product_id=p.id,
                product_name=p.name,
                reason="Top rated product",
                score=p.rating
            )
            for p in top_rated
        ]
    
    viewed_products = [p for p in products_db if p.id in user_views_db[user_id]]
    
    if not viewed_products:
        top_rated = sorted(products_db, key=lambda x: x.rating, reverse=True)[:limit]
        return [
            Recommendation(
                product_id=p.id,
                product_name=p.name,
                reason="Top rated product",
                score=p.rating
            )
            for p in top_rated
        ]
    
    viewed_categories = [p.category for p in viewed_products]
    category_counts = {}
    for cat in viewed_categories:
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    most_viewed_category = max(category_counts, key=category_counts.get)
    
    recommendations = []
    
    same_category = [
        p for p in products_db 
        if p.category == most_viewed_category and p.id not in user_views_db[user_id]
    ]
    same_category_sorted = sorted(same_category, key=lambda x: x.rating, reverse=True)
    
    for p in same_category_sorted[:limit]:
        recommendations.append(
            Recommendation(
                product_id=p.id,
                product_name=p.name,
                reason=f"Similar to products you viewed in {most_viewed_category}",
                score=p.rating
            )
        )
    
    if len(recommendations) < limit:
        remaining = limit - len(recommendations)
        other_products = [
            p for p in products_db 
            if p.id not in user_views_db[user_id] and p.id not in [r.product_id for r in recommendations]
        ]
        other_sorted = sorted(other_products, key=lambda x: x.rating, reverse=True)[:remaining]
        
        for p in other_sorted:
            recommendations.append(
                Recommendation(
                    product_id=p.id,
                    product_name=p.name,
                    reason="Top rated product",
                    score=p.rating
                )
            )
    
    return recommendations[:limit]


@app.get("/api/categories")
def get_categories():
    categories = list(set(p.category for p in products_db))
    category_data = []
    
    for category in categories:
        products_in_category = [p for p in products_db if p.category == category]
        category_data.append({
            "name": category,
            "product_count": len(products_in_category)
        })
    
    return sorted(category_data, key=lambda x: x["product_count"], reverse=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)