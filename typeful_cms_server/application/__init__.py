import os
from flask import Flask

from .routes.query import query_routes

from .routes.model import model_routes
from .routes import default_routes

def init_app():
    app = Flask(__name__)
    
    with app.app_context():
        app.register_blueprint(default_routes.route_blueprint)
        app.register_blueprint(model_routes.model_routes_blueprint)
        app.register_blueprint(query_routes.row_routes_blueprint)
        return app

