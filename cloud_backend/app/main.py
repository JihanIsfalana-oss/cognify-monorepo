# cloud_backend/app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
from app.core.config import settings
from google.cloud import firestore

# --- IMPOR SKEMA & DATABASE ---
from app.core.firebase import db
from app.services.nlp_engine import process_farmer_input
from app.services.weather_bridge import sync_weather_by_ai_signal
from app.services.geo_radar import scan_nearby_threats
from app.models.schemas import NLPRequest, NLPExtractionResult, TelemetryData

# --- SETUP PATH DATA MASTER ---
BASE_DIR = Path(__file__).resolve().parent
MONOREPO_DIR = BASE_DIR.parent.parent
DATA_DIR = MONOREPO_DIR / "ai_engine" / "data" / "nlp_dataset"

# Graceful Loading Data Master (Lokal sebagai SSOT)
try:
    with open(settings.TANAMAN_JSON, "r", encoding="utf-8") as f:
        CROP_DB = json.load(f).get("data", [])
    with open(settings.PEST_JSON, "r", encoding="utf-8") as f:
        PEST_DB = json.load(f).get("data", [])
except Exception as e:
    print(f"⚠️ WARNING Master Data: {e}")
    CROP_DB, PEST_DB = [], []


# --- INISIALISASI APP ---
app = FastAPI(title="COGNIFY Cloud API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENDPOINT 1: HEALTH CHECK ---
@app.get("/", tags=["Sistem Manajer"])
async def root_health_check():
    return {
        "status": "online", 
        "engine": "Firebase Firestore",
        "message": "COGNIFY Gateway Terintegrasi"
    }

# --- ENDPOINT 2: EKSTRAKSI NLP + CUACA ---
@app.post("/api/nlp/extract", response_model=NLPExtractionResult, tags=["AI Engine"])
async def extract_agronomy_entities(payload: NLPRequest):
    try:
        hasil_ner = process_farmer_input(payload.raw_text)
        
        if hasil_ner.get("komoditas") != "Tidak Diketahui" or hasil_ner.get("lokasi") != "Tidak Diketahui":
            suhu_aktual, total_air_liter = 0.0, 0.0
            nama_lokasi = hasil_ner.get("lokasi", "")

            msg = "[Sistem NLP] Ekstraksi sukses."

            if nama_lokasi != "Tidak Diketahui":
                res_cuaca = sync_weather_by_ai_signal(nama_lokasi)
                if res_cuaca.get("success"):
                    suhu_aktual = res_cuaca["weather_data"]["temp"]
                    et0 = res_cuaca["reference_evapotranspiration_et0"]
                    total_air_liter = et0 * 1.15 * hasil_ner.get("luas_lahan_ha", 0.0) * 10000

                    msg += f" Cuaca di {nama_lokasi}: {suhu_aktual}°C. Kebutuhan Irigasi: {round(total_air_liter)} L/hari."
                else:
                    msg += f" (Data cuaca {nama_lokasi} gagal ditarik)."

            return {
                **hasil_ner, 
                "suhu_lokasi": suhu_aktual, 
                "kebutuhan_air_liter": round(total_air_liter, 2), 
                "success": True,
                "message": msg 
            }

        return {
            "success": False, 
            "message": "Gagal mendeteksi entitas.",
            "komoditas": "Tidak Diketahui",
            "luas_lahan_ha": 0.0,
            "lokasi": "Tidak Diketahui",
            "confidence": 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ENDPOINT 3: IOT TELEMETRI (FIREBASE) ---
@app.post("/api/iot/telemetry", tags=["IoT Telemetri"])
async def receive_telemetry(data: TelemetryData):
    """Menerima data dari ESP32 dan menyimpannya ke Firestore."""
    try:
        instruksi_pompa = "ON" if data.kelembapan_tanah < 40.0 else "OFF"
        
        # 1. Simpan Log Historis (Collection: telemetry_logs)
        db.collection("telemetry_logs").add({
            "device_id": data.device_id,
            "kelembapan_tanah": data.kelembapan_tanah,
            "suhu_lingkungan": data.suhu_lingkungan,
            "ph_tanah": data.ph_tanah,
            "status_pompa": instruksi_pompa,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        
        # 2. Update Status Lahan (Collection: lahan_pertanian)
        db.collection("lahan_pertanian").document(data.device_id).set({
            "last_updated": firestore.SERVER_TIMESTAMP,
            "current_status": {
                "kelembapan": data.kelembapan_tanah,
                "pompa": instruksi_pompa
            },
            "koordinat": {"lat": data.lat, "lon": data.lon}
        }, merge=True)

        return {"success": True, "instruksi_pompa": instruksi_pompa}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase Error: {str(e)}")

# --- ENDPOINT 4: GEOSPATIAL RADAR SCAN ---
@app.get("/api/radar/scan", tags=["Geospatial Radar"])
async def geospatial_radar_scan(lat: float, lon: float, radius_km: float = 10.0):
    """Mendeteksi ancaman hama di sekitar koordinat tertentu."""
    try:
        threats = scan_nearby_threats(lat, lon, radius_km)
        return {
            "success": True, 
            "center": {"lat": lat, "lon": lon},
            "radius": f"{radius_km} km",
            "threats_found": len(threats),
            "data": threats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))