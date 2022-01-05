from flask import Blueprint, request
import json
model_creation_routes_blueprint = Blueprint("model_creation_blueprint", __name__)

@model_creation_routes_blueprint.route("/Create", methods = ["POST"])
def create_new_model_endpoint():
    req_json = request.get_json()
    if(setup_model_in_db(req_json)):
        #TODO: Setup proper methods on succesful model creation
        return
    else:
        #TODO: Error handling
        return
    return "<b>TODO: IMPLEMENT</b>"

def setup_model_in_db(model):
    return

def does_model_with