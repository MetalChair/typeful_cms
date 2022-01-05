from flask import json
from flask.app import Flask
from flask.ctx import AppContext
import pytest
def test_string_model_creation(test_app : AppContext):
    post_data = {
        "name": "test_string",
        "model_def" : [
            {"my_cool_string" : "string"}
        ]
    }
    res = test_app.app.test_client().post("/Create", json = post_data)
    '''Testing model creation with a simple string data type'''
    assert res.data == b"<b>TODO: IMPLEMENT</b>"