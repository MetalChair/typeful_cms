import sqlite3
from sqlite3.dbapi2 import Connection
from flask import g
from typeful_cms_server import config 
DATABASE = "db/typeful.db"
def get_db():
    if 'db' not in g:
        db = g.db = sqlite3.connect(DATABASE)
        scaffold_db(db)
    return g.db

def scaffold_db(database : Connection):
    with open(config.DB_SCAFFOLD_PATH, 'r') as sql_file:
        sql_script = sql_file.read()
    database.executescript(sql_script)
    database.commit()
