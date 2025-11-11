# AI Agents E-commerce Stack Installer
# Angular + JavaScript Frontend | FastAPI Backend

Write-Host "🤖🛒 AI Agents E-commerce Platform Installer" -ForegroundColor Cyan
Write-Host "Angular + JavaScript + FastAPI Stack" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: package.json not found!" -ForegroundColor Red
    Write-Host "Please run this script from the Internship directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "Select your installation profile:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 🎨 Essential Frontend (Material + State + Chat UI)" -ForegroundColor Green
Write-Host "2. 🛒 E-commerce Frontend (Essential + Cart + Payment + Search)" -ForegroundColor Green
Write-Host "3. 🚀 Complete Frontend (Everything for production)" -ForegroundColor Green
Write-Host "4. 🐍 Backend Requirements (Shows FastAPI installation commands)" -ForegroundColor Green
Write-Host "5. 🌟 Full Stack (Frontend + Backend setup guide)" -ForegroundColor Green
Write-Host ""

$choice = Read-Host "Enter choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host "`n📦 Installing Essential Frontend Stack..." -ForegroundColor Cyan
        Write-Host "⏱️  Estimated time: 5-7 minutes" -ForegroundColor Yellow
        Write-Host ""
        
        Write-Host "1/8 Installing Angular Material..." -ForegroundColor Yellow
        ng add @angular/material --skip-confirmation
        
        Write-Host "`n2/8 Installing State Management (NgRx)..." -ForegroundColor Yellow
        npm install @ngrx/store @ngrx/effects @ngrx/entity @ngrx/store-devtools
        
        Write-Host "`n3/8 Installing Markdown (AI Chat)..." -ForegroundColor Yellow
        npm install ngx-markdown marked highlight.js
        
        Write-Host "`n4/8 Installing Real-time Communication..." -ForegroundColor Yellow
        npm install socket.io-client
        
        Write-Host "`n5/8 Installing Notifications..." -ForegroundColor Yellow
        npm install ngx-toastr @angular/animations
        
        Write-Host "`n6/8 Installing Forms..." -ForegroundColor Yellow
        npm install @ngx-formly/core @ngx-formly/material
        
        Write-Host "`n7/8 Installing Utilities..." -ForegroundColor Yellow
        npm install lodash-es date-fns
        
        Write-Host "`n8/8 Installing Error Tracking..." -ForegroundColor Yellow
        npm install @sentry/angular
        
        Write-Host "`n✅ Essential frontend stack installed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 Next Steps:" -ForegroundColor Yellow
        Write-Host "1. Update app.config.ts with providers" -ForegroundColor White
        Write-Host "2. Read ANGULAR_FASTAPI_ECOMMERCE_STACK.md for configuration" -ForegroundColor White
        Write-Host "3. Set up FastAPI backend (choose option 4)" -ForegroundColor White
    }
    
    "2" {
        Write-Host "`n📦 Installing E-commerce Frontend Stack..." -ForegroundColor Cyan
        Write-Host "⏱️  Estimated time: 8-10 minutes" -ForegroundColor Yellow
        Write-Host ""
        
        Write-Host "1/13 Installing Angular Material..." -ForegroundColor Yellow
        ng add @angular/material --skip-confirmation
        
        Write-Host "`n2/13 Installing PrimeNG (E-commerce Components)..." -ForegroundColor Yellow
        npm install primeng primeicons
        
        Write-Host "`n3/13 Installing State Management..." -ForegroundColor Yellow
        npm install @ngrx/store @ngrx/effects @ngrx/entity @ngrx/store-devtools
        
        Write-Host "`n4/13 Installing AI Chat UI..." -ForegroundColor Yellow
        npm install ngx-markdown marked highlight.js
        
        Write-Host "`n5/13 Installing Real-time..." -ForegroundColor Yellow
        npm install socket.io-client
        
        Write-Host "`n6/13 Installing Shopping Cart Storage..." -ForegroundColor Yellow
        npm install @ngx-pwa/local-storage
        
        Write-Host "`n7/13 Installing Payment (Stripe)..." -ForegroundColor Yellow
        npm install @stripe/stripe-js
        
        Write-Host "`n8/13 Installing Search..." -ForegroundColor Yellow
        npm install fuse.js
        
        Write-Host "`n9/13 Installing Product Display..." -ForegroundColor Yellow
        npm install swiper
        
        Write-Host "`n10/13 Installing Notifications..." -ForegroundColor Yellow
        npm install ngx-toastr sweetalert2
        
        Write-Host "`n11/13 Installing Forms..." -ForegroundColor Yellow
        npm install @ngx-formly/core @ngx-formly/material
        
        Write-Host "`n12/13 Installing Utilities..." -ForegroundColor Yellow
        npm install lodash-es date-fns
        
        Write-Host "`n13/13 Installing Error Tracking..." -ForegroundColor Yellow
        npm install @sentry/angular
        
        Write-Host "`n✅ E-commerce frontend stack installed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 Next Steps:" -ForegroundColor Yellow
        Write-Host "1. Configure providers in app.config.ts" -ForegroundColor White
        Write-Host "2. Set up Stripe keys" -ForegroundColor White
        Write-Host "3. Configure Socket.io connection" -ForegroundColor White
        Write-Host "4. Set up FastAPI backend (choose option 4)" -ForegroundColor White
    }
    
    "3" {
        Write-Host "`n📦 Installing Complete Frontend Stack..." -ForegroundColor Cyan
        Write-Host "⏱️  Estimated time: 10-15 minutes" -ForegroundColor Yellow
        Write-Host ""
        
        Write-Host "Installing all packages..." -ForegroundColor Yellow
        
        # UI Components
        Write-Host "`n[1/4] UI Components..." -ForegroundColor Cyan
        ng add @angular/material --skip-confirmation
        npm install primeng primeicons
        
        # Core Features
        Write-Host "`n[2/4] Core Features..." -ForegroundColor Cyan
        npm install @ngrx/store @ngrx/effects @ngrx/entity @ngrx/store-devtools @ngrx/router-store
        npm install socket.io-client
        npm install ngx-markdown marked highlight.js
        npm install @ngx-formly/core @ngx-formly/material
        npm install @ngx-pwa/local-storage
        
        # E-commerce Features
        Write-Host "`n[3/4] E-commerce Features..." -ForegroundColor Cyan
        npm install @stripe/stripe-js
        npm install fuse.js
        npm install swiper
        npm install ngx-toastr sweetalert2
        npm install ngx-infinite-scroll
        npm install ngx-skeleton-loader
        
        # Advanced Features
        Write-Host "`n[4/4] Advanced Features..." -ForegroundColor Cyan
        npm install chart.js ng2-charts
        npm install @ngx-translate/core @ngx-translate/http-loader
        npm install @angular/fire
        npm install @sentry/angular @sentry/tracing
        npm install lodash-es date-fns
        
        Write-Host "`n✅ Complete frontend stack installed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 You now have:" -ForegroundColor Green
        Write-Host "  ✓ Angular Material & PrimeNG" -ForegroundColor White
        Write-Host "  ✓ NgRx State Management" -ForegroundColor White
        Write-Host "  ✓ AI Chatbot UI" -ForegroundColor White
        Write-Host "  ✓ Real-time WebSocket" -ForegroundColor White
        Write-Host "  ✓ Shopping Cart" -ForegroundColor White
        Write-Host "  ✓ Payment Integration" -ForegroundColor White
        Write-Host "  ✓ Search & Filters" -ForegroundColor White
        Write-Host "  ✓ Charts & Analytics" -ForegroundColor White
        Write-Host "  ✓ i18n Support" -ForegroundColor White
        Write-Host "  ✓ Error Tracking" -ForegroundColor White
    }
    
    "4" {
        Write-Host "`n🐍 FastAPI Backend Installation Guide" -ForegroundColor Cyan
        Write-Host "======================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📂 Create backend directory:" -ForegroundColor Yellow
        Write-Host "  mkdir backend" -ForegroundColor White
        Write-Host "  cd backend" -ForegroundColor White
        Write-Host ""
        Write-Host "🐍 Create virtual environment:" -ForegroundColor Yellow
        Write-Host "  python -m venv venv" -ForegroundColor White
        Write-Host "  .\venv\Scripts\activate  # On Windows" -ForegroundColor White
        Write-Host ""
        Write-Host "📦 Create requirements.txt:" -ForegroundColor Yellow
        
        # Create requirements.txt in backend folder if it doesn't exist
        if (-not (Test-Path "..\backend")) {
            New-Item -ItemType Directory -Path "..\backend" -Force | Out-Null
        }
        
        $requirementsContent = @"
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# AI & Agents
langchain==0.1.0
langchain-openai==0.0.2
openai==1.3.7
anthropic==0.8.0
pinecone-client==3.0.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.0

# Auth & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Payment
stripe==7.7.0

# WebSocket
websockets==12.0

# Image Processing
Pillow==10.1.0
cloudinary==1.36.0

# Email
fastapi-mail==1.4.1

# Background Tasks
celery==5.3.4
redis==5.0.1

# Caching
aioredis==2.0.1

# Rate Limiting
slowapi==0.1.9

# Logging
loguru==0.7.2

# Monitoring
sentry-sdk[fastapi]==1.38.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# CORS
python-cors==1.0.0
"@
        
        $requirementsContent | Out-File -FilePath "..\backend\requirements.txt" -Encoding UTF8
        
        Write-Host ""
        Write-Host "✅ requirements.txt created in ../backend/" -ForegroundColor Green
        Write-Host ""
        Write-Host "📥 Install packages:" -ForegroundColor Yellow
        Write-Host "  pip install -r requirements.txt" -ForegroundColor White
        Write-Host ""
        Write-Host "🚀 Create main.py:" -ForegroundColor Yellow
        
        $mainPyContent = @"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI E-commerce API", version="1.0.0")

# Enable CORS for Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI E-commerce API"}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}

# Import routes here
# from api.routes import products, orders, ai_chat
# app.include_router(products.router, prefix="/api/v1")
# app.include_router(orders.router, prefix="/api/v1")
# app.include_router(ai_chat.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
"@
        
        $mainPyContent | Out-File -FilePath "..\backend\main.py" -Encoding UTF8
        
        Write-Host "✅ main.py created in ../backend/" -ForegroundColor Green
        Write-Host ""
        Write-Host "▶️  Run server:" -ForegroundColor Yellow
        Write-Host "  uvicorn main:app --reload --port 8000" -ForegroundColor White
        Write-Host ""
        Write-Host "📚 API Docs will be available at:" -ForegroundColor Yellow
        Write-Host "  http://localhost:8000/docs" -ForegroundColor White
        Write-Host "  http://localhost:8000/redoc" -ForegroundColor White
    }
    
    "5" {
        Write-Host "`n🌟 Full Stack Setup Guide" -ForegroundColor Cyan
        Write-Host "=========================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "This will guide you through setting up both frontend and backend" -ForegroundColor Yellow
        Write-Host ""
        
        Write-Host "Step 1: Install Frontend" -ForegroundColor Green
        Write-Host "------------------------" -ForegroundColor Green
        $installFrontend = Read-Host "Install E-commerce frontend stack? (y/n)"
        
        if ($installFrontend -eq "y") {
            Write-Host "`nInstalling frontend..." -ForegroundColor Cyan
            ng add @angular/material --skip-confirmation
            npm install primeng primeicons @ngrx/store @ngrx/effects @ngrx/entity @ngrx/store-devtools socket.io-client ngx-markdown marked highlight.js @ngx-formly/core @ngx-formly/material @ngx-pwa/local-storage @stripe/stripe-js fuse.js swiper ngx-toastr sweetalert2 @sentry/angular lodash-es date-fns
            Write-Host "✅ Frontend installed!" -ForegroundColor Green
        }
        
        Write-Host "`nStep 2: Setup Backend" -ForegroundColor Green
        Write-Host "---------------------" -ForegroundColor Green
        Write-Host "Backend setup requires Python. Follow these commands:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  cd .." -ForegroundColor White
        Write-Host "  mkdir backend" -ForegroundColor White
        Write-Host "  cd backend" -ForegroundColor White
        Write-Host "  python -m venv venv" -ForegroundColor White
        Write-Host "  .\venv\Scripts\activate" -ForegroundColor White
        Write-Host "  pip install -r requirements.txt" -ForegroundColor White
        Write-Host "  uvicorn main:app --reload" -ForegroundColor White
        Write-Host ""
        
        Write-Host "Step 3: Environment Variables" -ForegroundColor Green
        Write-Host "-----------------------------" -ForegroundColor Green
        Write-Host "Create .env files:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Frontend (src/environments/environment.ts):" -ForegroundColor White
        Write-Host "  apiUrl: 'http://localhost:8000'" -ForegroundColor Gray
        Write-Host "  stripePublicKey: 'your_key'" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Backend (.env):" -ForegroundColor White
        Write-Host "  OPENAI_API_KEY=your_key" -ForegroundColor Gray
        Write-Host "  DATABASE_URL=postgresql://..." -ForegroundColor Gray
        Write-Host "  STRIPE_SECRET_KEY=your_key" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "✅ Setup guide complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📖 Read ANGULAR_FASTAPI_ECOMMERCE_STACK.md for details" -ForegroundColor Yellow
    }
    
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🎉 Installation Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Documentation:" -ForegroundColor Yellow
Write-Host "  ANGULAR_FASTAPI_ECOMMERCE_STACK.md - Complete guide" -ForegroundColor White
Write-Host ""
Write-Host "🚀 To start development:" -ForegroundColor Yellow
Write-Host "  Frontend: npm start (http://localhost:4200)" -ForegroundColor White
Write-Host "  Backend:  uvicorn main:app --reload (http://localhost:8000)" -ForegroundColor White
Write-Host ""
Write-Host "Good luck building your AI E-commerce platform! 🤖🛒" -ForegroundColor Cyan

