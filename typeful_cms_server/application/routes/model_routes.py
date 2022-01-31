from typing import Dict, List, Tuple, Deque
from flask import Blueprint, request, g
from collections import deque

from application.database.database import *
from application.models.message_reponse import message_response
from application.util.psql_reserved_keywords import PSQL_RESERVED_KEYWORDS

model_routes_blueprint = Blueprint("model_route_blueprint", __name__)

def infer_sql_type(object : any):
    '''
        Takes an object and attempts to cast it to various types,
        returning the corresponding sql column type
    '''
    try:
        as_int = int(object)
        if as_int == float(object):
            return "INTEGER"
    except:
        pass

    try:
        float(object)
        return "REAL"
    except:
        pass #Explicitly pass to ignore conversion

    try:
        complex(object)
        return "REAL"
    except:
        pass

    if isinstance(object, list):
        return "TEXT[]"

    return "TEXT"


def flatten_json_object(json_object : Dict) -> List[Tuple[str, dict, str, List[str]]]:
    '''
    Flattens a json object to a dict of dicts representing the outermost
    object and all of the objects inside the query 
    The order that this is returned in is important
    the first record in the list has to be created first
    '''
    schema_objs = []

    def flatten_json_helper(key: str, json_object : Dict, fkey_table = ""):
        obj_without_nested_dicts = {}
        related_tables = []
        for inner_schema_key in json_object:
            inner_schema_val = json_object.get(inner_schema_key)
            if type(inner_schema_val) is dict:
                related_tables.append(inner_schema_key)
                flatten_json_helper(inner_schema_key,inner_schema_val, key)
            else:
                obj_without_nested_dicts[inner_schema_key] = inner_schema_val
        schema_objs.append((key,obj_without_nested_dicts, fkey_table, related_tables))
    
    for outermost_schema_key in json_object:
        outermost_schema_val = json_object.get(outermost_schema_key)
        if type(outermost_schema_val) is list:
            for inner_schema_val in outermost_schema_val:
                flatten_json_helper(outermost_schema_key, inner_schema_val)
        else:
            flatten_json_helper(outermost_schema_key, outermost_schema_val)
    schema_objs.reverse()
    return schema_objs

def create_tables_from_json_schema(schema_list : List[Tuple[str, dict, str]]):
    '''
    Takes a list of tuples where each tuple is
    <table_name,json_object,foreign_key_table_name>, converts it to a CREATE
    TABLE command, and runs it

    Also creates a schema table that specifies public/private fields 
    that the user can use
    '''
    queries = []
    all_tables = get_all_table_names()
    for (table_name, schema, fk_table, related_tables) in schema_list:

        #Ensure the table name isn't already in use
        #Skip if it is
        if table_name.upper() in all_tables:
            continue
        
        #Ensure the table name provided isn't a reserved word
        if table_name.upper() in PSQL_RESERVED_KEYWORDS:
            g.error = "Table name {name} is a reserved keyword".format(
                name = table_name
            )
            raise Exception


        column_creation_lines = []
        #Add foreign key and primary key columns
        column_creation_lines.append(
            sql.SQL("{table_name} SERIAL PRIMARY KEY")
                .format(
                    table_name = sql.Identifier(table_name + "_id")
                )
        )
        if fk_table:
            column_creation_lines.append(
                sql.SQL("{fkey_col_name} INTEGER REFERENCES {fkey_table} ({fkey_col_name})")
                    .format(
                        fkey_col_name = sql.Identifier(fk_table + "_id"),
                        fkey_table = sql.Identifier(fk_table.upper())
                    )
            )
        for schema_item in schema:
            column_creation_lines.append(
                sql.SQL("{col_name} {col_type}")
                    .format(
                        col_name = sql.Identifier(schema_item),
                        col_type = sql.SQL(
                            infer_sql_type(schema.get(schema_item)
                        ))
                    )
            )
        query = sql.SQL("CREATE TABLE {table_name} ({create_cols})").format(
            table_name = sql.Identifier(table_name.upper()),
            create_cols = sql.SQL(",").join(x for x in column_creation_lines)
        )
        queries.append((query, []))

        #Create a query that will create a schema attrib entry
        attrib_query = sql.SQL(
                "INSERT INTO attribs.\"SCHEMA_ATTRIBS\"(table_name, associated_tables)" +
                "VALUES (%s, %s) RETURNING id"  
        )
        #We have to run this first so we can get the PK out and create the FK
        #reference in the privacy column
        cur = run_query(attrib_query, [table_name.upper(), related_tables])

        id = cur.fetchone()[0]

        privacy_query = sql.SQL(
            "INSERT INTO attribs.\"SCHEMA_PRIVACY\"" +
            "(role_name, accesible_fields, attrib_table_id)" +
            "VALUES (%s, %s, %s)"
        )
        queries.append((privacy_query, ["public",list(schema.keys()), id]))

        all_tables.append(table_name.upper())
    run_queries(queries)

def insert_records(schema_list : List[Tuple[str, dict, str]]):

    '''
        Takes a list of schema options containing a definition for records
        and inserts them into the corresponding tables
    '''

    """
        This is a bit confusing. We've created a list of schemas from a json
        object where the first element in the list is the outermost object. The
        goal here is to insert the outermost object first so we can retrieve a
        Foreign Key from it. But we can have nested, objects IE:
            "users": {
                "name: {...}
                "address" : { ..., "coordinates" : {}, ...}
                "company" : {...}
            }
        The naive approach would be to just keep track of the inserted FK record
        as we loop through all the schemas. This causes a problem in this
        instance, however, because coordinates should have an FK value of an
        addresss record, but company should still refer to a user record.

        To solve this, we make a note of the last fk record for each context in
        a queue and pop from it till we find the most recently created FK for
        our intended parent table

        IE:
            After user creation:
                QUEUE: {(users, FK_NUM)}
            After address creation
                QUEUE: {(address, FK_NUM)(users,FK_NUM)}
            
            Coordinates would then be created by pulling the FK off of the
            record on top of the queue. After which, the creation of a
            coordinates object, we will pop items off the top of the queue until
            we find an entry where the string matches the fk_table name value
    """

    # A queue consisting of tuples[table_name, foreign_key_int]
    parent_record_ctxs: Deque[Tuple(str, int)] = deque()


    for (table_name, schema, fk_table, _) in schema_list:
        #Find the first context on our context stack that matches the current
        #table.
        while(
            len(parent_record_ctxs) > 0 and
            parent_record_ctxs[0][0] is not fk_table
        ):
            parent_record_ctxs.popleft()
        
        #Create a map of all our values
        col_val_map = {}

        #Map the foreign column id value
        if fk_table:
            col_val_map[fk_table + "_id"] = parent_record_ctxs[0][1]

        for key in schema:
            val = schema.get(key)
            if type(val) is not dict:
                if type(val) is list:
                    val = [str(x) for x in val]
                col_val_map[key] = val
        try:
            cur = run_query(
                sql.SQL("INSERT INTO {table_name}({cols}) VALUES ({vals}) RETURNING {id} ")
                .format(
                    table_name = sql.Identifier(table_name.upper()),
                    cols = sql.SQL(", ").join(
                            sql.Identifier(x) for x in col_val_map.keys()
                        ),
                    vals = sql.SQL(", ").join(
                        sql.Literal(col_val_map[x]) for x in col_val_map.keys()
                    ),
                    id = sql.Identifier(table_name + "_id")
                )
            )
            inserted_id = cur.fetchone()[0]
            if inserted_id:
                parent_record_ctxs.appendleft(
                    (table_name, inserted_id)
                )
        except Exception as e:
            raise e
    return

def update_record(update_model : Dict[str, dict], update_action : str):
    for (table_action, table_val) in update_model.items():
        if update_action == "add":
            column_list : Dict[str, str] = table_val.get("columns")
            query = sql.SQL("ALTER TABLE {table_name} {add_clauses}").format(
                    table_name = sql.Identifier(table_action.upper()),
                    add_clauses = sql.SQL(", ").join(
                        sql.SQL("ADD {col_name} {col_type}").format(
                            col_name = sql.Identifier(name),
                            col_type = sql.SQL(infer_sql_type(col_type))
                        ) for (name, col_type) in column_list.items()
                    )
                )
            cur = run_query(query)
        elif update_action == "drop":
            column_list : Dict[str, str] = table_val.get("columns")
            query = sql.SQL("ALTER TABLE {table_name} {add_clauses}").format(
                    table_name = sql.Identifier(table_action.upper()),
                    add_clauses = sql.SQL(", ").join(
                        sql.SQL("DROP {col_name}").format(
                            col_name = sql.Identifier(name),
                        ) for name in column_list
                    )
                )
            cur = run_query(query)
        elif update_action == "update":
            #Get affiliated tables 
            set_params : Dict = table_val.get("set")
            where_params : Dict = table_val.get("where")
            query = sql.SQL(
                "UPDATE {table_name} SET {set_clauses} WHERE {where_clauses}"
            ).format(
                table_name =  sql.Identifier(table_action.upper()),
                set_clauses = sql.SQL(", ").join(
                    sql.SQL("{col_name} = {placeholder}")
                        .format(
                            col_name = sql.Identifier(x),
                            placeholder = sql.Placeholder()
                    ) for x in set_params
                ),
                where_clauses = sql.SQL(", ").join(
                    sql.SQL("{col_name} = {placeholder}")
                        .format(
                            col_name = sql.Identifier(x),
                            placeholder = sql.Placeholder()
                    ) for x in where_params
                )
            )
            cur = run_query(
                query, 
                list(set_params.values()) + list(where_params.values())
            )
    return

def drop_table(table_name : str):
    query = sql.SQL("DROP TABLE {table_name}").format(
        table_name = sql.Identifier(table_name.upper())
    )
    run_query(query)


@model_routes_blueprint.route("/Model", methods = ["POST", "PATCH"])
def perform_model_action():
    model = request.get_json()
    act_type = DB_ACTION_TYPE.from_post_method(request.method)
    response_object = message_response(False, e_msg= "Unknown action in submission")
    try:
        if act_type == DB_ACTION_TYPE.CREATE:
                dict_list = flatten_json_object(model)
                create_tables_from_json_schema(dict_list)
                insert_records(dict_list)
                response_object = message_response(True, msg = "Created models and added to db")
        if act_type == DB_ACTION_TYPE.UPDATE:
            if len(model) > 1:
                response_object = message_response(False, e_msg = "Update queries must contain one and only one action")
            else:
                for action_item in model:
                    response_object = message_response(True, msg = "Action succeeded")
                    update_record(model.get(action_item), action_item)
        return response_object.as_dict()
    except Exception as e:
        response_object = message_response(False, e_msg= getattr(g, "error", "Unknown Error"))
        return response_object.as_dict()

@model_routes_blueprint.route("/Model/<table_name>", methods = ["DELETE"])
def perform_delete_action(table_name):
    response_object = message_response(False, e_msg= "Unknown action in submission")
    try:
        drop_table(table_name)
        response_object = message_response(True, msg = "Table deleted")
        return response_object.as_dict()
    except Exception:
        response_object = message_response(False, e_msg= getattr(g, "error", "Unkown Error"))
        return response_object.as_dict()

    
