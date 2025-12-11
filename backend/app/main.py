from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import init_db
from app.accounts.routes import router as accounts_router
from app.transactions.routes import router as transactions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    await init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="AutoAgents Demo Backend API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(transactions_router, prefix="/accounts", tags=["transactions"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

