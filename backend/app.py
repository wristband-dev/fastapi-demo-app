from flask import Flask

from src.api.auth_route import auth_route

app = Flask(__name__)
app.register_blueprint(auth_route, url_prefix='/api/auth')
    
if __name__ == '__main__':
    # For local dev on plain HTTP:
    app.run(host='0.0.0.0', port=8080, debug=True)

    # Or for local HTTPS (self-signed):
    # app.run(host='0.0.0.0', port=8080, debug=True, ssl_context='adhoc')