from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import settings

# Engine configuration (uses sqlite in-memory fallback for testing if postgresql driver is not available/configured)
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
    # SQLAlchemy 2.0+ standard connection string handling
    engine = create_engine(database_url, pool_pre_ping=True)
else:
    engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for providing a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
