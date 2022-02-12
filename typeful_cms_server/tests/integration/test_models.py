from io import BytesIO
import os
from pickle import TRUE
from typing import List
from flask import json
from flask.ctx import AppContext
from psycopg2 import sql

from application.database.database import get_db, get_db_cursor, run_query
from tests.helpers import *

TEST_FILE_NAMES = [
    "Test.svg",
    "Test2.svg"
]

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
                    "lat": -37.3159,
                    "lng": 81.1496
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
    ]
}

SAMPLE_DROP_SINGLE_DATA = {
    "drop": {
        "users" : {
            "columns" :[
                "favorite_number",
            ]
        }
    }
}

SAMPLE_DROP_MANY_DATA = {
    "drop": {
        "users" : {
            "columns" :[
                "favorite_number",
                "name"
            ]
        }
    }
}

SAMPLE_ADD_SINGLE_DATA = {
    "add": {
        "users": {
            "columns" :{
                "likes_pretzels" : True
            }
        }
    }
}

SAMPLE_ADD_MANY_DATA = {
    "add": {
        "users": {
            "columns" :{
                "likes_pretzels" : True,
                "likes_cracker_jacks" : ""
            }
        }
    }
}


EXPECTED_COL_TYPE_IDS = {
    "users_int_id" : 23,
    "aliases" : 1009,
    "email" : 25,
    "favorite_number" : 700,
    "id" : 23,
    "name" : 25,
    "phone" : 25,
    "username" : 25,
    "website" : 25,
    "users_ext_id" : 2950
}



def test_model_creation(test_app : AppContext):
    #Arrange
    
    #Act
    res = test_app.app.test_client().post("/Model", json = SAMPLE_CREATION_POST_DATA)
    
    #Assert
    responseJson = json.loads(res.data)
    succesful_response_object(responseJson)
    cols_exist_on_table("users",["id","name","favorite_number"])

def test_delete_single_column(test_app : AppContext):
    #Arrange
    test_model_creation(test_app)
    res = test_app.app.test_client().patch("/Model", json = SAMPLE_DROP_SINGLE_DATA)
    succesful_response_object(json.loads(res.data))
    cols_dont_exist_on_table("users", ["favorite_number"])
    cols_exist_on_table(
        "users", ["name", "username", "email", "aliases", "phone", "website"])


def test_add_single_column(test_app):
    #arrange
    test_model_creation(test_app)

    #act
    res = test_app.app.test_client().patch("/Model", json = SAMPLE_ADD_SINGLE_DATA)
    succesful_response_object(json.loads(res.data))
    #assert
    cols_exist_on_table("users", ["likes_pretzels"])


def test_add_many_column(test_app):
    #arrange
    test_model_creation(test_app)

    #act
    res = test_app.app.test_client().patch("/Model", json = SAMPLE_ADD_MANY_DATA)

    #assert
    succesful_response_object(json.loads(res.data))
    cols_exist_on_table("users", ["likes_pretzels", "likes_cracker_jacks"])


def test_delete_many_column(test_app):
    #arrange
    test_model_creation(test_app)

    #act
    res = test_app.app.test_client().patch("/Model", json = SAMPLE_DROP_MANY_DATA)
    
    #assert
    cols_dont_exist_on_table("USERS", ["name", "favorite_number"])

def test_media_upload(test_app : AppContext):
    test_model_creation(test_app)
    files = [open(os.path.dirname(__file__)+ "/" + fpath, 'rb') for fpath in TEST_FILE_NAMES]

    data =  {}
    data["files[]"] = [file for file in files]
    res = test_app.app.test_client().post(
        "/Model/Media", 
        data = data, 
        content_type = 'multipart/form-data'    
    )
    succesful_response_object(json.loads(res.data))
    cur = run_query("SELECT * FROM public.media")
    assert cur.rowcount == 2

def test_media_attach():
    return

def test_typings_on_creation(test_app):
    #arrange
    test_model_creation(test_app)

    #act
    cur = get_db_cursor()
    cur.execute("SELECT * FROM public.\"users\"")

    #assert
    for col in cur.description:
        assert col.type_code == EXPECTED_COL_TYPE_IDS[col.name]
    return

