import uuid
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from app.db import get_db

shifts_bp = Blueprint("shifts", __name__)

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
    db = get_db()
    return db.collection("state").document("currentShift")

def shifts_collection():
    db = get_db()
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
    doc_ref = current_shift_doc()
    snap = doc_ref.get()

    if snap.exists:
        cur = snap.to_dict() or {}
        if cur.get("status") == "ACTIVE":
            return jsonify({"status": "ok", "message": "Shift already active", "shift": cur}), 200

    shift_id = str(uuid.uuid4())
    started_at = now_iso()

    shift = {
        "id": shift_id,
        "status": "ACTIVE",
        "startedAt": started_at,
        "endedAt": None,
    }

    # пишем историю
    shifts_collection().document(shift_id).set(shift)
    # пишем текущее состояние
    doc_ref.set(shift)

    return jsonify({"status": "ok", "message": "Shift started", "shift": shift}), 200

# ====== API: Stop shift ======

@shifts_bp.route("/shift/stop", methods=["POST"])
def stop_shift():
    doc_ref = current_shift_doc()
    snap = doc_ref.get()

    if not snap.exists:
        return jsonify({"status": "ok", "message": "No active shift", "shift": None}), 200

    cur = snap.to_dict() or {}
    if cur.get("status") != "ACTIVE":
        return jsonify({"status": "ok", "message": "Shift already stopped", "shift": cur}), 200

    ended_at = now_iso()
    started_at = cur.get("startedAt")
    shift_id = cur.get("id")

    # duration (секунды)
    duration_sec = None
    try:
        if started_at:
            dt_start = datetime.fromisoformat(started_at)
            dt_end = datetime.fromisoformat(ended_at)
            duration_sec = int((dt_end - dt_start).total_seconds())
    except Exception:
        pass

    cur["status"] = "STOPPED"
    cur["endedAt"] = ended_at
    cur["durationSec"] = duration_sec

    # обновляем историю
    if shift_id:
        shifts_collection().document(shift_id).set(cur, merge=True)

    # обновляем текущее состояние
    doc_ref.set(cur, merge=True)

    return jsonify({"status": "ok", "message": "Shift stopped", "shift": cur}), 200

# ====== API: Drive/Break actions ======

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
