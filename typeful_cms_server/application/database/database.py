import enum
import psycopg2
from typing import Tuple
from flask import g
from psycopg2 import sql
from application import config


DATABASE = "db/typeful.db"
VALID_DB_TYPES = ["TEXT", "DATE", "JSON", "BOOLEAN", "UUID", "INTEGER"]
class DB_ACTION_TYPE(enum.Enum):
    CREATE = 1
    UPDATE = 2
    DELETE = 3
    def from_post_method(method : str):
        if method == "POST":
            return DB_ACTION_TYPE.CREATE
        elif method == "PATCH":
            return DB_ACTION_TYPE.UPDATE
        elif method == "DELETE":
            return DB_ACTION_TYPE.DELETE

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
    with open(config.DB_SCAFFOLD_PATH, 'r') as sql_file:
        sql_script = sql_file.read()
    db.cursor().execute(sql_script)
    db.autocommit = False

def run_queries(list_of_queries):
    '''
    Runs a list of queries of format (query, list_of_params). 
    Batches the query by running them all on a single cursor before committing
    '''
    try:
        cursor = get_db_cursor()
        db = get_db()
        for (query, params) in list_of_queries:
            cursor.execute(query, params)
        db.commit()
    except Exception as e:
        db.rollback()
        print("An error occurred ", e)
        if not hasattr(g, "error"):
            g.error = "An error occurred while running the db query {}".format(e)
        raise e


def run_query(sql_query, params = []):
    try:
        '''Runs the query and throws an exception if an error occurs '''
        db = get_db()
        cur = get_db_cursor()
        as_string = sql_query.as_string(cur)
        cur.execute(sql_query, params)
        db.commit()
        return cur
    except Exception as e:
        db.rollback()
        print("An error occurred ", e)
        if not hasattr(g, "error"):
            g.error = "An error occurred while running the db query {}".format(e)
        raise e



def get_all_table_names():
    '''
    Gets all the names of the current tables in the typeful_db
    '''
    cur = run_query(
        sql.SQL(
            "SELECT table_name from information_schema.tables WHERE " +
            "table_schema = 'public' AND table_type = 'BASE TABLE'"
        )
    )
    return [x[0] for x in cur.fetchall()]

def get_associated_tables(table_name):
    '''
    Gets all the tables associated with table_name
    '''
    run_query(
        "SELECT associated_tables FROM attribs.\"SCHEMA_ATTRIBS\"" +
        " WHERE table_name = %s",
        table_name
    ).fetchone()[0]


