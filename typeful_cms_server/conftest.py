import os
from sys import implementation
from flask.app import Flask
from flask import g
from flask.ctx import AppContext
import pytest
import psycopg2
import json
from application import init_app
from application.database.database import get_db, get_db_cursor, scaffold_db
from application.config import TEST_CONFIG_PATH

@pytest.fixture
def test_app() -> AppContext:
    print("Initializing app")
    app = init_app()
    app.config.from_file(TEST_CONFIG_PATH, json.load) #Load the testing config
    with app.app_context() as context:
        g.db = psycopg2.connect("dbname=typeful_test user=typefulserver")
        scaffold_db(g.db)
        yield context

        
