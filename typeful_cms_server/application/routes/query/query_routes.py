from ast import Str, operator
from collections import deque
from ntpath import join
from typing import Deque, List
from xml.etree.ElementInclude import include
from attr import attr
from flask import Blueprint, request, g
from matplotlib.pyplot import table
from pandas import read_sql_query
from pytest import param
from sympy import false, true
from application.database.database import *
from application.models.message_reponse import message_response

row_routes_blueprint = Blueprint("row_route_blueprint", __name__)

VALID_EQUALITY_CHARS = [
    "<>",
    ">=",
    "<=",
    "<",
    ">",
    "="
]

EXTRA_VALID_FIELDS = [
    "offset"
]

def get_api_credential_tier():
    return "public"


def find_operator_in_query_string(
        query_string: str) -> Tuple[str, int]:
    '''
        Finds the first instance of a valid equality operator
        in the query string. Takes a paremeter 'backticked' indicating
        if this function should look for equality operators that 
        are surrounded in backticks
        
        Returns:
            Tuple(found_operator, index_of_operator)

        Except:
            Raises an exception if no operators are found
    '''
    found_operator = ""
    operator_pos = 9999999
    for operator in VALID_EQUALITY_CHARS:
        operator_query = query_string.find(operator)
        if operator_query < operator_pos and operator_query >= 0:
            operator_pos = query_string.find(operator)
            found_operator = operator

    if not found_operator:
        raise Exception   

    return (found_operator, operator_pos)     


            
def parse_query_string(query_string : bytes, encoding : str) -> Tuple[List[Tuple[str, str, str]], List[str]]:
    '''
    Parses a query string and returns a tuple of format:
    List of tuples(param_name, equality_operator, value)
    List of tables to include in result
    '''
    as_string = query_string.decode(encoding)
    split_arr = as_string.split("&")
    includes_list = []
    query_params_list = []
    #TODO: Find a way to parse query strings that contain equality characters
    #TODO: Beat this up for parsing
    for query_item in split_arr:
        if(query_item.startswith("includes")):
            includes_list = [x for x in query_item.split("=")[1].split(",")]
        else:
            (found_operator, _) = find_operator_in_query_string(query_item)
            query_params_list.append(
                query_item.partition(found_operator)
            )
    return (query_params_list, includes_list)


def schemify_query_result(cursor: Cursor, table_name : str, attribs : Dict[str, Dict[str, str]]):

    '''
        Takes a cursor that has performed a query and the list of all
        tables queries and "reschemifies" it. When querying with sql and
        joining, the object comes back flattened:

        "test" : {
            "hello":{
                "goodbye" : "!"
            }
        }

        would return as a flat list. The query run from form_query aliases all
        returned sql columns of the format <table_name>_<col_name>. In this
        call, we use this information and a list of all the tables queried to
        form a new nested dict object
    '''
    query_result = cursor.fetchall()
    dict_to_return = {
        table_name : []
    }
    for result in query_result:
        new_dict_item = {}
        for prop, desc in zip(result, cursor.description):
            #We need to sort the table names by descending length
            #this prevents an issue where an incorrect match could occur
            #IE. Table named java and javascript, query on java
            sorted_table_names = list(attribs.keys())
            sorted_table_names.sort(key = len, reverse=True)
            for name in sorted_table_names:
                if desc.name.startswith(name):
                    if name not in new_dict_item:
                        new_dict_item[name] = {}
                    prop_name = desc.name[len(name) + 1 :]
                    new_dict_item[name][prop_name] = prop
                    break
        #Now, join the objects on parent tables
        for obj_table_name, obj in new_dict_item.items():
            if ("parent_table" in attribs[obj_table_name] and 
                attribs[obj_table_name]["parent_table"]):
                new_dict_item[attribs[obj_table_name]["parent_table"]][obj_table_name] = obj
        dict_to_return[table_name].append(new_dict_item[table_name])

    return dict_to_return

def form_query(
    table_name: str, 
    query_clauses : List[Tuple[str, str, str]], 
    attribs : Dict[str, Dict[str, str or List[Str]]], 
    includes : List[str]):
    '''
        Takes a table_name to be queried, a list of where clauses of the form
        (field, equality_op, value), a list of tables to include, and 
        an attribute dictionary where the format is:
        
        {
            table_name: {
                accesible_fields: [...]
                parent_table: "..."
            }
        }

        Forms a valid sql query that can be executed
    '''
    
    #Get all the fields to be queried
    to_query_fields = []
    alias = 0
    for attribs_table_name, properties in attribs.items():
        properties["alias"] = "t" + str(alias)
        if "accesible_fields" in properties:
            to_query_fields.extend(
                (properties["alias"], x, attribs_table_name) 
                for x in properties["accesible_fields"]
            )
        alias = alias + 1

    join_clauses = []
    for table in includes:
        if "parent_table" in attribs[table]:
            child_alias = attribs[table]["alias"]
            parent_table = attribs[table]["parent_table"]
            parent_alias = attribs[parent_table]["alias"]
            join_clauses.append(
                sql.SQL(
                    "JOIN public.{table_name} {child_alias} " +
                    "ON {parent_alias}.{parent_join_clause} = {child_alias}.{child_join_clause}"
                ).format(
                    table_name = sql.Identifier(table),
                    parent_join_clause = sql.Identifier(parent_table + "_int_id"),
                    child_join_clause = sql.Identifier(
                        (parent_table + "_int_id")
                    ),
                    parent_alias = sql.SQL(parent_alias),
                    child_alias = sql.SQL(child_alias)
                )
            )
        else:
            raise Exception("No parent table found for includes table")

    sorted_col_name = includes + [table_name]
    sorted_col_name.sort(key = len, reverse=True)
    aliased_wheres = []
    #alias where cluauses
    for col_name, operator, val in query_clauses:
        for name in sorted_col_name:
            if col_name.startswith(name):
                #Find a matching col_name
                alias = attribs[name]["alias"]
                #Alias it
                aliased_wheres.append(
                    (
                        alias, 
                        col_name[len(name) + 1: ],
                        operator,
                        val
                    )
                )
                break
    query = sql.SQL(
        "SELECT {accesible_fields} FROM {table_name} {table_alias} {join_clauses} WHERE {where_clauses}"
        ).format(
        accesible_fields = sql.SQL(", ").join(
            sql.SQL("{table_alias}.{col_name} AS {alias}").format(
                table_alias = sql.SQL(x),
                col_name = sql.Identifier(y),
                alias = sql.Identifier((z + "_" + y))
            ) for x, y, z in to_query_fields),
        table_name = sql.Identifier(table_name),
        join_clauses = sql.SQL("").join(x for x in join_clauses),
        table_alias = sql.SQL(attribs[table_name]["alias"]),
        where_clauses = sql.SQL(" AND ").join(
            sql.SQL("{alias}.{column_name} {eq} {value}").format(
                alias = sql.SQL(alias),
                column_name = sql.Identifier(col_name),
                eq = sql.SQL(operator),
                value = sql.Placeholder()
            ) for alias, col_name, operator, val in aliased_wheres
        )
    )
    as_string = query.as_string(get_db_cursor())

    return (query, [x[3] for x in aliased_wheres])

@row_routes_blueprint.route("/<table_name>", methods = ["GET"])
def run_posted_query(table_name : str):
    #Get the credentials and fields that said credential can query
    credential_tier = get_api_credential_tier()
    query_clauses, includes = parse_query_string(
        request.query_string, request.charset)
    all_tables = [*includes, table_name]
    #Explicitly include the queried table in includes
    field_attribs = get_table_attribs(all_tables, credential_tier)
    query, params = form_query(table_name, query_clauses, field_attribs, includes)
    response = message_response(status=True)
    try:
        cursor = run_query(query, params)
        # as_dict = query_to_dict(cursor)
        as_schema = schemify_query_result(cursor, table_name, field_attribs)
        response.result = as_schema
    except Exception as e:
        response.status = False
        response.error = str(e)
        
    #Form the query
    return response.as_dict()