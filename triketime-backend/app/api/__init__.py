from flask import Blueprint
from .health import health_bp
from .shifts import shifts_bp
from .ai import ai_bp

__all__ = ["shifts_bp", "health_bp","ai_bp"]

api_bp = Blueprint("api", __name__) 
#, url_prefix="/api")

api_bp.register_blueprint(health_bp, url_prefix="/health")
api_bp.register_blueprint(shifts_bp, url_prefix="/shifts")
api_bp.register_blueprint(ai_bp, url_prefix="/ai")