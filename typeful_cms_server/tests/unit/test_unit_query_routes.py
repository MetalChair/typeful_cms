from application.routes.query_routes import parse_query_string, form_query
from flask.ctx import AppContext
from application.database.database import get_table_attribs

from tests.integration.test_models import test_model_creation

def test_parse_query_string():
    (test_one,_) = parse_query_string(b'name=logan', "utf-8")
    assert test_one[0] == ('name', '=', 'logan')

    (test_two,_) = parse_query_string(b'name==<>><=<>', "utf-8")
    assert test_two[0] == ('name', '=', '=<>><=<>')

    (test_three,_) = parse_query_string(b'name>=logan', "utf-8")
    assert test_three[0] == ('name', '>=', 'logan' )

    (test_four,_) = parse_query_string(b'<<><><><>', "utf-8")
    assert test_four[0] == ('', '<', '<><><><>')

    (test_five, includes) = parse_query_string(
        b'users.name=Leanne Graham&includes=address,company,geo', "utf-8")
        
    assert test_five[0] == ('users.name', '=','Leanne Graham')
    assert includes == ["address", "company", "geo"]

def test_get_table_attribs(test_app : AppContext):
    #Arrange
    test_model_creation(test_app)

    #Act
    attribs = get_table_attribs(["users","address","geo","company"], "public")
    assert len(attribs) == 4
    assert attribs['users']['accesible_fields'] == ['aliases','email','favorite_number','id','name','phone','username','website']
    assert attribs['geo']['accesible_fields'] == ['lat','lng']
    assert attribs['geo']['parent_table'] == 'address'
    assert attribs['address']['parent_table'] == 'users'
    return

    
