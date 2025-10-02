from app.db import engine, Base
from app.models import User, Transaction, ChatMessage  # Import all models here

def create_tables():
    """
    Create all tables defined by SQLAlchemy models
    """
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("----- Tables created successfully! -----")

if __name__ == "__main__":
    create_tables()