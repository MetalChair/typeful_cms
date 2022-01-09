import sqlite3
from flask import g
import psycopg2
from typeful_cms_server import config 
DATABASE = "db/typeful.db"
def get_db():
    if 'db' not in g:
        db = g.db = psycopg2.connect("dbname=typeful user=newserver")
        scaffold_db(db)
    return g.db.cursor()

def scaffold_db(db):
    cur = db.cursor()
    with open(config.DB_SCAFFOLD_PATH, 'r') as sql_file:
        sql_script = sql_file.read()
    cur.execute(sql_script)
