from flask import Blueprint, request, g
import json

from flask.app import Flask

from typeful_cms_server.application.database import create_model_database
model_creation_routes_blueprint = Blueprint("model_creation_blueprint", __name__)

@model_creation_routes_blueprint.before_request
def before_model_endpoint():
    g.model_erros = []

@model_creation_routes_blueprint.route("/Create", methods = ["POST"])
def create_new_model_endpoint():
    req_json = request.get_json()
    if not is_valid_model(req_json):
        return

    if(setup_model_in_db(req_json)):
        #TODO: Setup proper methods on succesful model creation
        return
    else:
        #TODO: Error handling
        return
    return "<b>TODO: IMPLEMENT</b>"

def setup_model_in_db(model):
    path_list = request.path.strip("/").split("/") #Split path list
    schema_list = []
    for schema_item in model["model_def"]:
        schema_list.append(
            (
                schema_item["name"],
                schema_item["type"],
                schema_item["nullable"]
            )
        )
    test_schema = [("test", "text", False),("new","text",True)]
    create_model_database(schema_list, model["name"])

    return

def parse_path():
    return

def is_valid_model(model):
    '''
        Validates an order creation model and populates
        the request context object with any model errors
    '''
    if "name" not in model:
        request["errors"].push("You must specify a model name")
        return False
    return True
