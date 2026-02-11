# API-Gateway-Rate-Limiter
## API Gateway – Reverse Proxy with Rate Limiting, Caching & Circuit Breaker

A production-style **API Gateway / Reverse Proxy** built using **FastAPI**.  
This gateway forwards requests to upstream services while applying **rate limiting, caching, circuit breaker protection, and analytics logging**.

---

## Features

- Reverse proxy using `httpx` (async)
- API key authentication with tiers (free / basic / premium)
- Token Bucket rate limiting (Redis)
- Response caching for GET requests (Redis)
- Circuit breaker pattern for upstream services
- Async request logging & analytics
- Request / response transformation support
- Dockerized setup
- CI/CD ready (Railway deployment)

---

## Tech Stack

- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy + Alembic
- httpx
- Pytest
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Railway (Deployment)

---


