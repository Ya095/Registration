from gunicorn.app.base import BaseApplication
from fastapi import FastAPI


class Application(BaseApplication):
    def __init__(self, app: FastAPI, options: dict | None = None):
        self.options = options or {}
        self.app = app
        super().__init__()

    def load(self) -> FastAPI:
        return self.app

    @property
    def config_options(self) -> dict:
        return {
            k: v
            for k, v in self.options.items()
            if k in self.cfg.settings and v is not None
        }

    def load_config(self) -> None:
        for key, value in self.config_options.items():
            self.cfg.set(key.lower(), value)
