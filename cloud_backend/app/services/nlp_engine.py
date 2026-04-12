import re
import json
import logging
import spacy
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CURRENT_DIR = Path(__file__).resolve().parent
MONOREPO_DIR = CURRENT_DIR.parent.parent.parent  
MODEL_PATH = MONOREPO_DIR / "ai_engine" / "models" / "fao56_model"
DATA_DIR = MONOREPO_DIR / "ai_engine" / "data" / "nlp_dataset"

class FAO56HybridEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FAO56HybridEngine, cls).__new__(cls)
            cls._instance._initialize_engine()
        return cls._instance

    def _initialize_engine(self):
        self.model_loaded = False
        self.nlp = None
        self.lokasi_firebase_map = {} # Pemetaan Lokasi -> Sinyal Firebase

        # 1. Muat Pemetaan Firebase dari lokasi.json
        try:
            with open(DATA_DIR / "lokasi.json", "r", encoding="utf-8") as f:
                data_lokasi = json.load(f).get("data", [])
                for item in data_lokasi:
                    self.lokasi_firebase_map[item["nama"].lower()] = item["firebase_signal"]
            logger.info("✅ Firebase Signal Mapping berhasil dimuat.")
        except Exception as e:
            logger.warning(f"⚠️ Gagal memuat lokasi.json: {e}")

        # 2. Muat Model AI SpaCy
        if MODEL_PATH.exists():
            try:
                self.nlp = spacy.load(MODEL_PATH)
                self.model_loaded = True
                logger.info("✅ Model AI (Komoditas & Lokasi) berhasil dimuat.")
            except Exception as e:
                logger.error(f"❌ Gagal memuat model SpaCy: {e}")

    def convert_to_hectares(self, text: str) -> float:
        """Regex Matematika untuk ekstraksi & konversi Luas Lahan (Satuan Internasional)."""
        unit_multipliers = {
            "hektar": 1.0, "ha": 1.0,
            "bata": 0.0014,   # 1 bata = 14 meter persegi = 0.0014 ha
            "tumbak": 0.0014,
            "ru": 0.0014,
            "bau": 0.7096,    # 1 bau = ~0.7 hektar
            "meter": 0.0001, "m2": 0.0001
        }
        
        # Mencari pola: (Angka/Desimal) + (Spasi Opsional) + (Satuan)
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*(hektar|ha|meter|m2|bata|tumbak|ru|bau)', text.lower())
        if match:
            angka = float(match.group(1).replace(',', '.'))
            satuan = match.group(2)
            multiplier = unit_multipliers.get(satuan, 1.0)
            # Dibulatkan 4 angka di belakang koma (Standar Database Internasional)
            return round(angka * multiplier, 4)
        return 0.0

    def extract_entities(self, text: str) -> Dict[str, Any]:
        hasil = {
            "komoditas": "Tidak Diketahui",
            "luas_lahan_ha": 0.0,
            "lokasi": "Tidak Diketahui",
            "firebase_signal": None,
            "confidence": 0.0
        }
        text_lower = text.lower()

        # ==========================================
        # 1. AI LAYER: Mengekstrak Komoditas & Lokasi
        # ==========================================
        if self.model_loaded and self.nlp:
            doc = self.nlp(text)
            
            komo_terdeteksi = [ent.text.title() for ent in doc.ents if ent.label_ == "KOMODITAS"]
            lokasi_terdeteksi = [ent.text.title() for ent in doc.ents if ent.label_ == "LOKASI"]
            
            if komo_terdeteksi:
                hasil["komoditas"] = komo_terdeteksi[0]
                hasil["confidence"] += 0.45
            
            if lokasi_terdeteksi:
                lok = lokasi_terdeteksi[0]
                hasil["lokasi"] = lok
                # Cocokkan dengan Sinyal Firebase
                hasil["firebase_signal"] = self.lokasi_firebase_map.get(lok.lower(), "SIGNAL-NOT-FOUND")
                hasil["confidence"] += 0.45

        # ==========================================
        # 2. HEURISTIC LAYER: Ekstraksi Luas (Satuan Internasional)
        # ==========================================
        hasil["luas_lahan_ha"] = self.convert_to_hectares(text_lower)
        if hasil["luas_lahan_ha"] > 0:
            hasil["confidence"] += 0.10

        hasil["confidence"] = round(min(hasil["confidence"], 0.99), 2)
        return hasil

nlp_processor = FAO56HybridEngine()

def process_farmer_input(text: str) -> Dict[str, Any]:
    logger.info(f"📡 Memproses Input Petani: '{text}'")
    hasil = nlp_processor.extract_entities(text)
    logger.info(f"Hasil Model FAO-56: {hasil}")
    return hasil