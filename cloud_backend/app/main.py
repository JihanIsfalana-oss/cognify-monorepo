from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
import os
from pathlib import Path

# --- IMPOR SKEMA & DATABASE ---
from app.models.schemas import NLPRequest, NLPExtractionResult, TelemetryData
from app.database import SessionLocal, engine, Base, TelemetryRecord

# 1. Perintahkan SQLite untuk membuat tabel jika belum ada
Base.metadata.create_all(bind=engine)

# 2. Fungsi Dependency untuk membuka & menutup koneksi database dengan aman
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- SETUP PATH & LOAD DATA JSON ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

with open(DATA_DIR / "jenis_tanaman.json", "r", encoding="utf-8") as f:
    CROP_DB = json.load(f)["data"]

with open(DATA_DIR / "pest_types.json", "r", encoding="utf-8") as f:
    PEST_DB = json.load(f)["data"]

# ==========================================
# INISIALISASI MESIN UTAMA (Ini yang tadi hilang!)
# ==========================================
app = FastAPI(title="COGNIFY API Gateway", version="2.0.0")

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
    return {"status": "online", "message": "COGNIFY Knowledge Base terintegrasi!", "total_crops": len(CROP_DB)}

# --- ENDPOINT 2: EKSTRAKSI NLP ---
@app.post("/api/nlp/extract", response_model=NLPExtractionResult, tags=["Pemrosesan NLP"])
async def extract_agronomy_entities(payload: NLPRequest):
    teks = payload.raw_text.lower()
    detected_crop_name = None
    confidence_score = 0.0
    
    for crop in CROP_DB:
        if crop["nama_umum"].lower() in teks:
            detected_crop_name = crop["nama_umum"]
            confidence_score = 0.85
            
        for varietas in crop["varietas_populer"]:
            if varietas.lower() in teks:
                detected_crop_name = crop["nama_umum"]
                confidence_score = 0.98
                break 

        if detected_crop_name and confidence_score == 0.98:
            break 

    if detected_crop_name:
        return NLPExtractionResult(
            success=True,
            message=f"Mendeteksi komoditas {detected_crop_name}. Mengambil data FAO-56...",
            komoditas=detected_crop_name,
            luas_lahan_ha=2.0,
            lokasi="Kandanghaur",
            confidence=confidence_score
        )
    
    return NLPExtractionResult(
        success=False,
        message="Gagal mengekstrak. Komoditas tidak ditemukan.",
        komoditas="Tidak Diketahui",
        luas_lahan_ha=0.1,
        lokasi="Unknown",
        confidence=0.0
    )

@app.get("/api/data/hama", tags=["Database API"])
async def get_all_pests():
    return {"success": True, "data": PEST_DB}

# --- ENDPOINT 3: IOT TELEMETRI (DATABASE TERINTEGRASI) ---
@app.post("/api/iot/telemetry", tags=["IoT Telemetri"])
async def receive_telemetry(data: TelemetryData, db: Session = Depends(get_db)):
    """
    Menerima data dari ESP32, mengevaluasi status pompa, dan menyimpannya ke Database SQLite.
    """
    print(f"\n📡 [IoT Terhubung] Data masuk dari perangkat: {data.device_id}")
    
    # Logika Pompa Sederhana
    instruksi_pompa = "ON" if data.kelembapan_tanah < 40.0 else "OFF"
    
    if instruksi_pompa == "ON":
        print("   ⚠️ Peringatan: Tanah kering! Mengirim instruksi POMPA ON ke ESP32.")

    # 1. Bungkus data ke format Tabel Database
    db_record = TelemetryRecord(
        device_id=data.device_id,
        kelembapan_tanah=data.kelembapan_tanah,
        suhu_lingkungan=data.suhu_lingkungan,
        ph_tanah=data.ph_tanah,
        status_pompa=(instruksi_pompa == "ON")
    )
    
    # 2. Simpan secara permanen ke file SQLite!
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return {
        "success": True,
        "message": "Data telemetri berhasil direkam ke Database",
        "record_id": db_record.id,
        "instruksi_pompa": instruksi_pompa
    }