from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import tasks
from database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])

@app.get("/")
def read_root():
    return {"message": "Welcome to TaskFlow API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
