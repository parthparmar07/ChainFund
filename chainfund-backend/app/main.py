from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.db import init_db, close_db
from app.routers import users, campaigns, funding, milestones, votes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="ChainFund Lite API",
    description="Decentralized crowdfunding dApp backend with milestone-based payments and NFT badges",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(campaigns.router, prefix="/api/v1", tags=["campaigns"])
app.include_router(funding.router, prefix="/api/v1", tags=["funding"])
app.include_router(milestones.router, prefix="/api/v1", tags=["milestones"])
app.include_router(votes.router, prefix="/api/v1", tags=["votes"])


@app.get("/")
async def root():
    return {"message": "ChainFund Lite API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )