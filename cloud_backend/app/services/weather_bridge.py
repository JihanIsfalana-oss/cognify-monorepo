# cloud_backend/app/services/weather_bridge.py

import json
from pathlib import Path
from .weather_service import WeatherEngine, calculate_et0_simple

DATA_PATH = Path("ai_engine/data/nlp_dataset/lokasi.json")

def sync_weather_by_ai_signal(location_name: str):
    """
    Fungsi utama untuk sinkronisasi data cuaca berdasarkan
    lokasi yang dideteksi oleh AI.
    """
    # 1. Load data koordinat dari lokasi.json
    with open(DATA_PATH, "r") as f:
        lokasi_db = json.load(f).get("data", [])
    
    # 2. Cari koordinat berdasarkan nama lokasi
    target_geo = next((item for item in lokasi_db if item["nama"].lower() == location_name.lower()), None)
    
    if not target_geo:
        return {"success": False, "message": "Lokasi tidak terdaftar di Database Geo."}

    # 3. Ambil data cuaca (Gunakan API Key OpenWeatherMap)
    weather = WeatherEngine(api_key="API_KEY_ANDA")
    data_cuaca = weather.get_weather_data(target_geo["lat"], target_geo["lon"])
    
    # 4. Hitung ET0 (Evapotranspirasi Referensi)
    et0 = calculate_et0_simple(data_cuaca["temp"], data_cuaca["humidity"])
    
    return {
        "success": True,
        "firebase_signal": target_geo["firebase_signal"],
        "weather_data": data_cuaca,
        "reference_evapotranspiration_et0": et0,
        "message": f"Sinyal {target_geo['firebase_signal']} aktif. Data cuaca berhasil disinkronkan."
    }