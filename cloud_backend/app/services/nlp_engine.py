# cloud_backend/app/services/nlp_engine.py

import re
import logging
import spacy
from pathlib import Path
from typing import Dict, Any

# --- KONFIGURASI LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- MANAJEMEN PATH (MONOREPO ARCHITECTURE) ---
CURRENT_DIR = Path(__file__).resolve().parent
MONOREPO_DIR = CURRENT_DIR.parent.parent.parent  
MODEL_PATH = MONOREPO_DIR / "ai_engine" / "models" / "fao56_model"

class FAO56NLPEngine:
    """
    Singleton Class untuk NLP Engine COGNIFY.
    Memastikan model SpaCy hanya di-load 1 kali ke dalam memori RAM saat server menyala,
    mencegah memory leak dan mempercepat inferensi hingga < 50ms per request.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FAO56NLPEngine, cls).__new__(cls)
            cls._instance._initialize_engine()
        return cls._instance

    def _initialize_engine(self):
        """Memuat model AI dari sistem file."""
        self.model_loaded = False
        self.nlp = None

        logger.info("Mencoba memuat Model AI FAO-56 NER...")
        if MODEL_PATH.exists():
            try:
                self.nlp = spacy.load(MODEL_PATH)
                self.model_loaded = True
                logger.info(f"✅ Model NER berhasil dimuat dari: {MODEL_PATH}")
            except Exception as e:
                logger.error(f"❌ Gagal memuat model SpaCy: {e}")
        else:
            logger.warning(f"Direktori model tidak ditemukan di {MODEL_PATH}!")
            logger.warning("Sistem akan berjalan menggunakan Regex/Heuristik sebagai Fallback (Plan B).")

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Fungsi utama (Inference) untuk membedah teks petani.
        Menggabungkan Deep Learning (SpaCy) untuk Hama, dan Regex canggih untuk Luas & Lokasi.
        """
        # 1. Parameter Default
        hasil = {
            "komoditas": None,
            "varietas": "Standar",
            "hama": None,
            "luas_lahan_ha": 0.0,
            "lokasi": None,
            "confidence": 0.0
        }
        
        text_lower = text.lower()
        confidence_score = 0.5 # Base score

        # ==========================================
        # FASE 1: DEEP LEARNING (Mendeteksi KOMODITAS)
        # ==========================================
        if self.model_loaded and self.nlp:
            doc = self.nlp(text)

            komoditas_terdeteksi = [ent.text for ent in doc.ents if ent.label_ == "KOMODITAS"]
            
            if komoditas_terdeteksi:
                hasil["komoditas"] = komoditas_terdeteksi[0].title()
                confidence_score += 0.35  
                logger.info(f"AI Model FAO-56 Mendeteksi Komoditas: {hasil['komoditas']}")

        # ==========================================
        # FASE 2: PATTERN RECOGNITION & FALLBACK
        # ==========================================
        
        # A. Fallback Heuristik untuk Komoditas (Hanya jalan jika AI gagal)
        if not hasil["komoditas"]:
            if "padi" in text_lower or "beras" in text_lower:
                hasil["komoditas"] = "Padi"
                confidence_score += 0.1
            elif "cabe" in text_lower or "cabai" in text_lower:
                hasil["komoditas"] = "Cabai"
                confidence_score += 0.1
            elif "jagung" in text_lower:
                hasil["komoditas"] = "Jagung"
                confidence_score += 0.1
            if hasil["komoditas"]:
                logger.info(f"Fallback Regex Mendeteksi Komoditas: {hasil['komoditas']}")

        # B. Ekstraksi Varietas (Terpisah dari Komoditas agar AI tidak tertimpa)
        if hasil["komoditas"]:
            komo_cek = hasil["komoditas"].lower()
            if "padi" in komo_cek:
                if "inpari" in text_lower: hasil["varietas"] = "Inpari 32"
                elif "ciherang" in text_lower: hasil["varietas"] = "Ciherang"
            elif "caba" in komo_cek or "cabe" in komo_cek:
                if "rawit" in text_lower: hasil["varietas"] = "Rawit Merah"

        # C. Ekstraksi Hama (Karena model khusus Komoditas, Hama pakai Regex murni)
        hama_umum = ["wereng", "tikus", "penggerek batang", "antraknosa", "kutu daun", "ulat grayak"]
        for h in hama_umum:
            if h in text_lower:
                hasil["hama"] = h.title()
                confidence_score += 0.15
                logger.info(f"Fallback Regex Mendeteksi Hama: {hasil['hama']}")
                break

        # D. Ekstraksi Luas Lahan (Support format desimal dan berbagai satuan)
        luas_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(hektar|ha|meter|m2|bata|ru)', text_lower)
        if luas_match:
            angka = float(luas_match.group(1).replace(',', '.'))
            satuan = luas_match.group(2)
            
            # Normalisasi ke Hektar (Standar FAO-56)
            if satuan in ['hektar', 'ha']:
                hasil["luas_lahan_ha"] = angka
            elif satuan in ['meter', 'm2']:
                hasil["luas_lahan_ha"] = angka / 10000.0
            elif satuan == 'bata':
                hasil["luas_lahan_ha"] = angka * 14 / 10000.0 # 1 bata lokal jabar = ~14m2
                
            confidence_score += 0.1

        # E. Ekstraksi Lokasi
        lokasi_match = re.search(r'(?:di|daerah|desa|kecamatan|kec|kabupaten|kab|kota|wilayah)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})', text_lower)
        if lokasi_match:
            lokasi_raw = lokasi_match.group(1).strip()
            kata_kotor = ["yang", "dan", "terkena", "kena", "banyak", "luas"]
            lokasi_bersih = " ".join([w for w in lokasi_raw.split() if w.lower() not in kata_kotor])
            
            if len(lokasi_bersih) > 2:
                hasil["lokasi"] = lokasi_bersih.title()
                confidence_score += 0.1

        # Finalisasi Confidence (Max 0.99)
        hasil["confidence"] = round(min(confidence_score, 0.99), 2)
        
        return hasil

# ==========================================
# INISIALISASI INSTANCE & FUNGSI WRAPPER API
# ==========================================
nlp_processor = FAO56NLPEngine()

def process_farmer_input(text: str) -> Dict[str, Any]:
    """
    Fungsi antarmuka (wrapper) yang akan dipanggil oleh router di main.py.
    Menyembunyikan kompleksitas OOP dari endpoint.
    """
    logger.info(f"Menerima input dari Frontend: '{text}'")
    hasil = nlp_processor.extract_entities(text)
    logger.info(f"Output Ekstraksi: {hasil}")
    return hasil