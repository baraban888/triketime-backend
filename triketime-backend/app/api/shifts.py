from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from app.db import get_db

shifts_bp = Blueprint("shifts", __name__, url_prefix="/api")
db = get_db()

def now_iso() -> str:
    """Текущий момент в ISO-формате UTC (как в мобильном приложении)."""
    return datetime.now(timezone.utc).isoformat()

def parse_iso(ts: str) -> datetime:
    # поддержка "Z" от Android: 2025-...T...Z
    if ts.endswith("Z"):
        ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)

def current_shift_doc():
    # один документ состояния   
    return db.collection("state").document("currentShift")

def shifts_collection():
    return db.collection("shifts")

# ====== API: Текущая смена ======

@shifts_bp.route("/shift/current", methods=["GET"])
def get_current_shift():
    doc = current_shift_doc().get()
    if not doc.exists:
        return jsonify({"status": "ok", "message": "No active shift", "shift": None})

    shift = doc.to_dict()
    if not shift or shift.get("status") != "ACTIVE":
        return jsonify({"status": "ok", "message": "No active shift", "shift": None})

    return jsonify({"status": "ok", "message": "Shift is active", "shift": shift})

# ====== API: Start shift ======

@shifts_bp.route("/shift/start", methods=["POST"])
def start_shift():
    data = request.get_json(silent=True) or {}
    ts = data.get("timestamp") or now_iso()

    doc_ref = current_shift_doc()
    doc = doc_ref.get()
    if doc.exists:
        existing = doc.to_dict() or {}
        if existing.get("status") == "ACTIVE":
            return jsonify({"status": "error", "message": "Shift already active", "shift": existing}), 400

    # создаём новый id (можно uuid, но пусть будет doc id из Firestore)
    new_ref = shifts_collection().document()
    shift = {
        "id": new_ref.id,
        "status": "ACTIVE",
        "startedAt": ts,
        "endedAt": None,
        "durationSeconds": None,
    }

    # пишем и в историю, и в "current"
    new_ref.set(shift)
    doc_ref.set(shift)

    return jsonify({"status": "ok", "message": "Shift started", "shift": shift})

# ====== API: Stop shift ======

@shifts_bp.route("/shift/stop", methods=["POST"])
def stop_shift():
    data = request.get_json(silent=True) or {}
    end_ts = data.get("timestamp") or now_iso()

    doc_ref = current_shift_doc()
    doc = doc_ref.get()
    if not doc.exists:
        return jsonify({"status": "error", "message": "No active shift to stop", "shift": None}), 400

    shift = doc.to_dict() or {}
    if shift.get("status") != "ACTIVE":
        return jsonify({"status": "error", "message": "No active shift to stop", "shift": None}), 400

    # duration
    try:
        started = parse_iso(shift["startedAt"])
        ended = parse_iso(end_ts)
        duration = int((ended - started).total_seconds())
    except Exception:
        duration = None

    finished = {
        **shift,
        "status": "FINISHED",
        "endedAt": end_ts,
        "durationSeconds": duration,
    }

    # обновим историю (если id есть)
    shift_id = finished.get("id")
    if shift_id:
        shifts_collection().document(shift_id).set(finished, merge=True)

    # удаляем currentShift => больше нет активной смены
    doc_ref.delete()

    return jsonify({"status": "ok", "message": "Shift stopped", "shift": finished})

# ====== Заглушки для drive/break (можно потом доработать аналогично) ======

@shifts_bp.route("/drive/start", methods=["POST"])
def start_drive():
    return jsonify({"status": "ok", "message": "Drive started"})


@shifts_bp.route("/drive/stop", methods=["POST"])
def stop_drive():
    return jsonify({"status": "ok", "message": "Drive/Break stopped"})


@shifts_bp.route("/break/start", methods=["POST"])
def start_break():
    return jsonify({"status": "ok", "message": "Break started"})


@shifts_bp.route("/break/stop", methods=["POST"])
def stop_break():
    return jsonify({"status": "ok", "message": "Break stopped"})
