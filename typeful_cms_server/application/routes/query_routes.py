from ast import Str
from collections import deque
from typing import Deque, List
from flask import Blueprint, request, g
from matplotlib.pyplot import table
from pandas import read_sql_query
from application.database.database import *

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
            includes_list = [x.upper() for x in query_item.split("=")[1].split(",")]
        else:
            (found_operator, _) = find_operator_in_query_string(query_item)
            query_params_list.append(
                query_item.partition(found_operator)
            )
    return (query_params_list, includes_list)

def form_sql_from_query_list(
        list_of_query_tuples : List[Tuple[str, str, str]],
        fields : List[str],
        table_name : str
    ) -> sql.SQL:

    where_clause = sql.SQL(",").join(
        sql.SQL("{col_name} {operator} {col_val}").format(
            col_name = sql.Identifier(x[0]),
            operator = sql.SQL(x[1]),
            col_val = sql.Placeholder()
        ) for x in list_of_query_tuples
    )

    query = sql.SQL(
        "SELECT {query_cols} FROM " + 
        "{table_name} WHERE {where_clause}"
    ).format(
        query_cols = sql.SQL(",").join(sql.Identifier(x) for x in fields),
        table_name = sql.Identifier(table_name),
        where_clause = where_clause
    )

    return query

def map_results_to_dict(res_list : List, col_descriptors):
    mapped_object_list = []
    for result in res_list:
        current_obj = {}
        for field, name in zip(result, col_descriptors):
            current_obj[name[0]] = field
        mapped_object_list.append(current_obj)
    return mapped_object_list

def form_query(table_name: str, query_clauses : List[Tuple[str, str, str]], 
    attribs : Dict[str, Dict[str, str or List[Str]]]):
    query = sql.SQL("SELECT {accesible_fields} FROM {table_name} {join_clauses}")


    return

@row_routes_blueprint.route("/<table_name>", methods = ["GET"])
def run_posted_query(table_name : str):
    table_name = table_name.upper()
    #Get the credentials and fields that said credential can query
    credential_tier = get_api_credential_tier()
    query_clauses, includes = parse_query_string(
        request.query_string, request.charset)
    #Explicitly include the queried table in includes
    field_attribs = get_table_attribs([*includes, table_name] , credential_tier)
    #Form the query
    return