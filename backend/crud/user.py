"""CRUD operations for User entities."""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from database.models import User
from schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    """Get user by Google ID."""
    return db.query(User).filter(User.google_id == google_id).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user."""
    db_user = User(
        email=user_data.email,
        google_id=user_data.google_id,
        name=user_data.name,
        avatar_url=user_data.avatar_url,
        preferences=user_data.preferences,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: str, user_data: UserUpdate) -> Optional[User]:
    """Update a user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_last_login(db: Session, user_id: str) -> Optional[User]:
    """Update user's last login time."""
    db_user = get_user(db, user_id)
    if db_user:
        db_user.last_login_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str) -> bool:
    """Delete a user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True
