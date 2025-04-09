from flask import Flask
from app.routes import defect_routes


def create_app():
    app = Flask(__name__)

    app.register_blueprint(defect_routes.bp)

    return app
