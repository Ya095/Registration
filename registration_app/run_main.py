from registration_app.core.config import settings
from registration_app.logs.setup_logs import setup_logs
from registration_app.core.gunicorn_ import Application, get_app_options
from main import app


if __name__ == '__main__':
    setup_logs()

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
