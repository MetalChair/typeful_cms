import os
import sys
from application import init_app


app = init_app()
if __name__ == "__main__":
    #TODO: Set debug from environ
    app.run(host='0.0.0.0', debug=True, port=3000)