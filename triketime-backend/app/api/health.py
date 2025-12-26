from flask import Blueprint , jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return {"status": "ok", "service": "TrikeTime Backend"}, 200
