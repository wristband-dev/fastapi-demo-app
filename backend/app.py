from flask import Flask

from src.api.auth.auth_route import auth_route

app = Flask(__name__)
app.register_blueprint(auth_route, url_prefix='/api')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)