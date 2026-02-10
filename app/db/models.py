from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Tier(Base):
    __tablename__ = "tiers"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    rate_limit = Column(Integer)
    daily_request_limit = Column(Integer)
    api_keys = relationship("APIKey", back_populates="tier")


class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    tier_id = Column(Integer, ForeignKey("tiers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    tier = relationship("Tier", back_populates="api_keys")


class RequestLog(Base):
    __tablename__ = "request_logs"
    id = Column(Integer, primary_key=True)
    api_key = Column(String)
    path = Column(String)
    status_code = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
