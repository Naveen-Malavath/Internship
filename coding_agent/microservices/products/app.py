from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Products Service",
    description="Microservice for managing product catalog",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: Optional[str] = None
    created_at: datetime
    is_available: bool = True

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
    is_available: Optional[bool] = None

# In-memory database (replace with real database in production)
products_db = [
    {
        "id": 1,
        "name": "Laptop Pro 15",
        "description": "High-performance laptop with 15-inch display",
        "price": 999.99,
        "category": "Electronics",
        "stock": 50,
        "image_url": "https://example.com/laptop.jpg",
        "created_at": datetime.now(),
        "is_available": True
    },
    {
        "id": 2,
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse with precision tracking",
        "price": 29.99,
        "category": "Accessories",
        "stock": 200,
        "image_url": "https://example.com/mouse.jpg",
        "created_at": datetime.now(),
        "is_available": True
    },
    {
        "id": 3,
        "name": "Mechanical Keyboard",
        "description": "RGB mechanical keyboard with blue switches",
        "price": 79.99,
        "category": "Accessories",
        "stock": 100,
        "image_url": "https://example.com/keyboard.jpg",
        "created_at": datetime.now(),
        "is_available": True
    }
]

# Routes
@app.get("/")
async def root():
    return {
        "service": "Products Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/products", response_model=List[Product])
async def get_products(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    available_only: bool = True
):
    """Get all products with pagination and filtering"""
    filtered_products = products_db
    
    # Filter by category if provided
    if category:
        filtered_products = [p for p in filtered_products if p["category"] == category]
    
    # Filter by availability
    if available_only:
        filtered_products = [p for p in filtered_products if p["is_available"]]
    
    return filtered_products[skip:skip + limit]

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get a specific product by ID"""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products", response_model=Product, status_code=201)
async def create_product(product: ProductCreate):
    """Create a new product"""
    # Check if product name already exists
    if any(p["name"].lower() == product.name.lower() for p in products_db):
        raise HTTPException(status_code=400, detail="Product name already exists")
    
    new_product = {
        "id": max([p["id"] for p in products_db]) + 1 if products_db else 1,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category": product.category,
        "stock": product.stock,
        "image_url": product.image_url,
        "created_at": datetime.now(),
        "is_available": True
    }
    
    products_db.append(new_product)
    return new_product

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, product: ProductUpdate):
    """Update an existing product"""
    existing_product = next((p for p in products_db if p["id"] == product_id), None)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update only provided fields
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        existing_product[key] = value
    
    return existing_product

@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int):
    """Delete a product (soft delete by setting is_available to False)"""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product["is_available"] = False
    return None

@app.patch("/products/{product_id}/stock")
async def update_stock(product_id: int, quantity: int):
    """Update product stock quantity"""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product["stock"] += quantity
    if product["stock"] < 0:
        product["stock"] = 0
    
    return {
        "product_id": product_id,
        "new_stock": product["stock"]
    }

@app.get("/categories")
async def get_categories():
    """Get all unique product categories"""
    categories = list(set(p["category"] for p in products_db))
    return {"categories": sorted(categories)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
