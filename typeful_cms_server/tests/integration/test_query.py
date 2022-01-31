from flask.ctx import AppContext
import test_models
def test_simple_query(test_app : AppContext):
    test_models.test_simple_model_creation(test_app)
    res = test_app.app.test_client().get(
        "/Users?name=Leanne Graham&includes=Address[Geo],Company"
    )
    res_json = res.get_json()
    return