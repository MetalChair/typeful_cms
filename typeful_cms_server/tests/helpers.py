from typeful_cms_server.application.database import get_db, get_db_cursor
from typing import List
from psycopg2 import sql

def table_contains_record(table_name : str, 
    table_cols : List[str], table_vals : List[str]):
    cur = get_db_cursor()
    where_clauses = []
    for where_clause in zip(table_cols, table_vals):
        where_clauses.append(
            sql.SQL("{col_name} = {col_val}")
                .format(
                    col_name = sql.Identifier(where_clause[0]),
                    col_val = sql.Literal(where_clause[1])
                )
        )
    cur.execute(
        sql.SQL("SELECT FROM {table_name} WHERE {queries}")
        .format(
            table_name = sql.Identifier(table_name),
            queries = sql.SQL(" AND ").join(where_clauses)
        )
    )
    assert cur.rowcount > 0, "Row with values {} not found on table {}".format(
        table_vals,
        table_name
    )
def cols_dont_exist_on_table(table_name: str, col_names : List[str]):
    for col_name in col_names:
        try:
            cols_exist_on_table(table_name, [col_name])
            #This line should only be reached if the col does exist on col
            assert False, (
                "Column {col} does exist on {table} but shouldn't"
                    .format(col_name, table_name)
            )
        except AssertionError as e:
            continue
    assert True

def cols_exist_on_table(table_name: str, col_names : List[str]):
    cur = get_db_cursor()
    for col_name in col_names:
        cur.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name=%s and column_name=%s;",
            [table_name, col_name]
        )
        assert cur.rowcount > 0, "Column {col_name} does not exist in {table}".format(
            col_name = col_name,
            table = table_name
        )
    return

def succesful_response_object(responseJson):
    assert "actionSucceeded" in responseJson
    assert "errorMessage" in responseJson
    assert responseJson["actionSucceeded"] == True, (
        "Action failed with error {err}"
            .format(err = responseJson["errorMessage"])
    )
    assert responseJson["errorMessage"] == ""