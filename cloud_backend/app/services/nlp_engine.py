# cloud_backend/app/services/nlp_engine.py
import spacy
from spacy.pipeline import EntityRuler
import json
import re
from pathlib import Path

# --- 1. LOAD KNOWLEDGE BASE (JSON) ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

with open(DATA_DIR / "jenis_tanaman.json", "r", encoding="utf-8") as f:
    CROP_DB = json.load(f)["data"]

with open(DATA_DIR / "pest_types.json", "r", encoding="utf-8") as f:
    PEST_DB = json.load(f)["data"]

# --- 2. INISIALISASI SPACY NLP (Bahasa Indonesia Blank Model) ---
# Kita pakai model kosong agar ringan dan super cepat, lalu kita isi dengan aturan kita sendiri
nlp = spacy.blank("id")
ruler = nlp.add_pipe("entity_ruler")

patterns = []

# --- 3. INJEKSI DATA CROP & PEST KE DALAM OTAK AI (NER PATTERNS) ---
for crop in CROP_DB:
    # Daftarkan Nama Umum (CROP)
    patterns.append({"label": "CROP", "pattern": [{"LOWER": word.lower()} for word in crop["nama_umum"].split()]})
    # Daftarkan Varietas Spesifik (VARIETY)
    for varietas in crop["varietas_populer"]:
         patterns.append({"label": "VARIETY", "pattern": [{"LOWER": word.lower()} for word in varietas.split()]})

for pest in PEST_DB:
    # Daftarkan Hama (PEST)
    patterns.append({"label": "PEST", "pattern": [{"LOWER": word.lower()} for word in pest["nama_umum"].split()]})

ruler.add_patterns(patterns)

# --- 4. FUNGSI EKSTRAKSI UTAMA ---
def process_farmer_input(text: str):
    """
    Menganalisis teks natural dari petani dan mengekstrak entitas penting (NER).
    """
    doc = nlp(text)
    
    # Tempat penampungan hasil ekstraksi
    extracted = {
        "komoditas": None,
        "varietas": None,
        "hama": None,
        "luas_lahan_ha": 0.0,
        "lokasi": "Tidak Diketahui",
        "confidence": 0.0
    }
    
    # 1. Ekstraksi Entitas Agrikultur menggunakan spacy NER
    for ent in doc.ents:
        if ent.label_ == "CROP" and not extracted["komoditas"]:
            extracted["komoditas"] = ent.text.title()
            extracted["confidence"] = 0.85
        elif ent.label_ == "VARIETY":
            extracted["varietas"] = ent.text.title()
            extracted["confidence"] = 0.95 # Confidence naik karena varietas spesifik
        elif ent.label_ == "PEST":
            extracted["hama"] = ent.text.title()

    # Logika Cerdas: Jika varietas terdeteksi tapi komoditas kosong, cari induknya di JSON
    if extracted["varietas"] and not extracted["komoditas"]:
        for crop in CROP_DB:
            if extracted["varietas"].lower() in [v.lower() for v in crop["varietas_populer"]]:
                extracted["komoditas"] = crop["nama_umum"]
                break

    # 2. Ekstraksi Luas Lahan (Regex Pengejaran Angka + Kata Hektar/Ha/Bata)
    # Contoh: "1.5 hektar", "2 ha", "100 bata"
    area_match = re.search(r'(\d+(?:\.\d+)?)\s*(hektar|ha|bata)', text, re.IGNORECASE)
    if area_match:
        angka = float(area_match.group(1))
        satuan = area_match.group(2).lower()
        if satuan == 'bata':
            extracted["luas_lahan_ha"] = angka * 0.0014 # 1 bata = 14 meter persegi
        else:
            extracted["luas_lahan_ha"] = angka

    # 3. Ekstraksi Lokasi (Regex sederhana setelah kata "di", "desa", "kecamatan")
    loc_match = re.search(r'(?:di\s+desa|di\s+kecamatan|di)\s+([A-Za-z\s]+)(?:[,.]|$)', text, re.IGNORECASE)
    if loc_match:
        # Mengambil 2 kata pertama setelah preposisi sebagai lokasi
        words = loc_match.group(1).strip().split()
        extracted["lokasi"] = " ".join(words[:2]).title()

    return extracted