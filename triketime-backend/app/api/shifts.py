from flask import Blueprint, jsonify
from datetime import datetime

shifts_bp = Blueprint("shifts", __name__, url_prefix="/api/shifts")

# ВРЕМЕННО: храним данные в памяти (пока без базы)
SHIFTS = []
NEXT_ID = 1

def _calc_duration_seconds(start_iso, end_iso):
    """Посчитать длительность в секундах между двумя ISO-датами."""
    # убираем 'Z' в конце, чтобы fromisoformat не ругался
    start = datetime.fromisoformat(start_iso.replace("Z", ""))
    end = datetime.fromisoformat(end_iso.replace("Z", ""))
    return int((end - start).total_seconds())

def get_current_shift():
    """Вернуть текущую активную смену (status == running) или None."""
    for shift in SHIFTS:
        if shift["status"] == "running":
            return shift
    return None

def get_current_event(shift):
    """Вернуть текущее активное событие (drive/break), если есть."""
    if "events" not in shift:
        shift["events"] = []
        return None

    for event in shift["events"]:
        if event["ended_at"] is None:
            return event

    return None

def start_event(shift, event_type):
    """Создать новое событие (drive или break)."""
    if "events" not in shift:
        shift["events"] = []

    now = datetime.utcnow().isoformat() + "Z"
    event = {
        "type": event_type,
        "started_at": now,
        "ended_at": None,
    }
    shift["events"].append(event)
    return event

def stop_event(shift):
    """Остановить текущее активное событие, если оно есть."""
    event = get_current_event(shift)
    if event is None:
        return None

    now = datetime.utcnow().isoformat() + "Z"
    event["ended_at"] = now
    # добавляем длительность
    event["duration_seconds"] = _calc_duration_seconds(event["started_at"], now)
    return event

@shifts_bp.get("/")
def list_shifts():
    """Вернуть все смены (пока из памяти)."""
    return jsonify(SHIFTS), 200


@shifts_bp.post("/start")
def start_shift():
    """Начать смену, если сейчас нет активной."""
    global NEXT_ID

    current = get_current_shift()
    if current is not None:
        return (
            jsonify(
                {
                    "error": "shift_already_running",
                    "message": "Смена уже запущена, сначала останови текущую.",
                    "current_shift_id": current["id"],
                }
            ),
            400,
        )

    now = datetime.utcnow().isoformat() + "Z"

    shift = {
        "id": NEXT_ID,
        "started_at": now,
        "ended_at": None,
        "status": "running",
    }
    NEXT_ID += 1
    SHIFTS.append(shift)

    return jsonify(shift), 201

@shifts_bp.post("/stop")
def stop_shift():
    """Остановить текущую активную смену, если нет активных событий."""
    current = get_current_shift()
    if current is None:
        return jsonify({
            "error": "no_running_shift",
            "message": "Нет активной смены для остановки."
        }), 400

    if has_active_event(current):
        return jsonify({
            "error": "active_event_running",
            "message": "Нельзя остановить смену, пока идёт drive или break. Сначала останови все события."
        }), 400

    now = datetime.utcnow().isoformat() + "Z"
    current["ended_at"] = now
    current["status"] = "finished"
    current["duration_seconds"] = _calc_duration_seconds(current["started_at"], now)

    return jsonify(current), 200

@shifts_bp.post("/drive/start")
def drive_start():
    shift = get_current_shift()
    if shift is None:
        return jsonify({"error": "no_shift", "message": "Смена не запущена"}), 400

    current_event = get_current_event(shift)
    if current_event is not None:
        return jsonify({
            "error": "event_already_running",
            "message": f"Нельзя начать drive. Сейчас идёт {current_event['type']}.",
            "current_event": current_event
        }), 400
    def has_active_event(shift):
        """Проверить, есть ли в смене активное событие (drive/break)."""
        if "events" not in shift:
            return False

    for event in shift["events"]:
        if event["ended_at"] is None:
            return True

    return False

    event = start_event(shift, "drive")
    return jsonify(event), 201

@shifts_bp.post("/break/start")
def break_start():
    shift = get_current_shift()
    if shift is None:
        return jsonify({"error": "no_shift", "message": "Смена не запущена"}), 400

    current_event = get_current_event(shift)
    if current_event is not None:
      return jsonify({
        "error": "event_already_running",
        "message": f"Нельзя начать break. Сейчас идёт {current_event['type']}.",
        "current_event": current_event
    }), 400

    event = start_event(shift, "break")
    return jsonify(event), 201

@shifts_bp.post("/drive/stop")
def drive_stop():
    shift = get_current_shift()
    if shift is None:
        return jsonify({"error": "no_shift", "message": "Смена не запущена"}), 400

    event = get_current_event(shift)
    if event is None or event["type"] != "drive":
        return jsonify({
          "error": "no_active_drive",
          "message": "Нельзя остановить вождение — оно не начато."
    }), 400
    stopped = stop_event(event)
    return jsonify(stopped), 200


@shifts_bp.post("/break/stop")
def break_stop():
    shift = get_current_shift()
    if shift is None:
        return jsonify({
          "error": "no_active_break",
          "message": "Нельзя остановить перерыв — он не начат."
    }), 400

    event = get_current_event(shift)
    if event is None or event["type"] != "break":
        return jsonify({"error": "no_event", "message": "Нет активного перерыва"}), 400

    stopped = stop_event(event)
    return jsonify(stopped), 200

@shifts_bp.get("/current")
def current_shift():
    """Вернуть текущую активную смену, если есть."""
    current = get_current_shift()
    if current is None:
        return (
            jsonify(
                {
                    "active": False,
                    "message": "Сейчас нет активной смены.",
                }
            ),
            200,
        )

    return jsonify(
        {
            "active": True,
            "shift": current,
        }
    ), 200

@shifts_bp.get("/history")
def shifts_history():
    """Вернуть только завершённые смены (status == finished)."""
    finished = [s for s in SHIFTS if s.get("status") == "finished"]
    return jsonify(finished), 200
