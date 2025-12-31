import os
from flask import Blueprint, request, jsonify
from app.db import get_db  # если хочешь хранить историю в Firestore

ai_bp = Blueprint("ai", __name__)

SYSTEM_PROMPT = """You are TrikeTime, a concise AI assistant for EU truck drivers.
Goal: help the driver stay compliant with EU Regulation (EC) No 561/2006.
Style: English, very short answers (1-3 sentences), ask 1 clarifying question if needed.
Safety: not legal advice; if unsure, say what info is missing.

Rules focus (MVP):
- Break: after max 4h30 driving, take 45 min break (can be split 15+30).
- Daily driving: max 9h (twice per week 10h).
- Daily rest: 11h regular (can reduce to 9h up to 3 times between weekly rests).
- Weekly rest: regular 45h / reduced 24h (compensation required).
"""

def get_current_shift_summary(driver_id: str):
    # optional: pull your "currentShift_{driver_id}" from Firestore if exists
    db = get_db()
    doc = db.collection("state").document(f"currentShift_{driver_id}").get()
    if not doc.exists:
        return "No active shift."
    s = doc.to_dict() or {}
    if s.get("status") != "ACTIVE":
        return "No active shift."
    started = s.get("startedAt")
    return f"Active shift startedAt={started}."

@ai_bp.post("/ai/chat")
def ai_chat():
    data = request.get_json(silent=True) or {}
    driver_id = data.get("driverId") or request.args.get("driverId") or "demo"
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"status": "error", "error": "message is required"}), 400

    # minimal context
    shift_summary = get_current_shift_summary(driver_id)

    # ---- Vertex AI (Gemini) via Google auth on Cloud Run ----
    # simplest path: use google-genai (recommended) OR vertexai sdk
    # I'll give you the working version once you confirm which library is in requirements.
    #
    # For now return a stub so endpoint works:
    answer = f"{shift_summary} Tell me: how much driving since your last 45-min break?"

    return jsonify({"status": "ok", "answer": answer}), 200
