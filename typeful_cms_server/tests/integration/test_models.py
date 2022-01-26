from typing import List
from flask import json
from flask.ctx import AppContext
from matplotlib.pyplot import table
from psycopg2 import sql

from typeful_cms_server.application.database import get_db, get_db_cursor
from typeful_cms_server.tests.helpers import *

SAMPLE_CREATION_POST_DATA =   {
    "users" : [
        {
            "id": 1,
            "name": "Leanne Graham",
            "username": "Bret",
            "email": "Sincere@april.biz",
            "address": {
                "street": "Kulas Light",
                "suite": "Apt. 556",
                "city": "Gwenborough",
                "zipcode": "92998-3874",
                "geo": {
                    "lat": "-37.3159",
                    "lng": "81.1496"
                }
            },
            "favorite_number" : 5.555,
            "aliases" : ["greg", 5, "Daniel"],
            "phone": "1-770-736-8031 x56442",
            "website": "hildegard.org",
            "company": {
                "name": "Romaguera-Crona",
                "catchPhrase": "Multi-layered client-server neural-net",
                "bs": "harness real-time e-markets"
            }
        },
        {
            "id": 1,
            "name": "Leanne Graham",
            "username": "Bret",
            "email": "Sincere@april.biz",
            "address": {
                "street": "Kulas Light",
                "suite": "Apt. 556",
                "city": "Gwenborough",
                "zipcode": "92998-3874",
                "geo": {
                    "lat": "-37.3159",
                    "lng": "81.1496"
                }
            },
            "favorite_number" : 5.555,
            "aliases" : ["greg", 5, "Daniel"],
            "phone": "1-770-736-8031 x56442",
            "website": "hildegard.org",
            "company": {
                "name": "Romaguera-Crona",
                "catchPhrase": "Multi-layered client-server neural-net",
                "bs": "harness real-time e-markets"
            }
        }
    ],
    "Butts": {
        "hello" : "Goodbye"
    }
    
}

SAMPLE_UPDATE_DATA = {
    "drop": {
        "users" : {
            "columns" :[
                "favorite_number",
                "name"
            ]
        }
    }
}



def test_simple_model_creation(test_app : AppContext):
    #Arrange
    
    #Act
    res = test_app.app.test_client().post("/Model", json = SAMPLE_CREATION_POST_DATA)
    
    #Assert
    responseJson = json.loads(res.data)
    succesful_response_object(responseJson)
    cols_exist_on_table("BUTTS", ["hello"])
    # cols_exist_on_table("test_model",["my_cool_string", "my_cool_int"])
    # table_contains_record("typeful_routes", 
    #     ["table_name", "query_name"], ["test_model", "TestModel"])

def test_complex_model_creation(test_app : AppContext):
    #Arrange
    
    #Act
    res = test_app.app.test_client().post("/Model", json = SAMPLE_CREATION_NESTED_POST_DATA)
    
    #Assert
    responseJson = json.loads(res.data)
    succesful_response_object(responseJson)
    cols_exist_on_table("test_model",["my_cool_string", "my_cool_int"])
    table_contains_record("typeful_routes", 
        ["table_name", "query_name"], ["test_model", "TestModel"])


def test_add_to_model(test_app : AppContext):
    #Arrange
    test_simple_model_creation(test_app)

    #Act
    res = test_app.app.test_client().patch("/Model", json = SAMPLE_UPDATE_DATA)
    responseJson = json.loads(res.data)

    #Asset
    succesful_response_object(responseJson)

def test_delete_from_model(test_app : AppContext):
    #Arrange
    test_simple_model_creation(test_app)
    
    #Act
    res = test_app.app.test_client().delete("/Model/Geo")
    responseJson = json.loads(res.data)

    #Assert
    succesful_response_object(responseJson)


