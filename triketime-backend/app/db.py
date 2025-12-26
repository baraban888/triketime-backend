# db.py
from google.cloud import firestore

_db = None

def init_db() -> firestore.Client:
    """Optional init hook. Creates a global Firestore client once."""
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db

def get_db() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db
