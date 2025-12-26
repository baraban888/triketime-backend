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

def get_driver_id():
    data = request.get_json(silent=True) or {}
    driver_id = data.get("driverId")

    # временный дефолт, чтобы не ломать ручные вызовы
    if not driver_id:
        driver_id = request.args.get("driverId") or "demo"

    return driver_id


def current_shift_doc(driver_id: str):
    db = get_db()
    return db.collection("state").document(f"currentShift_{driver_id}")


def shifts_collection():
    db = get_db()
    return db.collection("shifts")



# ====== API: Текущая смена ======

@shifts_bp.route("/shift/current", methods=["GET"])
def get_current_shift():
    driver_id = request.args.get("driverId") or "demo"

    doc = current_shift_doc(driver_id).get()
    if not doc.exists:
        return jsonify({"status": "ok", "message": "No active shift", "shift": None}), 200

    shift = doc.to_dict()
    if not shift or shift.get("status") != "ACTIVE":
        return jsonify({"status": "ok", "message": "No active shift", "shift": None}), 200

    return jsonify({"status": "ok", "message": "Shift is active", "shift": shift}), 200


# ====== API: Start shift ======

@shifts_bp.route("/shift/start", methods=["POST"])
def start_shift():
    driver_id = get_driver_id()

    doc_ref = current_shift_doc(driver_id)
    snap = doc_ref.get()

    if snap.exists:
        cur = snap.to_dict() or {}
        if cur.get("status") == "ACTIVE":
            # для приложения удобнее вернуть ok + текущее состояние
            return jsonify({"status": "ok", "message": "Shift already active", "shift": cur}), 200

    shift_id = str(uuid.uuid4())
    started_at = now_iso()

    shift = {
        "id": shift_id,
        "driverId": driver_id,
        "status": "ACTIVE",
        "startedAt": started_at,
        "endedAt": None,
        "durationSeconds": None,
    }

    # пишем историю
    shifts_collection().document(shift_id).set(shift)
    # пишем текущее состояние
    doc_ref.set(shift)

    return jsonify({"status": "ok", "message": "Shift started", "shift": shift}), 200


# ====== API: Stop shift ======

@shifts_bp.route("/shift/stop", methods=["POST"])
def stop_shift():
    driver_id = get_driver_id()

    doc_ref = current_shift_doc(driver_id)
    snap = doc_ref.get()

    if not snap.exists:
        return jsonify({"status": "ok", "message": "No active shift to stop", "shift": None}), 200

    cur = snap.to_dict() or {}
    if cur.get("status") != "ACTIVE":
        return jsonify({"status": "ok", "message": "No active shift to stop", "shift": cur}), 200

    ended_at = now_iso()
    duration = int((parse_iso(ended_at) - parse_iso(cur["startedAt"])).total_seconds())

    finished = {
        **cur,
        "status": "FINISHED",
        "endedAt": ended_at,
        "durationSeconds": duration,
    }

    # обновляем историю
    shifts_collection().document(cur["id"]).set(finished)
    # обновляем текущее состояние
    doc_ref.set(finished)

    return jsonify({"status": "ok", "message": "Shift stopped", "shift": finished}), 200

# ====== API: Breaks ======

@shifts_bp.route("/break/start", methods=["POST"])
def start_break():
    return jsonify({"status": "ok", "message": "Break started"})

@shifts_bp.route("/break/stop", methods=["POST"])
def stop_break():
    return jsonify({"status": "ok", "message": "Break stopped"})

@shifts_bp.route("/shifts", methods=["GET"])
def list_shifts():
    driver_id = request.args.get("driverId") or "demo"
    limit = int(request.args.get("limit", 20))

    q = (
        shifts_collection()
        .where("driverId", "==", driver_id)
        .order_by("startedAt", direction="DESCENDING")
        .limit(limit)
    )

    items = [doc.to_dict() for doc in q.stream()]
    return jsonify({"status": "ok", "items": items}), 200
