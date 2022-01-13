import sqlite3
from typing import Tuple
from flask import g
import psycopg2
from psycopg2 import sql
from typeful_cms_server import config 


DATABASE = "db/typeful.db"
VALID_DB_TYPES = ["TEXT", "DATE", "JSON", "BOOLEAN", "UUID", "INTEGER"]

def get_db():
    if 'db' not in g:
        db = g.db = psycopg2.connect("dbname=typeful user=typefulserver")
        scaffold_db(db)
    return g.db

def get_db_cursor():
    if 'db' not in g:
        db = g.db = psycopg2.connect("dbname=typeful user=typefulserver")
        scaffold_db(db)
    return g.db.cursor()

def scaffold_db(db):
    db.autocommit = True
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM app_definition WHERE item_key = 'APP_INIT'"
        )
        app_init_exists = cur.fetchall()
        #If we have the app_init record,
        if(len(app_init_exists) > 0):
            return
    except:
        print("Tables don't exist")
        #Determine if the record for app_init exists already
        with open(config.DB_SCAFFOLD_PATH, 'r') as sql_file:
            sql_script = sql_file.read()
        cur.execute(sql_script)

    db.autocommit = False

def create_model_database(schema : Tuple[str, str, bool], table_name: str):
    '''
        Takes a list of tuples <name, type, nullable?> and a table name and
        creates a table in the db with that schema
    '''
    db = get_db()
    cur = get_db_cursor()
    schema_list = []
    param_list = []
    for item in schema:
        new_line = get_column_creation_line(item)
        if new_line is not None:
            schema_list.append(new_line)
    create_table_model = sql.SQL(
        "CREATE TABLE {table_name} ({query_list})"
        ).format(
            table_name = sql.Identifier(table_name),
            query_list = sql.SQL(', ').join(x for x in schema_list)
        )
    test = create_table_model.as_string(cur)
    cur.execute(test)
    db.commit()




def get_column_creation_line(schema : Tuple[str, str, bool]):
    '''
Takes a schema tuple[str, str, bool] and returns a line of sql that will create
the column in an insert query
    '''
    if schema[1].upper() in VALID_DB_TYPES:
        if schema[2]:
            return sql.SQL("{field_name} {type}").format(
                field_name = sql.Identifier(schema[0]),
                type = sql.SQL(schema[1])
            )
        else:
            return sql.SQL("{field_name} {type} NOT NULL").format(
                field_name = sql.Identifier(schema[0]),
                type = sql.SQL(schema[1])
            )
    return None

