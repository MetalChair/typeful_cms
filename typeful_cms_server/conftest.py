import os
from flask.app import Flask
from flask import g
from flask.ctx import AppContext
import pytest
import sqlite3
import json
from typeful_cms_server.application import init_app
from typeful_cms_server.application.database import scaffold_db

@pytest.fixture
def test_app() -> AppContext:
    print("Initializing app")
    app = init_app()
    app.config.from_file("config_test.json", json.load) #Load the testing config
    with app.app_context() as context:
        g.db = sqlite3.connect("db/testing.db")
        scaffold_db(g.db)
        yield context
    #After the test has executed, remove the testing db
    os.remove("db/testing.db")
