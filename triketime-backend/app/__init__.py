from flask import Flask
from .config import Config
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)  # чтобы PWA не страдал

    return app
