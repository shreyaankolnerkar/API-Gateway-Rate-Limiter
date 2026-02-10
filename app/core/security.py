from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import APIKey
from app.db.session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
):
    api_key = (
        db.query(APIKey)
        .filter(APIKey.key == x_api_key, APIKey.is_active.is_(True))
        .first()
    )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )

    return api_key
