from crypt import methods
from flask import Blueprint, request, g

row_routes_blueprint = Blueprint("row_route_blueprint", __name__)

@row_routes_blueprint.route("/<model_name>", methods = ["POST", "PATCH", "DELETE"])
def perform_row_action(model_name):
    print(model_name)
    return