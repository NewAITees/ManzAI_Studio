"""Flask application factory."""
from flask import Flask
from flask_cors import CORS

from src.backend.app.config import Config, DevelopmentConfig


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
    from src.backend.app.routes import api, models, prompts
    app.register_blueprint(api.bp)
    app.register_blueprint(models.bp)
    app.register_blueprint(prompts.bp)

    return app 