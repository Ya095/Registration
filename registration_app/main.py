from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger
from api_v1 import router as router_v1
from registration_app.core.config import settings
from registration_app.core import session_manager
from registration_app.core.utils.role_cache import RoleCache
from registration_app.logs.setup_logs import setup_logs
from starlette_exporter import handle_metrics, PrometheusMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan-менеджер для управления ресурсами приложения."""

    try:
        async with session_manager.create_session() as session:
            await RoleCache.initialize_roles(session)
            await RoleCache.load_roles(session)
            await session.commit()
    except Exception as e:
        await session.rollback()
        logger.exception(f"Start up transaction error: %s", str(e))
        exit(1)

    yield

    await session_manager.dispose()


app = FastAPI(
    title="User registration API",
    version="1.0.0",
    description="Working with users and their roles.",
    lifespan=lifespan,
)


@app.get("/")
def home_page():
    return {"message": "Добро пожаловать!"}


app.include_router(router_v1)

origins: list[str] = [
    "http://localhost:5170",  # адрес фронта
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


if __name__ == "__main__":
    setup_logs()

    uvicorn.run(
        "main:app",
        reload=True,
        host=settings.run.host,
        port=settings.run.port,
    )
