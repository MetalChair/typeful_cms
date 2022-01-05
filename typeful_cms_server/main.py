from os import environ
import os
from application import init_app


app = init_app()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    #TODO: Set debug from environ
    app.run(host='0.0.0.0', debug=True)