import logging
from loguru import logger
import sys
from registration_app.core.config import settings
from registration_app.core.gunicorn_.logs import InterceptHandler


def setup_logs() -> None:
    """Настройка logger совместно с loguru"""

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
                "format": settings.log.inplace_log_format,
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
