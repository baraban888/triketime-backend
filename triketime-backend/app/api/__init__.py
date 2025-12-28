from flask import Blueprint
from .health import health_bp
from .shifts import shifts_bp

__all__ = ["shifts_bp", "health_bp"]

api_bp = Blueprint("api", __name__, url_prefix="/api")

api_bp.register_blueprint(health_bp)
api_bp.register_blueprint(shifts_bp)
