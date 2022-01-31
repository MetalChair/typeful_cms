from application.routes.query_routes import parse_query_string

def test_parse_query_string():
    test_one = parse_query_string(b'name=logan', "utf-8")
    assert test_one[0] == ('name', '=', 'logan')

    test_two = parse_query_string(b'name==<>><=<>', "utf-8")
    assert test_two[0] == ('name', '=', '=<>><=<>')

    test_three = parse_query_string(b'name>=logan', "utf-8")
    assert test_three[0] == ('name', '>=', 'logan' )

    test_four = parse_query_string(b'<<><><><>', "utf-8")
    assert test_four[0] == ('', '<', '<><><><>')


    #TODO: Make these tests work
    #test_five = parse_query_string(b'`my<>><><>`=`<><>`', "utf-8")
    
    # test_six = parse_query_string(b'`a`b`c`=`d`e`f`', "utf-8")
    
    return