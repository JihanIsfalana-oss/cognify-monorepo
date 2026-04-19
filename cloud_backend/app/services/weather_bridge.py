# cloud_backend/app/services/weather_bridge.py

import json
from pathlib import Path
from .weather_service import WeatherEngine, calculate_et0_simple

CURRENT_DIR = Path(__file__).resolve().parent
MONOREPO_DIR = CURRENT_DIR.parent.parent.parent
DATA_PATH = MONOREPO_DIR / "ai_engine" / "data" / "nlp_dataset" / "lokasi.json"

def sync_weather_by_ai_signal(location_name: str):
    """
    Fungsi utama untuk sinkronisasi data cuaca berdasarkan
    lokasi yang dideteksi oleh Model FAO-56.
    """
    try:
        # 1. Load data koordinat dari lokasi.json dengan path yang aman
        if not DATA_PATH.exists():
            return {"success": False, "message": f"File Lokasi tidak ditemukan di {DATA_PATH}"}
            
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            lokasi_db = json.load(f).get("data", [])
        
        # 2. Cari koordinat berdasarkan nama lokasi
        target_geo = next((item for item in lokasi_db if item["nama"].lower() == location_name.lower()), None)
        
        if not target_geo:
            return {"success": False, "message": "Lokasi tidak terdaftar di Database Geo."}

        # 3. Ambil data cuaca berdasarkan koordinat yang ditemukan
        weather = WeatherEngine()
        data_cuaca = weather.get_weather_data(target_geo["lat"], target_geo["lon"])
        
        if not data_cuaca:
             return {"success": False, "message": "Gagal menarik data dari API Cuaca."}
        
        # 4. Hitung ET0 (Evapotranspirasi Referensi)
        et0 = calculate_et0_simple(data_cuaca["temp"], data_cuaca["humidity"])
        
        return {
            "success": True,
            "firebase_signal": target_geo["firebase_signal"],
            "weather_data": data_cuaca,
            "reference_evapotranspiration_et0": et0,
            "message": f"Sinyal {target_geo['firebase_signal']} aktif. Data cuaca berhasil disinkronkan."
        }
    except Exception as e:
        print(f"❌ Error Weather Bridge: {e}")
        return {"success": False, "message": str(e)}