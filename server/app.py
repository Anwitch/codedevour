from __future__ import annotations

import os
import webbrowser
from threading import Timer

from flask import Flask

from server.config import ROOT_DIR, SERVER_DIR, env_bool
from server.routes import register_blueprints


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(SERVER_DIR / "templates"),
        static_folder=str(ROOT_DIR / "static"),
    )
    register_blueprints(app)
    return app


app = create_app()


if __name__ == "__main__":
    def open_browser() -> None:
        webbrowser.open_new("http://127.0.0.1:5000")

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" and not getattr(app, "browser_opened", False):
        Timer(1, open_browser).start()
        app.browser_opened = True

    debug_mode = env_bool("FLASK_DEBUG", True)
    app.run(debug=debug_mode)

