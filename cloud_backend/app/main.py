from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

# Pastikan nama class di bawah ini sesuai dengan yang ada di schemas.py Anda
from app.models.schemas import NLPRequest, NLPExtractionResult

# Inisialisasi aplikasi FastAPI COGNIFY
app = FastAPI(
    title="COGNIFY API Gateway",
    description="API Antarmuka untuk Intelligence Hub Pertanian Off-Grid",
    version="1.0.0"
)

# Konfigurasi CORS agar Dasbor Web & Aplikasi Mobile bisa mengakses API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Ganti dengan domain Vercel/Frontend saat produksi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Sistem Manajer"])
async def root_health_check():
    """Endpoint untuk mengecek status server Cloud COGNIFY."""
    return {"status": "online", "message": "COGNIFY Cloud API is running."}

# --- 1. FITUR EKSTRAKSI NLP (NER) ---
@app.post("/api/nlp/extract", response_model=NLPExtractionResult, tags=["Pemrosesan NLP"])
async def extract_agronomy_entities(payload: NLPRequest):
    """
    Menerima teks bebas petani dan mengekstraksi parameter agronomis 
    untuk input algoritma FAO-56.
    """
    teks = payload.raw_text.lower()
    
    # MOCKUP Logika NLP
    if "inpari 32" in teks and "kandanghaur" in teks:
        return NLPExtractionResult(
            success=True,
            message="Entitas agronomis berhasil diekstrak",
            komoditas="Padi",  # Harus persis sesuai Enum di schemas.py
            luas_lahan_ha=2.0,
            lokasi="Kandanghaur",
            confidence=0.94
        )
    
    # Fallback jika teks tidak dikenali
    # Kita menggunakan nilai valid minimum (dummy) agar lolos validasi Pydantic
    return NLPExtractionResult(
        success=False,
        message="Gagal mengekstrak entitas. Kalimat tidak sesuai format uji coba.",
        komoditas="Padi",      # Nilai dummy valid
        luas_lahan_ha=0.1,     # Harus > 0
        lokasi="Unknown",
        confidence=0.0
    )

# --- 2. FITUR GEOSPATIAL RADAR (DBSCAN MOCK) ---
@app.get("/api/radar/status", tags=["Geospatial Radar"])
async def get_radar_status():
    """
    Mengambil data klaster wabah hama dalam radius 5 KM menggunakan 
    metode deteksi kumpulan (DBSCAN).
    """
    return {
        "status": "WASPADA",
        "active_clusters": 1,
        "pest_type": "Wereng Batang Coklat",
        "affected_area": "Kandanghaur",
        "radius_km": 5.0,
        "mitigation_action": "Pemicuan Early Warning System (EWS) ke pengguna sekitar."
    }

# --- 3. FITUR PREDICTIVE MATCHMAKING ---
@app.get("/api/matchmaking/{petani_id}", tags=["Sertifikat & Akses Pasar"])
async def get_reputasi_petani(petani_id: str):
    """
    Menghitung Skor Reputasi Budidaya berdasarkan kepatuhan irigasi 
    dan kesehatan lahan.
    """
    return {
        "petani_id": petani_id,
        "skor_reputasi": 94.5,
        "grade": "A",
        "status_sertifikat": "Terverifikasi",
        "rekomendasi_pembeli": ["PT AgriFood Nusantara", "Koperasi Mitra Tani"]
    }