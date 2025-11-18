# 🚀 AI Agents E-commerce Platform
## Angular + JavaScript Frontend | FastAPI Backend

---

## 🎯 PROJECT ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Angular)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  UI Layer    │  │  AI Chatbot  │  │  Components  │     │
│  │  (Material)  │  │  (LangChain) │  │  (E-comm)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          State Management (NgRx)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          HTTP Client (connects to FastAPI)           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Python)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  AI Agents   │  │  E-commerce  │  │  Auth & APIs │     │
│  │  (LangChain) │  │  Logic       │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Database (PostgreSQL/MongoDB)               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 COMPLETE LIBRARY STACK

### 🎨 FRONTEND (Angular + JavaScript)

#### 1. Core Angular Setup
```bash
# Already installed in your project
# Angular 17 with standalone components
```

#### 2. UI Component Library

**Option A: Angular Material (Recommended)**
```bash
ng add @angular/material
npm install @angular/cdk
```
**Features:**
- 50+ production-ready components
- Product cards, data tables, dialogs
- Shopping cart UI components
- Form controls for checkout

**Option B: PrimeNG (Best for E-commerce)**
```bash
npm install primeng primeicons
```
**Components:**
- DataTable with filters/sorting
- Carousel for products
- Mega menu
- Shopping cart components
- Rating stars
- File upload

**Option C: Both (Use Material as base + PrimeNG for specific components)**
```bash
ng add @angular/material
npm install primeng primeicons
```

#### 3. State Management

**NgRx (Recommended for Enterprise E-commerce)**
```bash
npm install @ngrx/store @ngrx/effects @ngrx/entity @ngrx/store-devtools @ngrx/router-store
```
**Use Cases:**
- Shopping cart state
- User authentication state
- Product catalog state
- Order management
- AI chat history

**Configuration Example:**
```typescript
// store/cart/cart.state.ts
export interface CartState {
  items: CartItem[];
  total: number;
  loading: boolean;
}

// store/cart/cart.actions.ts
export const addToCart = createAction('[Cart] Add Item', props<{ product: Product }>());
export const removeFromCart = createAction('[Cart] Remove Item', props<{ productId: string }>());
```

#### 4. HTTP Client & API Integration

**Built-in HttpClient + Interceptors**
```typescript
// services/api.service.ts
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private apiUrl = 'http://localhost:8000/api';  // FastAPI backend

  constructor(private http: HttpClient) {}

  // Products
  getProducts(): Observable<Product[]> {
    return this.http.get<Product[]>(`${this.apiUrl}/products`);
  }

  // AI Agent Chat
  sendChatMessage(message: string): Observable<{ response: string }> {
    return this.http.post<{ response: string }>(
      `${this.apiUrl}/ai/chat`,
      { message }
    );
  }

  // Orders
  createOrder(order: Order): Observable<Order> {
    return this.http.post<Order>(`${this.apiUrl}/orders`, order);
  }
}
```

**Advanced: Axios (Alternative)**
```bash
npm install axios
```

#### 5. Real-time Communication with FastAPI

**Socket.io Client**
```bash
npm install socket.io-client @types/socket.io-client
```

**Usage Example:**
```typescript
// services/websocket.service.ts
import { Injectable } from '@angular/core';
import { io, Socket } from 'socket.io-client';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private socket: Socket;

  constructor() {
    this.socket = io('http://localhost:8000');  // FastAPI WebSocket
  }

  // Listen to AI agent responses
  onAIResponse(): Observable<any> {
    return new Observable(observer => {
      this.socket.on('ai_response', (data) => {
        observer.next(data);
      });
    });
  }

  // Send message to AI agent
  sendMessage(message: string) {
    this.socket.emit('user_message', { message });
  }

  // Listen to inventory updates
  onInventoryUpdate(): Observable<any> {
    return new Observable(observer => {
      this.socket.on('inventory_update', (data) => {
        observer.next(data);
      });
    });
  }
}
```

#### 6. AI Chatbot UI

**Angular CDK for Chat Interface**
```bash
npm install @angular/cdk
```

**NGX Markdown (For AI responses with formatting)**
```bash
npm install ngx-markdown marked highlight.js
```

**Configuration:**
```typescript
// app.config.ts
import { provideMarkdown } from 'ngx-markdown';

export const appConfig: ApplicationConfig = {
  providers: [
    provideMarkdown(),
    // ... other providers
  ]
};
```

**Usage:**
```html
<!-- chat-message.component.html -->
<div class="message" [class.user]="message.role === 'user'">
  <markdown [data]="message.content"></markdown>
</div>
```

**Typing Indicator**
```bash
npm install ngx-typing-animation
```

#### 7. Forms & Validation (Checkout, Product Filters)

**Reactive Forms (Built-in)**
Already in Angular

**NGX Formly (Dynamic Forms)**
```bash
npm install @ngx-formly/core @ngx-formly/material
```

**Use Case:** Dynamic checkout forms, product filters
```typescript
// Checkout form
fields: FormlyFieldConfig[] = [
  {
    key: 'email',
    type: 'input',
    props: {
      label: 'Email',
      required: true,
    }
  },
  {
    key: 'address',
    fieldGroup: [
      { key: 'street', type: 'input', props: { label: 'Street' } },
      { key: 'city', type: 'input', props: { label: 'City' } },
      { key: 'zip', type: 'input', props: { label: 'ZIP Code' } },
    ]
  }
];
```

#### 8. Product Display & Carousels

**Swiper (Product Image Slider)**
```bash
npm install swiper
```

**Usage:**
```typescript
// product-images.component.ts
import { Component } from '@angular/core';
import Swiper from 'swiper';

@Component({
  selector: 'app-product-images',
  template: `
    <div class="swiper">
      <div class="swiper-wrapper">
        <div class="swiper-slide" *ngFor="let image of images">
          <img [src]="image" alt="Product">
        </div>
      </div>
    </div>
  `
})
export class ProductImagesComponent {
  images = ['img1.jpg', 'img2.jpg', 'img3.jpg'];
  
  ngAfterViewInit() {
    new Swiper('.swiper', {
      slidesPerView: 1,
      navigation: true,
      pagination: { clickable: true }
    });
  }
}
```

**NGX Gallery**
```bash
npm install @ngx-gallery/core @ngx-gallery/lightbox
```

#### 9. Search & Filters

**Client-side Search**
```bash
npm install fuse.js
```

**Usage:**
```typescript
// services/search.service.ts
import Fuse from 'fuse.js';

export class SearchService {
  searchProducts(products: Product[], query: string) {
    const fuse = new Fuse(products, {
      keys: ['name', 'description', 'category'],
      threshold: 0.3
    });
    return fuse.search(query).map(result => result.item);
  }
}
```

**Server-side Search (Connect to FastAPI)**
Just use HttpClient to call FastAPI search endpoints

#### 10. Shopping Cart

**NGX Local Storage**
```bash
npm install @ngx-pwa/local-storage
```

**Cart Service:**
```typescript
// services/cart.service.ts
import { Injectable, signal } from '@angular/core';
import { StorageMap } from '@ngx-pwa/local-storage';

@Injectable({ providedIn: 'root' })
export class CartService {
  private cartItems = signal<CartItem[]>([]);

  constructor(private storage: StorageMap) {
    this.loadCart();
  }

  addToCart(product: Product) {
    const items = [...this.cartItems()];
    const existing = items.find(i => i.id === product.id);
    
    if (existing) {
      existing.quantity++;
    } else {
      items.push({ ...product, quantity: 1 });
    }
    
    this.cartItems.set(items);
    this.saveCart();
  }

  private saveCart() {
    this.storage.set('cart', this.cartItems()).subscribe();
  }

  private loadCart() {
    this.storage.get('cart').subscribe(items => {
      if (items) this.cartItems.set(items as CartItem[]);
    });
  }
}
```

#### 11. Payment Integration

**Stripe**
```bash
npm install @stripe/stripe-js
```

**Usage:**
```typescript
// services/payment.service.ts
import { loadStripe } from '@stripe/stripe-js';

export class PaymentService {
  private stripePromise = loadStripe('your_publishable_key');

  async checkout(items: CartItem[]) {
    const stripe = await this.stripePromise;
    
    // Call FastAPI to create checkout session
    const session = await this.http.post('/api/create-checkout-session', {
      items
    }).toPromise();
    
    // Redirect to Stripe checkout
    await stripe?.redirectToCheckout({
      sessionId: session.id
    });
  }
}
```

**Razorpay (India)**
```bash
npm install razorpay
```

#### 12. Notifications

**NGX Toastr**
```bash
npm install ngx-toastr @angular/animations
```

**Configuration:**
```typescript
// app.config.ts
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideToastr } from 'ngx-toastr';

export const appConfig: ApplicationConfig = {
  providers: [
    provideAnimations(),
    provideToastr({
      timeOut: 3000,
      positionClass: 'toast-top-right',
      preventDuplicates: true,
    }),
  ]
};
```

**Usage:**
```typescript
// component
constructor(private toastr: ToastrService) {}

addToCart(product: Product) {
  this.cartService.addToCart(product);
  this.toastr.success('Added to cart!', product.name);
}
```

**Sweetalert2 (Beautiful Modals)**
```bash
npm install sweetalert2
```

#### 13. Image Optimization

**NGX Image (Built-in Angular 17)**
```html
<img ngSrc="product.jpg" width="500" height="500" priority>
```

**Image Lazy Loading**
```bash
npm install ng-lazyload-image
```

#### 14. Infinite Scroll (Product Listings)

**NGX Infinite Scroll**
```bash
npm install ngx-infinite-scroll
```

**Usage:**
```html
<div infiniteScroll
     [infiniteScrollDistance]="2"
     [infiniteScrollThrottle]="50"
     (scrolled)="onScroll()">
  <app-product-card *ngFor="let product of products" [product]="product">
  </app-product-card>
</div>
```

#### 15. Date & Time

**Date-fns**
```bash
npm install date-fns
```

**Usage:**
```typescript
import { formatDistance } from 'date-fns';

// Order placed 2 hours ago
const orderTime = formatDistance(order.createdAt, new Date(), { addSuffix: true });
```

#### 16. Charts & Analytics Dashboard

**Chart.js**
```bash
npm install chart.js ng2-charts
```

**Usage:**
```typescript
// sales-chart.component.ts
import { Component } from '@angular/core';
import { ChartData, ChartType } from 'chart.js';

@Component({
  selector: 'app-sales-chart',
  template: `
    <canvas baseChart
            [data]="chartData"
            [type]="chartType">
    </canvas>
  `
})
export class SalesChartComponent {
  chartType: ChartType = 'line';
  chartData: ChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [{
      label: 'Sales',
      data: [1000, 1500, 1200, 1800, 2000]
    }]
  };
}
```

#### 17. Internationalization (Multi-language)

**NGX Translate**
```bash
npm install @ngx-translate/core @ngx-translate/http-loader
```

**Configuration:**
```typescript
// app.config.ts
import { provideHttpClient } from '@angular/common/http';
import { TranslateModule, TranslateLoader } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';

export function HttpLoaderFactory(http: HttpClient) {
  return new TranslateHttpLoader(http, './assets/i18n/', '.json');
}
```

**Translation Files:**
```json
// assets/i18n/en.json
{
  "CART": {
    "ADD": "Add to Cart",
    "REMOVE": "Remove",
    "TOTAL": "Total"
  },
  "PRODUCT": {
    "DETAILS": "Product Details",
    "PRICE": "Price"
  }
}
```

#### 18. SEO (Important for E-commerce)

**Angular Universal (SSR)**
```bash
ng add @nguniversal/express-engine
```

**Meta Tags Service**
```typescript
// services/seo.service.ts
import { Injectable } from '@angular/core';
import { Meta, Title } from '@angular/platform-browser';

@Injectable({ providedIn: 'root' })
export class SeoService {
  constructor(
    private meta: Meta,
    private title: Title
  ) {}

  updateProductPage(product: Product) {
    this.title.setTitle(`${product.name} - Your Store`);
    this.meta.updateTag({ name: 'description', content: product.description });
    this.meta.updateTag({ property: 'og:title', content: product.name });
    this.meta.updateTag({ property: 'og:image', content: product.image });
  }
}
```

#### 19. Analytics

**Google Analytics 4**
```bash
npm install @angular/fire
```

**Usage:**
```typescript
// Track product views
this.analytics.logEvent('view_item', {
  items: [{
    item_id: product.id,
    item_name: product.name,
    price: product.price
  }]
});

// Track purchases
this.analytics.logEvent('purchase', {
  transaction_id: order.id,
  value: order.total,
  currency: 'USD'
});
```

#### 20. Error Tracking

**Sentry**
```bash
npm install @sentry/angular @sentry/tracing
```

**Configuration:**
```typescript
// main.ts
import * as Sentry from "@sentry/angular";

Sentry.init({
  dsn: "your_sentry_dsn",
  integrations: [
    new Sentry.BrowserTracing({
      tracePropagationTargets: ["localhost", "https://your-fastapi-backend.com"],
      routingInstrumentation: Sentry.routingInstrumentation,
    }),
  ],
  tracesSampleRate: 1.0,
});
```

#### 21. Loading States

**NGX Skeleton Loader**
```bash
npm install ngx-skeleton-loader
```

**Usage:**
```html
<ngx-skeleton-loader *ngIf="loading" count="5" appearance="line"></ngx-skeleton-loader>
<div *ngIf="!loading">
  <app-product-card *ngFor="let product of products" [product]="product">
  </app-product-card>
</div>
```

#### 22. Utility Libraries

**Lodash**
```bash
npm install lodash-es @types/lodash-es
```

**Usage:**
```typescript
import { debounce } from 'lodash-es';

// Search with debounce
searchProducts = debounce((query: string) => {
  this.apiService.searchProducts(query).subscribe(results => {
    this.products = results;
  });
}, 300);
```

---

### 🐍 BACKEND (FastAPI + Python)

#### 1. Core FastAPI
```bash
pip install fastapi uvicorn
pip install python-multipart  # For file uploads
```

#### 2. AI & LLM Integration

**LangChain**
```bash
pip install langchain langchain-openai langchain-community
pip install openai
```

**Usage Example:**
```python
# ai/agents/product_recommendation_agent.py
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool

class ProductRecommendationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.tools = [
            Tool(
                name="search_products",
                func=self.search_products,
                description="Search for products in the database"
            ),
            Tool(
                name="check_inventory",
                func=self.check_inventory,
                description="Check product inventory"
            ),
            Tool(
                name="get_reviews",
                func=self.get_reviews,
                description="Get product reviews"
            )
        ]
        
    async def recommend(self, user_query: str, user_preferences: dict):
        """Generate AI-powered product recommendations"""
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.create_prompt()
        )
        executor = AgentExecutor(agent=agent, tools=self.tools)
        result = await executor.ainvoke({
            "input": user_query,
            "preferences": user_preferences
        })
        return result
    
    def search_products(self, query: str):
        # Search products in database
        pass
```

**OpenAI Direct**
```bash
pip install openai
```

**Anthropic Claude**
```bash
pip install anthropic
```

**Google AI**
```bash
pip install google-generativeai
```

#### 3. Vector Databases (For AI Search)

**Pinecone**
```bash
pip install pinecone-client
```

**Usage:**
```python
# ai/vector_store/product_search.py
import pinecone
from langchain.embeddings import OpenAIEmbeddings

class ProductVectorSearch:
    def __init__(self):
        pinecone.init(api_key="your_key")
        self.index = pinecone.Index("products")
        self.embeddings = OpenAIEmbeddings()
    
    async def semantic_search(self, query: str, top_k: int = 5):
        """AI-powered semantic product search"""
        query_embedding = self.embeddings.embed_query(query)
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        return results
```

**Chroma (Open Source)**
```bash
pip install chromadb
```

**Weaviate**
```bash
pip install weaviate-client
```

#### 4. Database

**SQLAlchemy (PostgreSQL)**
```bash
pip install sqlalchemy psycopg2-binary
pip install alembic  # For migrations
```

**Models:**
```python
# models/product.py
from sqlalchemy import Column, String, Float, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String)
    inventory = Column(Integer, default=0)
    image_url = Column(String)
    
    reviews = relationship("Review", back_populates="product")
    
class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("products.id"))
    user_id = Column(String, ForeignKey("users.id"))
    rating = Column(Integer)
    comment = Column(Text)
    
    product = relationship("Product", back_populates="reviews")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    total = Column(Float)
    status = Column(String)  # pending, paid, shipped, delivered
    items = relationship("OrderItem", back_populates="order")
```

**MongoDB (Alternative)**
```bash
pip install motor  # Async MongoDB
pip install beanie  # ODM
```

#### 5. Authentication & Security

**JWT Authentication**
```bash
pip install python-jose[cryptography]
pip install passlib[bcrypt]
pip install python-multipart
```

**Implementation:**
```python
# auth/jwt.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
```

**OAuth2**
```bash
pip install authlib
```

#### 6. Payment Processing

**Stripe**
```bash
pip install stripe
```

**Implementation:**
```python
# services/payment.py
import stripe

stripe.api_key = "your_stripe_secret_key"

async def create_checkout_session(items: list):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': item['name']},
                    'unit_amount': int(item['price'] * 100),
                },
                'quantity': item['quantity'],
            }
            for item in items
        ],
        mode='payment',
        success_url='https://yoursite.com/success',
        cancel_url='https://yoursite.com/cancel',
    )
    return session
```

**Razorpay**
```bash
pip install razorpay
```

#### 7. Real-time Communication

**WebSocket Support**
```bash
pip install websockets
```

**Implementation:**
```python
# websocket/chat.py
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process with AI agent
            response = await ai_agent.process(data)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        manager.active_connections.remove(websocket)
```

**Socket.io (Alternative)**
```bash
pip install python-socketio
```

#### 8. Image Handling

**Pillow**
```bash
pip install Pillow
```

**Cloudinary Integration**
```bash
pip install cloudinary
```

**Usage:**
```python
# services/image.py
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="your_cloud",
    api_key="your_key",
    api_secret="your_secret"
)

async def upload_product_image(file):
    result = cloudinary.uploader.upload(file)
    return result['secure_url']
```

#### 9. Email

**FastAPI Mail**
```bash
pip install fastapi-mail
```

**Usage:**
```python
# services/email.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="your@email.com",
    MAIL_PASSWORD="password",
    MAIL_FROM="your@email.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False
)

async def send_order_confirmation(email: str, order_details: dict):
    message = MessageSchema(
        subject="Order Confirmation",
        recipients=[email],
        body=f"Your order {order_details['id']} is confirmed!",
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
```

#### 10. Background Tasks

**Celery**
```bash
pip install celery redis
```

**Usage:**
```python
# tasks/celery_app.py
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def process_order(order_id: str):
    # Process order
    # Send confirmation email
    # Update inventory
    pass

@celery_app.task
def generate_ai_recommendations(user_id: str):
    # Generate personalized recommendations using AI
    pass
```

**FastAPI Background Tasks (Simpler)**
```python
from fastapi import BackgroundTasks

@app.post("/orders")
async def create_order(order: Order, background_tasks: BackgroundTasks):
    # Save order
    background_tasks.add_task(send_confirmation_email, order.user_email)
    background_tasks.add_task(update_inventory, order.items)
    return order
```

#### 11. Caching

**Redis**
```bash
pip install redis aioredis
```

**Usage:**
```python
# cache/redis_client.py
import aioredis
import json

redis = await aioredis.create_redis_pool('redis://localhost')

async def cache_products(category: str, products: list):
    await redis.setex(
        f"products:{category}",
        3600,  # 1 hour
        json.dumps(products)
    )

async def get_cached_products(category: str):
    cached = await redis.get(f"products:{category}")
    return json.loads(cached) if cached else None
```

#### 12. Search

**Elasticsearch**
```bash
pip install elasticsearch
```

**Meilisearch**
```bash
pip install meilisearch
```

#### 13. Validation

**Pydantic (Built-in)**
```python
from pydantic import BaseModel, EmailStr, validator

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    inventory: int
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

class OrderCreate(BaseModel):
    user_id: str
    items: list[OrderItem]
    shipping_address: Address
```

#### 14. Rate Limiting

**SlowAPI**
```bash
pip install slowapi
```

**Usage:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/products")
@limiter.limit("100/minute")
async def get_products(request: Request):
    return products
```

#### 15. CORS (For Angular Frontend)

**Built-in FastAPI**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 16. Logging & Monitoring

**Loguru**
```bash
pip install loguru
```

**Usage:**
```python
from loguru import logger

logger.add("logs/ecommerce.log", rotation="500 MB")

@app.post("/orders")
async def create_order(order: Order):
    logger.info(f"Order created: {order.id}")
    return order
```

**Sentry**
```bash
pip install sentry-sdk[fastapi]
```

#### 17. Testing

**Pytest**
```bash
pip install pytest pytest-asyncio httpx
```

**Usage:**
```python
# tests/test_products.py
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_get_products():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/products")
        assert response.status_code == 200
```

#### 18. Documentation (Auto-generated by FastAPI)

Access at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### 19. API Versioning

```python
from fastapi import APIRouter

api_v1 = APIRouter(prefix="/api/v1")
api_v2 = APIRouter(prefix="/api/v2")

@api_v1.get("/products")
async def get_products_v1():
    pass

@api_v2.get("/products")
async def get_products_v2():
    # New version with AI recommendations
    pass

app.include_router(api_v1)
app.include_router(api_v2)
```

---

## 🎯 COMPLETE INSTALLATION GUIDE

### Frontend (Angular)
```bash
cd Internship

# Core UI
ng add @angular/material
npm install primeng primeicons

# State Management
npm install @ngrx/store @ngrx/effects @ngrx/entity @ngrx/store-devtools

# Real-time
npm install socket.io-client @types/socket.io-client

# Markdown (AI Chat)
npm install ngx-markdown marked highlight.js

# Forms
npm install @ngx-formly/core @ngx-formly/material

# Utilities
npm install swiper fuse.js lodash-es @types/lodash-es date-fns

# Payment
npm install @stripe/stripe-js

# Notifications
npm install ngx-toastr sweetalert2

# Charts
npm install chart.js ng2-charts

# i18n
npm install @ngx-translate/core @ngx-translate/http-loader

# Storage
npm install @ngx-pwa/local-storage

# Infinite Scroll
npm install ngx-infinite-scroll

# Loading States
npm install ngx-skeleton-loader

# Error Tracking
npm install @sentry/angular @sentry/tracing

# Analytics
npm install @angular/fire
```

### Backend (FastAPI)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Core
pip install fastapi uvicorn[standard]
pip install python-multipart

# AI & Agents
pip install langchain langchain-openai langchain-community
pip install openai anthropic
pip install pinecone-client chromadb

# Database
pip install sqlalchemy psycopg2-binary alembic
# OR
pip install motor beanie  # MongoDB

# Auth
pip install python-jose[cryptography] passlib[bcrypt]

# Payment
pip install stripe razorpay

# WebSocket
pip install websockets python-socketio

# Image Processing
pip install Pillow cloudinary

# Email
pip install fastapi-mail

# Background Tasks
pip install celery redis

# Caching
pip install aioredis

# Search
pip install elasticsearch meilisearch

# Rate Limiting
pip install slowapi

# Logging
pip install loguru

# Monitoring
pip install sentry-sdk[fastapi]

# Testing
pip install pytest pytest-asyncio httpx
```

---

## 🏗️ PROJECT STRUCTURE

```
ecommerce-ai-agents/
├── frontend/                          # Angular Project
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   ├── product-list/
│   │   │   │   ├── product-detail/
│   │   │   │   ├── cart/
│   │   │   │   ├── checkout/
│   │   │   │   ├── ai-chatbot/
│   │   │   │   └── order-history/
│   │   │   ├── services/
│   │   │   │   ├── api.service.ts
│   │   │   │   ├── cart.service.ts
│   │   │   │   ├── auth.service.ts
│   │   │   │   ├── websocket.service.ts
│   │   │   │   └── ai-chat.service.ts
│   │   │   ├── store/
│   │   │   │   ├── cart/
│   │   │   │   ├── products/
│   │   │   │   ├── auth/
│   │   │   │   └── orders/
│   │   │   ├── models/
│   │   │   └── guards/
│   │   └── assets/
│   └── package.json
│
├── backend/                           # FastAPI Project
│   ├── main.py
│   ├── api/
│   │   ├── routes/
│   │   │   ├── products.py
│   │   │   ├── orders.py
│   │   │   ├── auth.py
│   │   │   ├── ai_chat.py
│   │   │   └── payments.py
│   ├── models/
│   │   ├── product.py
│   │   ├── order.py
│   │   └── user.py
│   ├── ai/
│   │   ├── agents/
│   │   │   ├── product_recommendation_agent.py
│   │   │   ├── customer_service_agent.py
│   │   │   └── inventory_agent.py
│   │   ├── vector_store/
│   │   └── tools/
│   ├── services/
│   │   ├── payment.py
│   │   ├── email.py
│   │   ├── image.py
│   │   └── search.py
│   ├── database/
│   ├── auth/
│   ├── cache/
│   └── requirements.txt
│
└── README.md
```

---

## 🚀 QUICK START COMMANDS

### Development

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm start
# Opens on http://localhost:4200
```

**Terminal 3 - Redis (if using caching):**
```bash
redis-server
```

**Terminal 4 - Celery (if using background tasks):**
```bash
cd backend
celery -A tasks.celery_app worker --loglevel=info
```

---

## 🎯 KEY INTEGRATION POINTS

### Angular → FastAPI Communication

```typescript
// frontend/src/app/services/api.service.ts
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private apiUrl = 'http://localhost:8000/api/v1';

  constructor(private http: HttpClient) {}

  // Products
  getProducts() {
    return this.http.get(`${this.apiUrl}/products`);
  }

  // AI Chat
  sendChatMessage(message: string) {
    return this.http.post(`${this.apiUrl}/ai/chat`, { message });
  }

  // Orders
  createOrder(order: any) {
    return this.http.post(`${this.apiUrl}/orders`, order);
  }
}
```

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/products")
async def get_products():
    return {"products": []}

@app.post("/api/v1/ai/chat")
async def ai_chat(message: dict):
    response = await ai_agent.process(message["message"])
    return {"response": response}
```

---

## 📚 ADDITIONAL RESOURCES

### Documentation
- **Angular**: https://angular.dev
- **FastAPI**: https://fastapi.tiangolo.com
- **LangChain**: https://python.langchain.com
- **NgRx**: https://ngrx.io
- **PrimeNG**: https://primeng.org

### Example Projects
- FastAPI E-commerce: https://github.com/topics/fastapi-ecommerce
- Angular E-commerce: https://github.com/topics/angular-ecommerce
- LangChain Agents: https://python.langchain.com/docs/modules/agents

---

**This is your complete stack for building an AI Agent-powered E-commerce platform with Angular + FastAPI! 🚀**

