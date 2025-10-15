from __future__ import annotations

from flask import Flask

from .config_routes import config_bp
from .lists import lists_bp
from .names import names_bp
from .text import text_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(config_bp)
    app.register_blueprint(lists_bp)
    app.register_blueprint(names_bp)
    app.register_blueprint(text_bp)

