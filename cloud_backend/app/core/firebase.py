# cloud_backend/app/core/firebase.py
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CRED_PATH = BASE_DIR / "serviceAccountKey.json"

class FirebaseClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseClient, cls).__new__(cls)
            if not firebase_admin._apps:
                try:
                    cred = credentials.Certificate(str(CRED_PATH))
                    firebase_admin.initialize_app(cred)
                except Exception as e:
                    print(f"Firebase Init Error: {e}")
            cls._instance.db = firestore.client()
        return cls._instance

db = FirebaseClient().db