from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import json
import os
from pathlib import Path

# Import skema Pydantic Anda
from app.models.schemas import NLPRequest, NLPExtractionResult, TelemetryData

# --- SETUP PATH & LOAD DATA JSON ---
# Mencari rute folder saat ini agar tidak error saat di-deploy
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Memuat Database ke Memori (RAM) saat Server Startup
with open(DATA_DIR / "jenis_tanaman.json", "r", encoding="utf-8") as f:
    CROP_DB = json.load(f)["data"]

with open(DATA_DIR / "pest_types.json", "r", encoding="utf-8") as f:
    PEST_DB = json.load(f)["data"]


# Inisialisasi aplikasi
app = FastAPI(title="COGNIFY API Gateway", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Sistem Manajer"])
async def root_health_check():
    return {"status": "online", "message": "COGNIFY Online!", "total_crops": len(CROP_DB)}

# --- 1. FITUR EKSTRAKSI NLP (NER) DINAMIS ---
@app.post("/api/nlp/extract", response_model=NLPExtractionResult, tags=["Pemrosesan NLP"])
async def extract_agronomy_entities(payload: NLPRequest):
    """
    Menerima teks petani dan MENCARI kecocokannya di dalam database jenis_tanaman.json
    """
    teks = payload.raw_text.lower()
    
    detected_crop_name = None
    confidence_score = 0.0
    
    # LOGIKA PENCARIAN AI (Pattern Matching Engine)
    for crop in CROP_DB:
        # 1. Cek apakah nama umum disebut (contoh: "padi", "bawang")
        if crop["nama_umum"].lower() in teks:
            detected_crop_name = crop["nama_umum"]
            confidence_score = 0.85
            
        # 2. Cek apakah varietas spesifik disebut (contoh: "inpari 32", "bisi 18")
        # Ini akan menimpa confidence menjadi lebih tinggi karena spesifik
        for varietas in crop["varietas_populer"]:
            if varietas.lower() in teks:
                detected_crop_name = crop["nama_umum"] # Tetap simpan nama induknya
                confidence_score = 0.98
                break 

        if detected_crop_name and confidence_score == 0.98:
            break # Hentikan pencarian jika sudah ketemu varietas spesifik

    # Jika AI menemukan komoditas di dalam JSON
    if detected_crop_name:
        return NLPExtractionResult(
            success=True,
            message=f"Mendeteksi komoditas {detected_crop_name}. Mengambil data FAO-56 untuk kalkulasi...",
            komoditas=detected_crop_name,
            luas_lahan_ha=2.0, # (Masih mockup statis untuk luas)
            lokasi="Kandanghaur", # (Masih mockup statis untuk lokasi)
            confidence=confidence_score
        )
    
    # Jika tidak ada kecocokan di database
    return NLPExtractionResult(
        success=False,
        message="Gagal mengekstrak. Komoditas tidak ditemukan di Database Nasional.",
        komoditas="Tidak Diketahui",
        luas_lahan_ha=0.1,
        lokasi="Unknown",
        confidence=0.0
    )

# --- 2. ENDPOINT BARU UNTUK FRONTEND (Opsional tapi Kuat) ---
@app.get("/api/data/hama", tags=["Database API"])
async def get_all_pests():
    """Mengirim seluruh data hama ke Frontend untuk ditampilkan di tabel/peta"""
    return {"success": True, "data": PEST_DB}

# --- 3. ENDPOINT IOT TELEMETRI (ESP32) ---
@app.post("/api/iot/telemetry", tags=["IoT Telemetri"])
async def receive_telemetry(data: TelemetryData):
    """
    Endpoint sederhana untuk menerima data sensor dari ESP32 (Slave Node).
    """
    # Mencetak data yang masuk ke terminal server
    print(f"\n📡 [IoT Terhubung] Data masuk dari perangkat: {data.device_id}")
    print(f"   🌱 Kelembapan Tanah : {data.kelembapan_tanah}%")
    print(f"   🌡️ Suhu Lingkungan  : {data.suhu_lingkungan}°C")
    print(f"   🧪 pH Tanah         : {data.ph_tanah}")
    
    # --- LOGIKA KEPUTUSAN SEDERHANA ---
    # Jika kelembapan tanah di bawah 40%, perintahkan ESP32 menyalakan pompa air
    instruksi_pompa = "ON" if data.kelembapan_tanah < 40.0 else "OFF"
    
    if instruksi_pompa == "ON":
        print("   ⚠️ Peringatan: Tanah kering! Mengirim instruksi POMPA ON ke ESP32.")

    # Mengembalikan respons ke ESP32
    return {
        "success": True,
        "message": "Data telemetri berhasil direkam oleh server",
        "timestamp": "Real-time",
        "instruksi_pompa": instruksi_pompa
    }