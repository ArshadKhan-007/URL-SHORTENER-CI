"""SQLAlchemy engine, session factory, and FastAPI dependency."""

from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Safe URL Encoding for Special Characters in Credentials
encoded_user = quote_plus(settings.DB_USER)
encoded_password = quote_plus(settings.DB_PASSWORD)

DATABASE_URL = (
    f"mysql+pymysql://{encoded_user}:{encoded_password}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Yield a DB session per request, ensure it closes after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()