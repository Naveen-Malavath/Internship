from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, notes
import models

app = FastAPI(title="NoteVault API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])

@app.get("/")
def read_root():
    return {"message": "Welcome to NoteVault API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
