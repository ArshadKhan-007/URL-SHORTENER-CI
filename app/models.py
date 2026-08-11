"""ORM model for the `urls` table."""

from sqlalchemy import Column, Integer, String, Text, DateTime, func

from app.database import Base


class URL(Base):
    """Single table — custom alias and expiry are just extra columns."""

    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    short_code = Column(String(20), unique=True, nullable=False, index=True)
    original_url = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    click_count = Column(Integer, nullable=False, default=0)
