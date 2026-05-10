# cloud_backend/app/services/nlp_engine.py

import re
import json
import logging
import spacy
from typing import Dict, Any
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        self.lokasi_firebase_map = {} 
        self.valid_locations = []
        
        # Base komoditas default sebagai pengaman
        valid_set = {"padi", "jagung", "cabai", "bawang merah", "bawang putih", "kedelai", "tomat", "kentang"}

        # 1. Muat Pemetaan Firebase & Daftar Lokasi (via config.py)
        try:
            with open(settings.LOKASI_JSON, "r", encoding="utf-8") as f:
                data_lokasi = json.load(f).get("data", [])
                for item in data_lokasi:
                    nama_lok = item["nama"].lower()
                    self.lokasi_firebase_map[nama_lok] = item["firebase_signal"]
                    self.valid_locations.append(nama_lok)
            
            # Urutkan lokasi dari terpanjang ke terpendek agar pencocokan lebih akurat
            self.valid_locations = sorted(self.valid_locations, key=len, reverse=True)
            logger.info("✅ Firebase Signal Mapping & Valid Locations berhasil dimuat.")
        except Exception as e:
            logger.warning(f"⚠️ Gagal memuat lokasi.json: {e}")

        # 2. Muat Database Tanaman (via config.py)
        try:
            with open(settings.TANAMAN_JSON, "r", encoding="utf-8") as f:
                data_tanaman = json.load(f).get("data", [])
                for item in data_tanaman:
                    if isinstance(item, dict):
                        if "komoditas" in item:
                            valid_set.add(item["komoditas"].lower())
                        if "nama" in item:
                            valid_set.add(item["nama"].lower())
            
            self.valid_crops = sorted(list(valid_set), key=len, reverse=True)
            logger.info("✅ Valid Database berhasil dimuat.")
        except Exception as e:
            self.valid_crops = sorted(list(valid_set), key=len, reverse=True)
            logger.warning(f"⚠️ Gagal memuat jenis_tanaman.json: {e}")

        # 3. Muat Model AI SpaCy
        model_path = settings.AI_MODEL_DIR / "fao56_model"
        if model_path.exists():
            try:
                self.nlp = spacy.load(model_path)
                self.model_loaded = True
                logger.info("✅ Model FAO-56 berhasil dimuat.")
            except Exception as e:
                logger.error(f"❌ Gagal memuat model SpaCy: {e}")

    def convert_to_hectares(self, text: str) -> float:
        """Regex Matematika untuk ekstraksi & konversi Luas Lahan (Satuan Internasional)."""
        unit_multipliers = {
            "hektar": 1.0, "ha": 1.0,
            "bata": 0.0014,   
            "tumbak": 0.0014,
            "ru": 0.0014,
            "bau": 0.7096,    
            "meter": 0.0001, "m2": 0.0001
        }
        
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*(hektar|ha|meter|m2|bata|tumbak|ru|bau)', text.lower())
        if match:
            angka = float(match.group(1).replace(',', '.'))
            satuan = match.group(2)
            multiplier = unit_multipliers.get(satuan, 1.0)
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
        # 1. HEURISTIC LAYER: Validasi Komoditas & Lokasi Cerdas
        # ==========================================
        komoditas_pasti = None
        for crop in self.valid_crops:
            if re.search(rf'\b{crop}\b', text_lower):
                komoditas_pasti = crop.title()
                break
                
        lokasi_pasti = None
        for lok in self.valid_locations:
            if re.search(rf'\b{lok}\b', text_lower):
                lokasi_pasti = lok.title()
                break

        # ==========================================
        # 2. AI LAYER: Ekstraksi Lokasi & Fallback Model
        # ==========================================
        if self.model_loaded and self.nlp:
            doc = self.nlp(text)
            
            # --- EVALUASI KOMODITAS ---
            if komoditas_pasti:
                hasil["komoditas"] = komoditas_pasti
                hasil["confidence"] += 0.45
            else:
                komo_terdeteksi = [ent.text.title() for ent in doc.ents if ent.label_ == "KOMODITAS"]
                if komo_terdeteksi:
                    anomali = ["saya", "kami", "kita", "menanam", "ingin", "punya", "ada"]
                    tebakan = komo_terdeteksi[0]
                    if not any(x in tebakan.lower() for x in anomali):
                        hasil["komoditas"] = tebakan
                        hasil["confidence"] += 0.20

            # --- EVALUASI LOKASI ---
            if lokasi_pasti:
                hasil["lokasi"] = lokasi_pasti
                hasil["firebase_signal"] = self.lokasi_firebase_map.get(lokasi_pasti.lower(), "SIGNAL-NOT-FOUND")
                hasil["confidence"] += 0.45
            else:
                lokasi_terdeteksi = [ent.text.title() for ent in doc.ents if ent.label_ == "LOKASI"]
                if lokasi_terdeteksi:
                    # Filter Anti-Halusinasi Angka
                    for lok_tebakan in lokasi_terdeteksi:
                        if not re.fullmatch(r'\d+', lok_tebakan) and len(lok_tebakan) > 2:
                            hasil["lokasi"] = lok_tebakan
                            hasil["firebase_signal"] = self.lokasi_firebase_map.get(lok_tebakan.lower(), "SIGNAL-NOT-FOUND")
                            hasil["confidence"] += 0.45
                            break

        # ==========================================
        # 3. MATH LAYER: Ekstraksi Luas 
        # ==========================================
        hasil["luas_lahan_ha"] = self.convert_to_hectares(text_lower)
        if hasil["luas_lahan_ha"] > 0:
            hasil["confidence"] += 0.10

        # ==========================================
        # 4. PENALTY SCORING
        # ==========================================
        if hasil["firebase_signal"] == "SIGNAL-NOT-FOUND" and hasil["lokasi"] != "Tidak Diketahui":
            hasil["confidence"] = max(0.0, hasil["confidence"] - 0.25)
            
        hasil["confidence"] = round(min(hasil["confidence"], 0.99), 2)
        return hasil

nlp_processor = FAO56HybridEngine()

def process_farmer_input(text: str) -> Dict[str, Any]:
    logger.info(f"📡 Memproses Input Petani: '{text}'")
    hasil = nlp_processor.extract_entities(text)
    logger.info(f"Hasil Model FAO-56: {hasil}")
    return hasil