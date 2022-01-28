from collections import deque
from typing import Deque, List
from flask import Blueprint, request, g
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

def get_fields_accessible_to_tier(tier: str, table_name: str) -> List:
    privacy_table_name = table_name + "_PRIVACY"
    privacy_query = sql.SQL(
        "SELECT {credential_tier} FROM {table_name}"
    ).format(
        credential_tier = sql.Identifier(tier),
        table_name = sql.Identifier(privacy_table_name)
    )
    try:
        cur = run_query(privacy_query)
        return list(cur.fetchone()[0])
    except Exception as e:
        g.error = "Unable to run this query"
        raise e


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
            
def parse_query_string(query_string : bytes, encoding : str) -> List[Tuple[str, str, str]]:
    as_string = query_string.decode(encoding)
    split_arr = as_string.split("&")
    query_params_list = []
    #TODO: Find a way to parse query strings that contain equality characters
    #TODO: Beat this up for parsing
    for query_item in split_arr:
        (found_operator, _) = find_operator_in_query_string(query_item)
        query_params_list.append(
            query_item.partition(found_operator)
        )
    return query_params_list

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


@row_routes_blueprint.route("/<table_name>", methods = ["GET"])
def perform_row_action(table_name : str):
    table_name = table_name.upper()
    #Get the credentials and fields that said credential can query
    credential_tier = get_api_credential_tier()
    fields = get_fields_accessible_to_tier(credential_tier, table_name)
    #fields.extend(EXTRA_VALID_FIELDS)
    #TODO: Extract extra sql verbiage
    parsed_query = parse_query_string(request.query_string, request.charset)

    parsed_query = list(filter(lambda x : x[0] in fields, parsed_query))
    sql_query = form_sql_from_query_list(parsed_query, fields, table_name)
    
    query_vals = [x[2] for x in parsed_query]

    cur = run_query(sql_query, query_vals)
    rows = cur.fetchmany(10)
    mapped_results = map_results_to_dict(rows, cur.description)
    #Form the query
    return