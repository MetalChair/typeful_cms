from os import curdir, truncate
import sqlite3
import enum
import psycopg2
from typing import Tuple
from flask import g
from psycopg2 import sql
from werkzeug.wrappers import request
from typeful_cms_server import config


DATABASE = "db/typeful.db"
VALID_DB_TYPES = ["TEXT", "DATE", "JSON", "BOOLEAN", "UUID", "INTEGER"]
class DB_ACTION_TYPE(enum.Enum):
    CREATE = 1
    UPDATE = 2

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

def perform_db_model_action(
    action : DB_ACTION_TYPE, schema : Tuple[str, str, bool], table_name: str):
    db = get_db()
    cur = get_db_cursor()
    try:
        schema_list = []
        for item in schema:
            new_line = get_column_creation_line(item)
            if new_line is not None:
                schema_list.append(new_line)
        if action is action.CREATE:
            create_table_model = sql.SQL(
            "CREATE TABLE {table_name} ({query_list})"
            ).format(
                table_name = sql.Identifier(table_name),
                query_list = sql.SQL(', ').join(x for x in schema_list)
            )
            cur.execute(create_table_model)
        elif action is action.UPDATE:
            update_table_model = sql.SQL(
                "ALTER TABLE {table_name} {columns}"
            ).format(
                table_name = sql.Identifier(table_name),
                columns = sql.SQL(', ').join(
                    sql.SQL("ADD COLUMN {cols}")
                        .format(cols = x) for x in schema_list
                )
            )
            cur.execute(update_table_model)
        db.commit()
        return True
    except Exception as e:
        print("An error occurred ", e)
        if not hasattr(g, "error"):
            g.error = "An error occured during DB creation"
        return False

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
    g.error = ("Type {} is not a valid SQL type".format(schema[1]))
    raise Exception("Type {} is not a valid SQL type".format(schema[1]))

