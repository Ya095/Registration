from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from api_v1 import router as router_v1
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    yield
    # Clean up the ML models and release the resources


app = FastAPI(
    lifespan=lifespan,
    title="Users API",
    version="1.0.0",
    description="Working with users.",
)

app.include_router(router_v1, prefix=settings.api.prefix)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5170"],  # адрес фронта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        host=settings.run.host,
        port=settings.run.port,
    )
