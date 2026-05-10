# cloud_backend/app/services/weather_bridge.py

import json
import math
from datetime import datetime
from .weather_service import WeatherEngine, calculate_et0_simple
from app.core.config import settings 

def sync_weather_by_ai_signal(location_name: str):
    """
    Fungsi utama untuk sinkronisasi data cuaca berdasarkan
    lokasi yang dideteksi oleh Model FAO-56.
    """
    try:
        # 1. Load data koordinat MENGGUNAKAN CONFIG SENTRAL
        if not settings.LOKASI_JSON.exists():
            return {"success": False, "message": f"File Lokasi tidak ditemukan di {settings.LOKASI_JSON}"}
            
        with open(settings.LOKASI_JSON, "r", encoding="utf-8") as f:
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
         
        suhu_min = data_cuaca.get("temp_min", data_cuaca["temp"] - 5.0) 
        hari_ini_doy = datetime.now().timetuple().tm_yday
        lat_radian = math.radians(target_geo["lat"])
        
        # 4. Hitung ET0 (Evapotranspirasi Referensi)
        et0 = calculate_et0_simple(
            temp=data_cuaca["temp"], 
            humidity=data_cuaca["humidity"],
            temp_min=suhu_min,
            day_of_year=hari_ini_doy,
            latitude_rad=lat_radian
        )
        
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