#!/usr/bin/env python3
"""Punto de entrada del backend: python run.py

La configuración se lee de variables de entorno o de apps/Backend/.env (ver config.py).
"""

import logging

from app.windows_fix import setup_windows_environment

setup_windows_environment()

from app import create_app  # noqa: E402
from config import Settings  # noqa: E402

settings = Settings.from_env()
app = create_app(settings)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app.run(host=settings.host, port=settings.port, debug=settings.debug)
