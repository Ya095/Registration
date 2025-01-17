from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from loguru import logger
from api_v1 import router as router_v1
from registration_app.core.config import settings
from registration_app.core import session_manager
from registration_app.core.utils.role_cache import RoleCache


app = FastAPI(
    title="Users API",
    version="1.0.0",
    description="Working with users.",
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


@app.on_event("startup")
async def start_up():
    try:
        async with session_manager.create_session() as session:
            await RoleCache.initialize_roles(session)
            await RoleCache.load_roles(session)
            await session.commit()
    except Exception as e:
        await session.rollback()
        logger.exception(f"Start up transaction error: %s", str(e))
        exit(1)


@app.on_event("shutdown")
async def shut_down():
    await session_manager.dispose()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        host=settings.run.host,
        port=settings.run.port,
    )
