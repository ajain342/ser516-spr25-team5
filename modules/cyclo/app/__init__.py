from flask import Flask
from app.routes import cyclo_routes

def create_app():
    app = Flask(__name__)

    app.register_blueprint(cyclo_routes.bp)

    return app
