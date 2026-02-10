from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.models import APIKey
from app.db.session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_api_key(x_api_key: str = Header(None), db: Session = Depends(get_db)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-Api-Key header missing")

    api_key = (
        db.query(APIKey)
        .filter(APIKey.key == x_api_key, APIKey.is_active == True)
        .first()
    )

    if not api_key:
        raise HTTPException(status_code=403, detail="Invalid or inactive API key")

    return api_key
