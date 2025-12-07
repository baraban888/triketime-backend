from flask import Flask
from app.api.health import health_bp
from app.api.health import health_bp
from app.api.shifts import shifts_bp
from dotenv import load_dotenv
load_dotenv()
import os

def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(shifts_bp)
    
    @app.route("/")
    def index():
        return {"message": "TrikeTime Backend is running"}

    return app


# Cloud Run uses PORT=8080
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080)
