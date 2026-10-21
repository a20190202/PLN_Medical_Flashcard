import threading

from flask import Flask
from flask_cors import CORS

from config import Settings


class Services:
    """Dependencias de la app. El generador se arma la primera vez que se usa."""

    def __init__(self, settings, generator=None):
        self.settings = settings
        self._generator = generator
        self._lock = threading.Lock()

    @property
    def generator(self):
        with self._lock:
            if self._generator is None:
                from .rag.generator import build_generator

                self._generator = build_generator(self.settings)
            return self._generator


def create_app(settings=None, generator=None):
    settings = settings or Settings.from_env()

    app = Flask(__name__)
    app.json.sort_keys = False
    app.json.ensure_ascii = False
    CORS(app, resources={r"/*": {"origins": list(settings.cors_origins)}})
    app.extensions["medcards"] = Services(settings, generator)

    from .routes import main, register_error_handlers

    register_error_handlers(app)
    app.register_blueprint(main)
    return app
