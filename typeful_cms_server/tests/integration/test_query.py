import json
from unicodedata import name
from flask.ctx import AppContext
import test_models
from typeful_cms_server.tests.helpers import succesful_response_object, compare_dicts_on_keys
def test_simple_query(test_app : AppContext):
    test_models.test_model_creation(test_app)
    res = test_app.app.test_client().get(
        "/Users?name=Leanne Graham&includes=Address,Company,Geo"
    )
    returned_json = json.loads(res.data)
    succesful_response_object(returned_json)
    user_list = returned_json["users"]
    assert len(user_list) == 1
    assert user_list[0]["name"] == "Leanne Graham"
    assert user_list[0]["username"] == "Bret"
    assert user_list[0]["address"] == {
            "street": "Kulas Light",
            "suite": "Apt. 556",
            "city": "Gwenborough",
            "zipcode": "92998-3874",
            "geo": {
                "lat": "-37.3159",
                "lng": "81.1496"
            }
        }

    return

def test_invalid_includes():
    return