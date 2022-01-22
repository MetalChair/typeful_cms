from flask.ctx import AppContext
import test_models
def test_create_row(test_app : AppContext):
    test_models.test_simple_model_creation(test_app)
    test_app.app.test_client().post("/TestModel")
    return