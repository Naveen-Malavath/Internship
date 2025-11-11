# ⚡ Quick Stack Reference - AI Agents E-commerce
## Angular + JavaScript + FastAPI

---

## 🎯 ONE-COMMAND INSTALLATION

### Use the Automated Installer
```powershell
cd C:\Users\uppin\OneDrive\Desktop\internship\Internship
.\install-angular-fastapi-stack.ps1
```

Select your profile:
- **Option 1**: Essential Frontend (5 min)
- **Option 2**: E-commerce Frontend (8 min)
- **Option 3**: Complete Frontend (12 min)
- **Option 4**: Backend Setup Guide
- **Option 5**: Full Stack Guide

---

## 📦 MANUAL INSTALLATION

### Frontend (Angular) - Recommended Stack
```bash
# Essential (5 minutes)
ng add @angular/material
npm install @ngrx/store @ngrx/effects @ngrx/entity @ngrx/store-devtools
npm install socket.io-client
npm install ngx-markdown marked highlight.js
npm install ngx-toastr
npm install @sentry/angular

# E-commerce Additions (3 minutes)
npm install primeng primeicons
npm install @ngx-pwa/local-storage
npm install @stripe/stripe-js
npm install fuse.js swiper
npm install @ngx-formly/core @ngx-formly/material
npm install lodash-es date-fns
```

### Backend (FastAPI)
```bash
# Setup
mkdir backend && cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Core packages
pip install fastapi uvicorn[standard]
pip install langchain langchain-openai openai
pip install sqlalchemy psycopg2-binary
pip install python-jose[cryptography] passlib[bcrypt]
pip install stripe websockets
pip install python-multipart fastapi-mail
pip install sentry-sdk[fastapi]
```

---

## 🏗️ PROJECT STRUCTURE

```
project/
├── Internship/              # Angular Frontend
│   ├── src/app/
│   │   ├── components/
│   │   │   ├── product-list/
│   │   │   ├── product-detail/
│   │   │   ├── shopping-cart/
│   │   │   ├── checkout/
│   │   │   └── ai-chatbot/
│   │   ├── services/
│   │   │   ├── api.service.ts        # FastAPI connector
│   │   │   ├── cart.service.ts
│   │   │   ├── websocket.service.ts
│   │   │   └── ai-chat.service.ts
│   │   └── store/                    # NgRx state
│   └── package.json
│
└── backend/                 # FastAPI Backend
    ├── main.py
    ├── api/
    │   └── routes/
    │       ├── products.py
    │       ├── orders.py
    │       └── ai_chat.py
    ├── ai/
    │   └── agents/
    │       ├── product_agent.py
    │       └── customer_service_agent.py
    └── requirements.txt
```

---

## 🔌 CONNECTING FRONTEND TO BACKEND

### Angular Service (Frontend)
```typescript
// services/api.service.ts
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private apiUrl = 'http://localhost:8000/api/v1';

  constructor(private http: HttpClient) {}

  getProducts() {
    return this.http.get(`${this.apiUrl}/products`);
  }

  chatWithAI(message: string) {
    return this.http.post(`${this.apiUrl}/ai/chat`, { message });
  }

  createOrder(order: any) {
    return this.http.post(`${this.apiUrl}/orders`, order);
  }
}
```

### FastAPI Route (Backend)
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/products")
async def get_products():
    return {"products": []}

@app.post("/api/v1/ai/chat")
async def ai_chat(request: dict):
    # AI agent logic here
    return {"response": "AI response"}
```

---

## 🤖 AI AGENT IMPLEMENTATION

### Backend (LangChain Agent)
```python
# ai/agents/product_agent.py
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent

class ProductAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")
        self.tools = [
            self.search_products_tool,
            self.check_inventory_tool,
            self.get_reviews_tool
        ]
    
    async def recommend(self, user_query: str):
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        executor = AgentExecutor(agent=agent, tools=self.tools)
        return await executor.ainvoke({"input": user_query})
```

### Frontend (Chat Component)
```typescript
// components/ai-chatbot/ai-chatbot.component.ts
export class AIChatbotComponent {
  messages = signal<Message[]>([]);

  sendMessage(text: string) {
    this.messages.update(m => [...m, { role: 'user', text }]);
    
    this.apiService.chatWithAI(text).subscribe(response => {
      this.messages.update(m => [...m, { 
        role: 'assistant', 
        text: response.response 
      }]);
    });
  }
}
```

---

## 🚀 RUNNING THE PROJECT

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```
✅ Backend: http://localhost:8000
📚 API Docs: http://localhost:8000/docs

**Terminal 2 - Frontend:**
```bash
cd Internship
npm start
```
✅ Frontend: http://localhost:4200

### Production Build

**Frontend:**
```bash
npm run build
# Output: dist/
```

**Backend:**
```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

---

## 🎯 KEY LIBRARIES BY FEATURE

### AI & Agents
| Feature | Frontend | Backend |
|---------|----------|---------|
| **Chat UI** | ngx-markdown, highlight.js | - |
| **AI Integration** | - | langchain, openai |
| **Vector Search** | - | pinecone-client |
| **Real-time** | socket.io-client | websockets |

### E-commerce
| Feature | Frontend | Backend |
|---------|----------|---------|
| **UI Components** | Angular Material, PrimeNG | - |
| **State** | NgRx | - |
| **Cart** | @ngx-pwa/local-storage | Redis (cache) |
| **Payment** | @stripe/stripe-js | stripe |
| **Search** | fuse.js | elasticsearch |
| **Images** | ngx-image | Pillow, cloudinary |

### Core Features
| Feature | Frontend | Backend |
|---------|----------|---------|
| **Auth** | JWT in localStorage | python-jose |
| **Database** | - | SQLAlchemy, PostgreSQL |
| **Forms** | @ngx-formly | Pydantic |
| **Validation** | Reactive Forms | Pydantic |
| **i18n** | @ngx-translate | - |
| **Error Tracking** | @sentry/angular | sentry-sdk[fastapi] |

---

## 🔥 QUICK COMMANDS

### Frontend Commands
```bash
npm start                 # Dev server
npm run build            # Production build
npm test                 # Run tests
ng generate component    # Create component
ng add @angular/material # Add Material
```

### Backend Commands
```bash
uvicorn main:app --reload           # Dev server
uvicorn main:app --workers 4        # Production
alembic revision --autogenerate     # Create migration
alembic upgrade head                # Run migrations
pytest                              # Run tests
```

---

## 🔐 ENVIRONMENT VARIABLES

### Frontend (`src/environments/environment.ts`)
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  stripePublicKey: 'pk_test_...',
  socketUrl: 'http://localhost:8000'
};
```

### Backend (`.env`)
```bash
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:pass@localhost/dbname
STRIPE_SECRET_KEY=sk_test_...
JWT_SECRET_KEY=your-secret-key
REDIS_URL=redis://localhost:6379
```

---

## 📊 STATE MANAGEMENT (NgRx)

### Define State
```typescript
// store/cart/cart.state.ts
export interface CartState {
  items: CartItem[];
  total: number;
}
```

### Actions
```typescript
// store/cart/cart.actions.ts
export const addToCart = createAction(
  '[Cart] Add Item',
  props<{ product: Product }>()
);
```

### Reducer
```typescript
// store/cart/cart.reducer.ts
export const cartReducer = createReducer(
  initialState,
  on(addToCart, (state, { product }) => ({
    ...state,
    items: [...state.items, product]
  }))
);
```

### Use in Component
```typescript
constructor(private store: Store) {}

addToCart(product: Product) {
  this.store.dispatch(addToCart({ product }));
}

cartItems$ = this.store.select(selectCartItems);
```

---

## 💳 PAYMENT INTEGRATION

### Frontend (Stripe)
```typescript
import { loadStripe } from '@stripe/stripe-js';

async checkout() {
  const stripe = await loadStripe('pk_test_...');
  
  // Get session from backend
  const session = await this.http.post('/api/v1/create-checkout', {
    items: this.cartItems
  }).toPromise();
  
  // Redirect to Stripe
  await stripe.redirectToCheckout({
    sessionId: session.id
  });
}
```

### Backend (Stripe)
```python
import stripe

@app.post("/api/v1/create-checkout")
async def create_checkout(items: list):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=items,
        mode='payment',
        success_url='http://localhost:4200/success',
        cancel_url='http://localhost:4200/cancel',
    )
    return {"id": session.id}
```

---

## 📱 WEBSOCKET (REAL-TIME)

### Frontend
```typescript
import { io } from 'socket.io-client';

export class WebSocketService {
  private socket = io('http://localhost:8000');
  
  sendMessage(msg: string) {
    this.socket.emit('message', msg);
  }
  
  onMessage() {
    return new Observable(observer => {
      this.socket.on('message', data => observer.next(data));
    });
  }
}
```

### Backend
```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Response: {data}")
```

---

## 🔍 COMMON PATTERNS

### API Call Pattern
```typescript
// Frontend
this.apiService.getProducts()
  .pipe(
    catchError(this.handleError),
    tap(products => this.products.set(products))
  )
  .subscribe();
```

### Loading State Pattern
```typescript
loading = signal(false);

loadProducts() {
  this.loading.set(true);
  this.apiService.getProducts()
    .pipe(finalize(() => this.loading.set(false)))
    .subscribe(products => this.products.set(products));
}
```

### Error Handling Pattern
```typescript
private handleError(error: HttpErrorResponse) {
  if (error.status === 0) {
    console.error('Network error:', error.error);
  } else {
    console.error(`Backend returned ${error.status}:`, error.error);
  }
  this.toastr.error('Something went wrong!');
  return throwError(() => new Error('Something went wrong'));
}
```

---

## 🐛 DEBUGGING

### Frontend
```bash
# Browser DevTools
F12 → Console, Network, Sources

# Angular DevTools
Install Chrome extension "Angular DevTools"

# Check NgRx State
Redux DevTools extension
```

### Backend
```bash
# FastAPI automatic docs
http://localhost:8000/docs

# Logging
from loguru import logger
logger.info("Debug message")

# Interactive debugger
import pdb; pdb.set_trace()
```

---

## 📚 DOCUMENTATION LINKS

### Frontend
- **Angular**: https://angular.dev
- **Angular Material**: https://material.angular.io
- **PrimeNG**: https://primeng.org
- **NgRx**: https://ngrx.io

### Backend
- **FastAPI**: https://fastapi.tiangolo.com
- **LangChain**: https://python.langchain.com
- **SQLAlchemy**: https://www.sqlalchemy.org
- **Stripe**: https://stripe.com/docs/api

### AI & Tools
- **OpenAI**: https://platform.openai.com/docs
- **Pinecone**: https://docs.pinecone.io

---

## 🆘 TROUBLESHOOTING

### CORS Issues
**Backend:** Ensure Angular URL is in `allow_origins`
```python
allow_origins=["http://localhost:4200"]
```

### Port Already in Use
**Frontend:** `npm start -- --port 4300`
**Backend:** `uvicorn main:app --port 8001`

### Module Not Found
**Frontend:** `npm install`
**Backend:** `pip install -r requirements.txt`

### WebSocket Connection Failed
Check backend is running and URL matches

---

## 🎯 NEXT STEPS

1. ✅ Install libraries (use the installer script)
2. 📝 Configure environment variables
3. 🏗️ Set up project structure
4. 🔌 Connect frontend to backend
5. 🤖 Implement AI agents
6. 🛒 Build e-commerce features
7. 🧪 Write tests
8. 🚀 Deploy to production

---

**For detailed implementation, see `ANGULAR_FASTAPI_ECOMMERCE_STACK.md`**

**Happy coding! 🚀🤖🛒**

