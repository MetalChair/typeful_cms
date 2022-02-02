import enum
from sqlite3 import Cursor
import psycopg2
from typing import Dict, List, Tuple
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

def get_table_attribs(table_name : str):
    try:
        cur = run_query(
            "SELECT * FROM attribs.\"SCHEMA_ATTRIBS\" WHERE table_name = %s LIMIT 1",
            [table_name]
        )
        row = cur.fetchone()
        attrib_dict = {}
        for description, value in zip(cur.description, row):
            attrib_dict[description.name] = value
        return attrib_dict
            
    except Exception as e:
        print("An error occurred while fetching table attribs")

def query_to_dict(cursor : Cursor):
    query_result = cursor.fetchall()
    dict_to_return = {}
    dict_to_return["result"] = []
    for result in query_result:
        new_dict_item = {}
        for prop, desc in zip(result, cursor.description):
            new_dict_item[desc.name] = prop
        dict_to_return["result"].append(new_dict_item)

    return dict_to_return

def get_table_attribs(tables : List[str], role : str) -> Dict[str, Dict[str, str]]:
    '''
    Performs a query to get attributes and privacy informaiton
    for the provided tables given the user is of the provided role
    '''
    query = (
        "SELECT accesible_fields, table_name, parent_table from " +
        "attribs.\"SCHEMA_PRIVACY\" a inner join attribs.\"SCHEMA_ATTRIBS\" b " +
        "ON b.id = a.attrib_table_id where role_name = %s and table_name = ANY(ARRAY[%s])"
    )
    cursor = run_query(query, [role, tables])
    attribs = cursor.fetchall()
    table_attribs = {}
    for returned_row in attribs:
        table_attribs[returned_row[1]] = {
            "accesible_fields" : returned_row[0],
            "parent_table" : returned_row[2]
        } 
    return table_attribs


