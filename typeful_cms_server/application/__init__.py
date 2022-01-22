from flask import Flask
from .routes import default_routes, model_routes, row_routes

def init_app():
    app = Flask(__name__)
    with app.app_context():
        app.register_blueprint(default_routes.route_blueprint)
        app.register_blueprint(model_routes.model_routes_blueprint)
        app.register_blueprint(row_routes.row_routes_blueprint)
        return app

