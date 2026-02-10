import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import APIKey, Tier
from app.db.session import SessionLocal

router = APIRouter(prefix="/keys", tags=["keys"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_key(tier_name: str, db: Session = Depends(get_db)):
    tier = db.query(Tier).filter(Tier.name == tier_name).first()
    if not tier:
        raise HTTPException(404, "Tier not found")

    key = secrets.token_hex(16)
    api_key = APIKey(key=key, tier_id=tier.id)
    db.add(api_key)
    db.commit()
    return {"api_key": key, "tier": tier_name}


@router.get("/")
def list_keys(db: Session = Depends(get_db)):
    return db.query(APIKey).all()


@router.delete("/{key}")
def revoke_key(key: str, db: Session = Depends(get_db)):
    api_key = db.query(APIKey).filter(APIKey.key == key).first()
    if not api_key:
        raise HTTPException(404)
    api_key.is_active = False
    db.commit()
    return {"revoked": key}
