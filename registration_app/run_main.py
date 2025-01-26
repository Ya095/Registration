import logging
from loguru import logger
import sys
from registration_app.core.config import settings
from registration_app.core.gunicorn_ import Application, get_app_options
from registration_app.core.gunicorn_.logs import InterceptHandler
from main import app


if __name__ == '__main__':
    intercept_handler = InterceptHandler()
    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]
            logging.getLogger(name).propagate = False

    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": settings.log.log_level,
                "format": f"<green>{settings.log.log_format}</green> | "
                          "<level>{level: <8}</level> | "
                          "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                          "<level>{message}</level>",
                "backtrace": True,
                "diagnose": True,
                "enqueue": True,
            },
            {
                "sink": settings.log.path_to_save,
                "level": settings.log.log_level,
                "format": settings.log.log_format,
                "rotation": "100 MB",
                "retention": "30 days",
                "compression": "zip",
                "backtrace": True,
                "diagnose": True,
                "enqueue": True,
            },
        ]
    )

    Application(
        app=app,
        options=get_app_options(
            host=settings.run.host,
            port=settings.run.port,
            timeout=settings.run.timeout,
            workers=settings.run.workers,
            log_level=settings.log.log_level,
        )
    ).run()
