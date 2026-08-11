"""Database operations for URL shortening."""

import string
import random

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import URL


SHORT_CODE_LENGTH = 6
SHORT_CODE_CHARS = string.ascii_letters + string.digits


def generate_short_code(length: int = SHORT_CODE_LENGTH) -> str:
    """Generate a random alphanumeric short code."""
    return "".join(random.choices(SHORT_CODE_CHARS, k=length))


def get_url_by_code(db: Session, short_code: str) -> URL | None:
    """Look up a URL record by its short code."""
    return db.query(URL).filter(URL.short_code == short_code).first()


def create_short_url(
    db: Session,
    original_url: str,
    custom_alias: str | None = None,
    expires_at=None,
) -> URL:
    """
    Create a new shortened URL.
    Uses custom_alias if provided, otherwise generates a random code.
    Retries on collision for auto-generated codes.
    """
    if custom_alias:
        short_code = custom_alias
    else:
        # Generate unique code, retry on (unlikely) collision
        for _ in range(10):
            short_code = generate_short_code()
            if not get_url_by_code(db, short_code):
                break
        else:
            raise RuntimeError("Failed to generate a unique short code after 10 attempts")

    url_record = URL(
        short_code=short_code,
        original_url=original_url,
        expires_at=expires_at,
    )
    db.add(url_record)
    db.commit()
    db.refresh(url_record)
    return url_record


def increment_click(db: Session, short_code: str) -> None:
    """Atomically increment the click counter for a short code."""
    db.execute(
        text("UPDATE urls SET click_count = click_count + 1 WHERE short_code = :code"),
        {"code": short_code},
    )
    db.commit()


def check_db_connection(db: Session) -> bool:
    """Quick connectivity check — used by /health endpoint."""
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
