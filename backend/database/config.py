"""
Database configuration and session management for SQLite with SQLAlchemy.
Designed for easy migration to PostgreSQL later.
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

# Database file location
DATABASE_DIR = Path(__file__).parent.parent / "data"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/autoagents.db"

# For testing, use in-memory database
TESTING = os.getenv("TESTING", "false").lower() == "true"
if TESTING:
    DATABASE_URL = "sqlite:///:memory:"

# Create engine with SQLite-specific settings
# These settings ensure proper concurrent access for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    poolclass=StaticPool if TESTING else None,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # Log SQL queries
)


# Enable foreign key support for SQLite (disabled by default)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")  # Better concurrent access
    cursor.close()


# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Use with FastAPI's Depends().
    
    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.
    Call this on application startup.
    """
    from .models import Base
    Base.metadata.create_all(bind=engine)
    print(f"[DATABASE] Initialized database at {DATABASE_URL}")


def drop_db():
    """
    Drop all tables. Use with caution!
    Mainly for testing purposes.
    """
    from .models import Base
    Base.metadata.drop_all(bind=engine)
    print("[DATABASE] Dropped all tables")
