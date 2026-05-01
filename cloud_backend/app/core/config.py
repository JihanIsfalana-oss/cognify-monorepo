# cloud_backend/app/core/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load variabel dari .env
load_dotenv()

# --- JANGKAR PATHING (Pathlib) ---
CORE_DIR = Path(__file__).resolve().parent
APP_DIR = CORE_DIR.parent
BACKEND_ROOT = APP_DIR.parent  # cloud_backend/
MONOREPO_ROOT = BACKEND_ROOT.parent  # cognify-monorepo/

class Settings:
    PROJECT_NAME: str = "COGNIFY Intelligence Hub"
    
    # 1. Jalur Kredensial (Cloud Backend)
    FIREBASE_CREDS_PATH = BACKEND_ROOT / "serviceAccountKey.json"
    ENV_FILE_PATH = BACKEND_ROOT / ".env"
    
    # 2. Jalur Data AI (AI Engine)
    AI_DATA_DIR = MONOREPO_ROOT / "ai_engine" / "data" / "nlp_dataset"
    LOKASI_JSON = AI_DATA_DIR / "lokasi.json"
    TANAMAN_JSON = AI_DATA_DIR / "jenis_tanaman.json"
    PEST_JSON = AI_DATA_DIR / "pest_types.json"
    
    # 3. Jalur Model AI (AI Engine)
    AI_MODEL_DIR = MONOREPO_ROOT / "ai_engine" / "models"
    
    # 4. Kredensial API ( .env)
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Inisialisasi sebagai Singleton
settings = Settings()