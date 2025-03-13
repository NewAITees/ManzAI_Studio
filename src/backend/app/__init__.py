"""Flask application factory."""
from flask import Flask
from flask_cors import CORS

from backend.app.config import Config, DevelopmentConfig


def create_app(config_object: Config = DevelopmentConfig) -> Flask:
    """Create and configure the Flask application.

    Args:
        config_object: Configuration object to use.

    Returns:
        Configured Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    CORS(app)

    # Register blueprints
    from backend.app.routes import api
    app.register_blueprint(api.bp)

    return app 