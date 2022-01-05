from flask import Blueprint

route_blueprint = Blueprint("route_blueprint", __name__)

@route_blueprint.route("/<path:full_path>")
def catch_all_routes(full_path):
    path_args = full_path.split('/')
    print(path_args)
    return str(path_args)