from __future__ import annotations

import os
import webbrowser
from threading import Timer

from flask import Flask

import json
from server.config import ROOT_DIR, SERVER_DIR, env_bool
from server.routes import register_blueprints

def find_and_parse_alias_config(project_root: str) -> Dict[str, Any]:
    """Finds and parses tsconfig.json or jsconfig.json for path aliases."""
    for config_file in ['tsconfig.json', 'jsconfig.json']:
        config_path = os.path.join(project_root, config_file)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    return config_data.get('compilerOptions', {}).get('paths', {})
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {config_file}")
    return {}

def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(SERVER_DIR / "templates"),
        static_folder=str(ROOT_DIR / "static"),
    )
    
    # Load alias config and store it in the app
    # This assumes the project being analyzed is in a 'frontend' subdirectory
    # In a more robust implementation, this would be configurable.
    project_root = str(ROOT_DIR / "frontend")
    app.config['ALIAS_CONFIG'] = find_and_parse_alias_config(project_root)
    
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

