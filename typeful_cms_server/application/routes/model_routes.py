from typing import Dict, List, Tuple, Deque
from flask import Blueprint, request, g
from collections import deque
from typeful_cms_server.application.database import *
from typeful_cms_server.application.models.message_reponse import message_response

model_routes_blueprint = Blueprint("model_route_blueprint", __name__)



# def posted_model_to_sql_query(post_data : dict):
#     def to_sql_query_helper(model_name, model, fkey_table_name = None, fkey_col = None):
#         sql_list = []
#         col_list = []
#         col_list.extend([
#             sql.SQL("{uuid_name} UUID GENERATED ALWAYS AS IDENTITY").format(
#                 uuid_name = sql.Identifier(model_name + "_id")
#             ),
#             sql.SQL("PRIMARY KEY ({primary_col_name}").format(
#                 primary_col_name = sql.Identifier(model_name + "_id")
#             )
#         ])
#         if(fkey_table_name is not None and fkey_col is not None):
#             col_list.extend([  
#                 sql.SQL("{fk_col} UUID").format(
#                     fk_col = sql.Identifier(fkey_col)
#                 ),
#                 sql.SQL(
#                     "CONSTRAINT {fk_col} FOREIGN KEY ({fk_col_name}) REFERENCES {fk_table_name}({fk_col_name})"
#                 ).format(
#                     fk_col = sql.Identifier("fk_" + fkey_col),
#                     fk_col_name =  sql.Identifier(fkey_col),
#                     fk_table_name = sql.SQL(fkey_table_name)
#                 )]
#             )
#         for item in model:
#             if type(model.get(item)) is dict:
#                 sql_list.extend(
#                     to_sql_query_helper(
#                         item,
#                         model.get(item), 
#                         model_name,
#                         model_name + "_id"
#                     )
#                 )
#                 print("Is dict")
#             else:
#                 col_list.append(
#                     sql.SQL("{col_name} {col_type}").format(
#                         col_name = sql.Identifier(item),
#                         col_type = sql.SQL(
#                             infer_sql_type(model.get(item)
#                             )
#                         )
#                     )
#                 )
#         separated_query = sql.SQL(",").join(x for x in col_list)
#         final_query = sql.SQL("CREATE TABLE {table_name} ({query_col})").format(
#             table_name = sql.Identifier(model_name),
#             query_col = sql.SQL("").join(x for x in separated_query)
#         )
#         return final_query
#     '''
#         Takes a raw JSON object from a posted model and "flattens" it
#         IE: Turns it into a list of raw sql queries that can be executed
#     '''
#     for model_name in post_data:
#         cur_model = post_data.get(model_name)
#         test = to_sql_query_helper(model_name, cur_model)
#     return col_list

def infer_sql_type(object : any):
    '''
        Takes an object and attempts to cast it to various types,
        returning the corresponding sql column type
    '''
    # try:
    #     as_int = int(object)
    #     if as_int == float(object):
    #         return "INTEGER"
    # except:
    #     pass

    # try:
    #     float(object)
    #     return "REAL"
    # except:
    #     pass #Explicitly pass to ignore conversion

    if type(object) is list:
        return "TEXT ARRAY"

    return "TEXT"


def flatten_json_object(json_object : Dict) -> List[Tuple[str, dict]]:
    '''
    Flattens a json object to a dict of dicts representing the outermost
    object and all of the objects inside the query 
    The order that this is returned in is important
    the first record in the list has to be created first
    '''
    schema_objs = []

    def flatten_json_helper(key: str, json_object : Dict, fkey_table = ""):
        obj_without_nested_dicts = {}
        for inner_schema_key in json_object:
            inner_schema_val = json_object.get(inner_schema_key)
            if type(inner_schema_val) is dict:
                flatten_json_helper(inner_schema_key,inner_schema_val, key)
            else:
                obj_without_nested_dicts[inner_schema_key] = inner_schema_val
        schema_objs.append((key,obj_without_nested_dicts, fkey_table))
    
    for outermost_schema_key in json_object:
        outermost_schema_val = json_object.get(outermost_schema_key)
        flatten_json_helper(outermost_schema_key, outermost_schema_val)
    schema_objs.reverse()
    return schema_objs

def create_tables_from_json_schema(schema_list : List[Tuple[str, dict, str]]):
    '''
    Takes a list of tuples where each tuple is
    <table_name,json_object,foreign_key_table_name>, converts it to a CREATE
    TABLE command, and runs it
    '''
    queries = []
    for (table_name, schema, fk_table) in schema_list:
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
                        col_type = sql.SQL(infer_sql_type(schema_item))
                    )
            )
        query = sql.SQL("CREATE TABLE {table_name} ({create_cols})").format(
            table_name = sql.Identifier(table_name.upper()),
            create_cols = sql.SQL(",").join(x for x in column_creation_lines)
        )
        queries.append(query)
    for query in queries:
        run_query(query)

def insert_records(schema_list : List[Tuple[str, dict, str]]):
    #Tuple[str,int] representing:
    #  <table_name for last created parent record, and int id>
    parent_record_ctxs: Deque[Tuple(str, int)] = deque()
    
    '''
        geo, 3
        address, 2
        users, 1

        if fk_table != stack.top.table_name
    '''

    for (table_name, schema, fk_table) in schema_list:
        while(
            len(parent_record_ctxs) > 0 and
            parent_record_ctxs[0][0] is not fk_table
        ):

            parent_record_ctxs.popleft()
        col_val_map = {}
        if fk_table:
            col_val_map[fk_table + "_id"] = parent_record_ctxs[0][1]
        for key in schema:
            val = schema.get(key)
            if type(val) is not dict:
                if type(val) is list:
                    val = [str(x) for x in val]
                col_val_map[key] = val

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
        print(schema)
    return


@model_routes_blueprint.route("/Model", methods = ["POST", "DELETE", "PATCH"])
def perform_model_action():
    model = request.get_json()
    act_type = DB_ACTION_TYPE.from_post_method(request.method)
    if act_type == DB_ACTION_TYPE.CREATE:
        dict_list = flatten_json_object(model)
        try:
            create_tables_from_json_schema(dict_list)
            insert_records(dict_list)
            res = message_response(True, msg = "Created models and added to db")
            return res.as_dict()
        except Exception as e:
            res = message_response(False, e_msg= str(e))
            return res.as_dict()

# def perform_model_action():
#     model = request.get_json()
#     if is_valid_model(model, act_type):
#         schema_list = posted_model_to_schema_list(model)
#         if act_type is DB_ACTION_TYPE.CREATE:
#             create_model_table(schema_list, model["name"])
#             create_route_table_entry(model["query_name"], model["name"])
#         elif act_type is DB_ACTION_TYPE.UPDATE:
#             update_model_table(schema_list, model["name"])
#         elif act_type is DB_ACTION_TYPE.DELETE:
#             delete_model_table_col(schema_list, model["name"])
#     status = not hasattr(g, "error")
#     return {
#         "actionSucceeded" : status,
#         "errorMessage"    : getattr(g, "error", "")
#     }

# def flatten

# def posted_model_to_schema_list(model : dict) -> List[Tuple[str, str, bool]]:
#     '''
#         Takes the posted JSON model and converts the
#         model_def attribute to a list of tuples
#     '''
#     schema_list = []
#     for schema_item in model["model_def"]:
#         schema_list.append(
#             (
#                 schema_item.get("name"),
#                 schema_item.get("type"),
#                 schema_item.get("nullable")
#             )
#         )
#     return schema_list

# def schema_to_sql_create_query(schema : Tuple[str, str or dict, bool]):
#     '''
#     tuple<model_name, type, nullable>
#     '''
#     schema_list = []
#     for item in schema:
#         if type(item[1]) is dict:
#             if is_valid_model(item[1], DB_ACTION_TYPE.CREATE):
#                 inner_schema_list = posted_model_to_schema_list(item[1])
#                 create_model_table(inner_schema_list, item[1]["name"])
#                 create_route_table_entry(item[1]["query_name"], item[1]["name"])
#             print("Type is dict")
#         else:
#             new_line = get_column_creation_line(item)
#             if new_line is not None:
#                 schema_list.append(new_line)
#     return schema_list

# def create_model_table(schema : Tuple[str, str, bool], table_name: str):
#     schema_list = schema_to_sql_create_query(schema)
#     run_query(sql.SQL(
#         "CREATE TABLE {table_name} ({query_list})"
#         ).format(
#             table_name = sql.Identifier(table_name),
#             query_list = sql.SQL(', ').join(x for x in schema_list)
#         )
#     )

# def update_model_table(schema : Tuple[str, str, bool], table_name: str):
#     schema_list = schema_to_sql_create_query(schema)
#     run_query(sql.SQL(
#         "ALTER TABLE {table_name} {columns}"
#         ).format(
#             table_name = sql.Identifier(table_name),
#             columns = sql.SQL(', ').join(
#                 sql.SQL("ADD COLUMN {cols}")
#                     .format(cols = x) for x in schema_list
#             )
#     ))
# def create_route_table_entry(query_name : str, table_name : str):
#     run_query(
#         "INSERT INTO typeful_routes (query_name, table_name) VALUES (%s,%s)",
#         [query_name, table_name]
#     )


# def delete_model_table_col(schema : Tuple[str, str, bool], table_name: str):
#     run_query(
#         sql.SQL(
#             "ALTER TABLE {table_name} {cols}"
#             ).format(
#                 table_name = sql.Identifier(table_name),
#                 cols = sql.SQL(', ').join(
#                     sql.SQL("DROP COLUMN {cols}")
#                         .format(cols = sql.Identifier(x[0])) for x in schema
#                 )
#             )
#     )

# def is_valid_model(model, type : DB_ACTION_TYPE):
#     '''
#         Validates an order creation model and populates
#         the request context object with any model errors
#     '''
#     if "name" not in model:
#         g.error = "You must specify a model name"
#         return False
#     if "model_def" not in model:
#         g.error = "You must specify a model definition"
#         return False
#     else:
#         if type is DB_ACTION_TYPE.UPDATE or type is DB_ACTION_TYPE.CREATE:
#             for item in model["model_def"]:
#                 if(
#                     "name" not in item or
#                     "type" not in item or
#                     "nullable" not in item
#                 ):
#                     g.error = "Model definitions for create/update must specify a name, type, and nullable field"
#                     return False

#     #Requests for model creation must have a queryable_name
#     if type == DB_ACTION_TYPE.CREATE and "query_name" not in model:
#         g.error = "You must specify a queryable_name for this object"
#         return False

    

#     return True
