from application.routes.query_routes import parse_query_string

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
        b'/Users?name=Leanne Graham&includes=Address,Company,Geo', "utf-8")


    
    return