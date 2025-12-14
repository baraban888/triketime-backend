# db.py
from google.cloud import firestore

_db = None

def get_db() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db
