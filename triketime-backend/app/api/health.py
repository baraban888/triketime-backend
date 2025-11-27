from flask import Blueprint

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health():
    return {"status": "ok", "service": "TrikeTime Backend"}, 200
