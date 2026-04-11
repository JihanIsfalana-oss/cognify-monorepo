import json
import random
import logging
from pathlib import Path
import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import warnings

# --- KONFIGURASI LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- MANAJEMEN PATH ---
CURRENT_DIR = Path(__file__).resolve().parent
AI_ENGINE_DIR = CURRENT_DIR.parent.parent  

DATA_PATH = AI_ENGINE_DIR / "data" / "nlp_dataset" / "jenis_tanaman.json"
OUTPUT_MODEL_DIR = AI_ENGINE_DIR / "models" / "fao56_model"

# --- AUGMENTASI DATA (KHUSUS INPUT LAHAN BARU) ---
# Menggenerate ribuan kalimat natural petani saat mendaftarkan lahan
FARMER_TEMPLATES = [
    "Saya mau buka lahan baru untuk tanam {}.",
    "Rencananya musim ini mau nanam {} seluas 2 hektar.",
    "Lahan di blok timur akan ditanami {} minggu depan.",
    "Kang, bibit {} yang tahan cuaca panas apa ya?",
    "Saya petani {} dari Indramayu.",
    "Persiapan bajak sawah untuk komoditas {} sudah selesai.",
    "Berapa estimasi kebutuhan pupuk urea untuk lahan {} 1 ha?",
    "Bulan depan saya mulai pindah tanam {}.",
    "Lahan 0.5 hektar ini khusus saya pakai buat {}.",
    "Sistem irigasi untuk {} bagusnya gimana?"
]

def load_and_augment_data(json_path: Path):
    """Membaca jenis_tanaman.json dan meracik dataset sintetis untuk training."""
    logger.info(f"Membaca dataset komoditas dari: {json_path}")
    
    if not json_path.exists():
        logger.error(f"File tidak ditemukan: {json_path}")
        return []

    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            logger.error("Format JSON tidak valid!")
            return []
    
    # Mengekstrak nama_umum dan varietas_populer
    crop_list = []
    items = data.get('data', [])
    
    for item in items:
        if isinstance(item, dict):
            # 1. Ambil Nama Umum (Misal: "Padi", "Jagung")
            if 'nama_umum' in item:
                crop_list.append(item['nama_umum'])
            
            # 2. Ambil Varietas agar AI makin jenius (Misal: "Inpari 32", "Ciherang")
            if 'varietas_populer' in item and isinstance(item['varietas_populer'], list):
                crop_list.extend(item['varietas_populer'])

    if not crop_list:
        logger.error("❌ Gagal mengekstrak nama tanaman.")
        return []

    # Filter duplikat dan bersihkan string kosong
    crop_list = list(set([c.strip() for c in crop_list if c.strip()]))
    logger.info(f"✅ Ditemukan {len(crop_list)} entitas komoditas/varietas. Memulai augmentasi...")

    training_data = []
    for crop in crop_list:
        for template in FARMER_TEMPLATES:
            text = template.format(crop)
            # Hitung index karakter untuk Entity KOMODITAS
            start_idx = text.find(crop)
            end_idx = start_idx + len(crop)
            
            training_data.append((text, {"entities": [(start_idx, end_idx, "KOMODITAS")]}))
    
    random.shuffle(training_data)
    logger.info(f"Dataset Input Lahan berhasil diracik! Total: {len(training_data)} kalimat.")
    return training_data

def train_ner(train_data, output_dir: Path, iterations: int = 30):
    """Arsitektur Training Neural Network untuk NLP SpaCy."""
    logger.info("Menginisialisasi arsitektur Model Bahasa Indonesia (id)...")
    nlp = spacy.blank("id")
    
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")
        
    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    logger.info(f"Memulai proses selama {iterations} epoch...")
    
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes), warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module='spacy')
        
        optimizer = nlp.begin_training()
        
        for itn in range(iterations):
            random.shuffle(train_data)
            losses = {}
            
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
            
            for batch in batches:
                examples = []
                for text, annotations in batch:
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    examples.append(example)
                
                nlp.update(
                    examples,
                    drop=0.2, # Mencegah model menghafal (overfitting)
                    sgd=optimizer,
                    losses=losses,
                )
            
            if (itn + 1) % 5 == 0 or (itn + 1) == iterations:
                logger.info(f"Epoch {itn+1:02d}/{iterations} selesai -> Loss: {losses['ner']:.4f}")

    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Menyimpan bobot model ke: {output_dir}")
    nlp.to_disk(output_dir)
    logger.info("✅ Training Selesai! siap digunakan.")

if __name__ == "__main__":
    print("="*60)
    print(" COGNIFY - NEW LAND REGISTRATION (NLP TRAINING) ".center(60))
    print("="*60)
    
    dataset = load_and_augment_data(DATA_PATH)
    
    if dataset:
        train_ner(dataset, OUTPUT_MODEL_DIR, iterations=30)