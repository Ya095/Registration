from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api_v1 import router as router_v1
from registration_app.core.config import settings


app = FastAPI(
    title="Users API",
    version="1.0.0",
    description="Working with users.",
)


@app.get("/")
def home_page():
    return {
        "message": "Добро пожаловать!"
    }


app.include_router(router_v1, prefix=settings.api.prefix)

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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        host=settings.run.host,
        port=settings.run.port,
    )
