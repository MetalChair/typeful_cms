from os import stat
from typing import List, Tuple
from flask import Blueprint, request, g
import json

from flask.app import Flask

from typeful_cms_server.application.database import DB_ACTION_TYPE, perform_db_model_action
model_routes_blueprint = Blueprint("model_route_blueprint", __name__)


@model_routes_blueprint.route("/Create", methods = ["POST"])
def create_model():
    model = request.get_json()
    if is_valid_model(model):
        schema_list = posted_model_to_schema_list(model)
        status = perform_db_model_action(
            DB_ACTION_TYPE.CREATE, schema_list, model["name"])
        return {
            "actionSucceeded" : status,
            "errorMessage"    : getattr(g, "error", "")
        }

@model_routes_blueprint.route("/Add", methods = ["PATCH"])
def update_model():
    model = request.get_json()
    if(is_valid_model(model)):
        schema_list = posted_model_to_schema_list(model)
        status = perform_db_model_action(
            DB_ACTION_TYPE.UPDATE, schema_list, model["name"])
        return {
            "actionSucceeded" : status,
            "errorMessage"    : getattr(g, "error", "")
        }

    return

def posted_model_to_schema_list(model) -> List[Tuple[str, str, bool]]:
    schema_list = []
    for schema_item in model["model_def"]:
        schema_list.append(
            (
                schema_item["name"],
                schema_item["type"],
                schema_item["nullable"]
            )
        )
    return schema_list



def is_valid_model(model):
    '''
        Validates an order creation model and populates
        the request context object with any model errors
    '''
    if "name" not in model:
        g.error = "You must specify a model name"
        return False
    elif "model_def" not in model:
        g.error = "You must specify a model definition"
        return False
    return True
