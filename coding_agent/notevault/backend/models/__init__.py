from .database import Base, engine, get_db
from .user import User
from .note import Note

# Create all tables
Base.metadata.create_all(bind=engine)
