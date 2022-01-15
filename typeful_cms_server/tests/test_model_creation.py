from typing import List
from flask import json
from flask.ctx import AppContext
from typeful_cms_server.application.database import get_db, get_db_cursor

SAMPLE_CREATION_POST_DATA = {
    "name": "test_model",
    "model_def" : [
        {
            "name" :"my_cool_string",
            "type" : "text",
            "nullable" : False

        },
        {
            "name" : "my_cool_int",
            "type" : "integer",
            "nullable" : True
        }
    ]
}

SAMPLE_UPDATE_POST_DATA = {
    "name": "test_model",
    "model_def" : [
        {
            "name" :"my_other_cool_string",
            "type" : "text",
            "nullable" : False
        },
        {
            "name" : "my_other_cool_int",
            "type" : "integer",
            "nullable" : True
        }
    ]
}
def test_simple_model_creation(test_app : AppContext):

    res = test_app.app.test_client().post("/Create", json = SAMPLE_CREATION_POST_DATA)
    '''Testing model creation with a simple string data type'''
    responseJson = json.loads(res.data)
    assert "actionSucceeded" in responseJson
    assert "errorMessage" in responseJson
    assert responseJson["actionSucceeded"] == True
    assert responseJson["errorMessage"] == ""
    validate_columns_exist_on_table("test_model",["my_cool_string", "my_cool_int"])


def test_add_to_model(test_app : AppContext):
    test_app.app.test_client().post("/Create", json = SAMPLE_CREATION_POST_DATA)
    test_app.app.test_client().patch("/Add", json = SAMPLE_UPDATE_POST_DATA)
    validate_columns_exist_on_table("test_model",["my_other_cool_string", "my_other_cool_int"])
    return

def validate_columns_exist_on_table(table_name: str, col_names : List[str]):
    cur = get_db_cursor()
    for col_name in col_names:
        cur.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name=%s and column_name=%s;",
            [table_name, col_name]
        )
        assert cur.rowcount > 0, "Column {col_name} was not created in {table}".format(
            col_name = col_name,
            table = table_name
        )
    return