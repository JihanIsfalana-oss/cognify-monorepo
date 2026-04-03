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

from app.services.nlp_engine import process_farmer_input

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
@app.post("/api/nlp/extract", response_model=NLPExtractionResult, tags=["NLP Model FAO-56"])
async def extract_agronomy_entities(payload: NLPRequest):
    """
    Engine NLP Model FAO-56: 
    Mengekstrak Komoditas, Hama, Luas Lahan, dan Lokasi dari teks natural petani, 
    guna menentukan parameter koefisien air (Kc) standar FAO-56.
    """
    # Lempar teks ke AI Engine kita
    hasil_ner = process_farmer_input(payload.raw_text)
    
    if hasil_ner["komoditas"] or hasil_ner["hama"]:
        # Rangkai pesan respons dengan branding FAO-56
        msg = f"[Sistem NLP FAO-56] Ekstraksi sukses."
        if hasil_ner["komoditas"]:
            msg += f" Komoditas: {hasil_ner['komoditas']} (Var: {hasil_ner['varietas']})."
        if hasil_ner["hama"]:
            msg += f" Potensi Ancaman: {hasil_ner['hama']}."

        return NLPExtractionResult(
            success=True,
            message=msg,
            komoditas=hasil_ner["komoditas"] if hasil_ner["komoditas"] else "Fokus Hama",
            luas_lahan_ha=hasil_ner["luas_lahan_ha"],
            lokasi=hasil_ner["lokasi"],
            confidence=hasil_ner["confidence"]
        )
    
    # Jika sistem gagal menemukan apa-apa
    return NLPExtractionResult(
        success=False,
        message="[Sistem NLP FAO-56] Gagal mendeteksi parameter agrikultur (Komoditas/Hama) dalam kalimat.",
        komoditas="Tidak Diketahui",
        luas_lahan_ha=0.0,
        lokasi="Tidak Diketahui",
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