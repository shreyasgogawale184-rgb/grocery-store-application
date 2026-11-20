import os
from flask import Flask, jsonify

from config import Config
from app import db


def create_app(config_overrides=None):
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    app = Flask(__name__, static_folder=static_dir, static_url_path="/static")
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)

    from app.routes.products import bp as products_bp
    from app.routes.orders import bp as orders_bp

    app.register_blueprint(products_bp, url_prefix="/api")
    app.register_blueprint(orders_bp, url_prefix="/api")

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error="Resource not found"), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error=getattr(e, "description", "Bad request")), 400

    return app
