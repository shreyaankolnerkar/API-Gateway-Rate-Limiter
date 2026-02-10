import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.gateway.proxy import router as proxy_router
from app.routes.analytics import router as analytics_router
from app.routes.keys import router as keys_router
from app.workers.loggers import logger_worker

app = FastAPI(title="API Gateway with Rate Limiting")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proxy_router, prefix="/proxy")
app.include_router(keys_router)
app.include_router(analytics_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(logger_worker())
