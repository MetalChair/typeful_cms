from os import confstr
import pytest
from flask.app import Flask

from typeful_cms_server.application.database import get_db

def test_did_db_scaffold(test_app : Flask):
    '''Was the DB properly scaffolded on app creation?'''
    with test_app:
        db  = get_db()
        tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        assert len(tables) == 2