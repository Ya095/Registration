from registration_app.core.config import settings
from registration_app.core.gunicorn_ import Application, get_app_options
from main import app


def main():
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


if __name__ == '__main__':
    main()
