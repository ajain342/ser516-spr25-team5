from flask import Flask
from app.routes import halstead_pv_routes

def create_app():
    app = Flask(__name__)

    app.register_blueprint(halstead_pv_routes.bp)

    return app