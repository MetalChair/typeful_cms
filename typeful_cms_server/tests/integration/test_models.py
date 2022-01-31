from typing import List
from flask import json
from flask.ctx import AppContext
from psycopg2 import sql

from application.database.database import get_db, get_db_cursor
from tests.helpers import *

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

SAMPLE_DROP_DATA = {
    "drop": {
        "users" : {
            "columns" :[
                "favorite_number",
                "name"
            ]
        }
    }
}



def test_model_creation(test_app : AppContext):
    #Arrange
    
    #Act
    res = test_app.app.test_client().post("/Model", json = SAMPLE_CREATION_POST_DATA)
    
    #Assert
    responseJson = json.loads(res.data)
    succesful_response_object(responseJson)
    cols_exist_on_table("BUTTS", ["hello"])
    cols_exist_on_table("USERS",["id","name","favorite_number"])

def test_delete_column_from_model(test_app : AppContext):
    #Arrange
    test_model_creation(test_app)
    res = test_app.app.test_client().patch("/Model", json = SAMPLE_DROP_DATA)
    succesful_response_object(json.loads(res.data))
    cols_dont_exist_on_table("USERS", ["favorite_number", "name"])


# def test_delete_from_model(test_app : AppContext):
#     #Arrange
#     test_simple_model_creation(test_app)
    
#     #Act
#     res = test_app.app.test_client().delete("/Model/Geo")
#     responseJson = json.loads(res.data)

#     #Assert
#     succesful_response_object(responseJson)


