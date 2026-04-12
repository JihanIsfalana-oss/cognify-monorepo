# cloud_backend/app/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
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

# --- SETUP PATH & LOAD DATA JSON DENGAN AMAN ---
BASE_DIR = Path(__file__).resolve().parent
MONOREPO_DIR = BASE_DIR.parent.parent

DATA_DIR = MONOREPO_DIR / "ai_engine" / "data" / "nlp_dataset"

# 1. Graceful Loading untuk Komoditas
try:
    with open(DATA_DIR / "jenis_tanaman.json", "r", encoding="utf-8") as f:
        CROP_DB = json.load(f).get("data", []) 
except Exception as e:
    print(f"⚠️ WARNING DB Komoditas: {e}")
    CROP_DB = [{"nama_umum": "Padi"}, {"nama_umum": "Jagung"}, {"nama_umum": "Cabai"}] # Data Darurat

# 2. Graceful Loading untuk Hama
try:
    pest_file = DATA_DIR / "Pesttype.json"
    if not pest_file.exists():
        pest_file = DATA_DIR / "pest_types.json"
        
    with open(pest_file, "r", encoding="utf-8") as f:
        PEST_DB = json.load(f).get("data", [])
except Exception as e:
    print(f"⚠️ WARNING DB Hama: {e}")
    PEST_DB = [{"nama": "Wereng Batang Coklat"}, {"nama": "Penggerek Batang"}] # Data Darurat


# ==========================================
# INISIALISASI MESIN UTAMA 
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
    Mengekstrak Komoditas, Luas Lahan (Hektar), dan Sinyal Lokasi Firebase.
    """
    try:
        hasil_ner = process_farmer_input(payload.raw_text)
        
        # Cek apakah AI berhasil menemukan Komoditas ATAU Lokasi
        if hasil_ner.get("komoditas") != "Tidak Diketahui" or hasil_ner.get("lokasi") != "Tidak Diketahui":
            
            # Rangkai pesan respons dengan branding FAO-56
            msg = f"[Sistem NLP FAO-56] Ekstraksi sukses."
            if hasil_ner.get("komoditas") != "Tidak Diketahui":
                msg += f" Komoditas: {hasil_ner['komoditas']}."
            if hasil_ner.get("lokasi") != "Tidak Diketahui":
                msg += f" Lokasi: {hasil_ner['lokasi']} (Sinyal: {hasil_ner.get('firebase_signal', 'N/A')})."

            return NLPExtractionResult(
                success=True,
                message=msg,
                komoditas=hasil_ner.get("komoditas", "Tidak Diketahui"),
                luas_lahan_ha=hasil_ner.get("luas_lahan_ha", 0.0),
                lokasi=hasil_ner.get("lokasi", "Tidak Diketahui"),
                confidence=hasil_ner.get("confidence", 0.0)
            )
        
        # Jika sistem gagal menemukan apa-apa
        return NLPExtractionResult(
            success=False,
            message="[Sistem NLP FAO-56] Gagal mendeteksi parameter agrikultur dalam kalimat.",
            komoditas="Tidak Diketahui",
            luas_lahan_ha=0.0,
            lokasi="Tidak Diketahui",
            confidence=0.0
        )
    except Exception as e:
        # Melindungi Server dari Crash jika AI mengalami error internal
        print(f"❌ Error Internal NLP: {e}")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan pada model FAO-56: {str(e)}")

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
    
    # 2. Simpan secara permanen ke file SQLite
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return {
        "success": True,
        "message": "Data telemetri berhasil direkam ke Database",
        "record_id": db_record.id,
        "instruksi_pompa": instruksi_pompa
    }