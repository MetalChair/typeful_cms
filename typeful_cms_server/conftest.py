import os
from flask.app import Flask
from flask import g
from flask.ctx import AppContext
import pytest
import psycopg2
import json
from typeful_cms_server.application import init_app
from typeful_cms_server.application.database import scaffold_db

@pytest.fixture
def test_app() -> AppContext:
    print("Initializing app")
    app = init_app()
    app.config.from_file("config_test.json", json.load) #Load the testing config
    with app.app_context() as context:
        g.db = psycopg2.connect("dbname=typeful_test user=typefulserver")
        scaffold_db(g.db)
        yield context
