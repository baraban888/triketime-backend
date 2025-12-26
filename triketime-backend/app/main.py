from flask import Flask
from app.api.health import health_bp
from app.api.shifts import shifts_bp
from dotenv import load_dotenv
import os
from flask_cors import CORS

load_dotenv()

def create_app():
    app = Flask(__name__)

    CORS(app, resources={
        r"/api/*": {
            "origins": "*"
        }
    })
    # регистрируем blueprints
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(shifts_bp, url_prefix="/api")

    @app.get("/")
    def index():
        return {"message": "TrikeTime Backend is running"}

    return app

# ВАЖНО: gunicorn будет искать именно эту переменную:
app = create_app()

