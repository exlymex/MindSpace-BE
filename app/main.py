from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import auth
from app.core.config import settings
from app.db.base import Base
from app.db.sessions import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀Initializing")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    print("🛑 Finishing")
    await async_engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="MindSpace API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
