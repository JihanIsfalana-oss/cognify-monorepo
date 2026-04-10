import json
import random
import logging
from pathlib import Path
import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import warnings

# --- KONFIGURASI LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s -  %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CURRENT_DIR = Path(__file__).resolve().parent
AI_ENGINE_DIR = CURRENT_DIR.parent.parent  

# Lokasi file dataset dan tempat menyimpan model
DATA_PATH = AI_ENGINE_DIR / "data" / "Pesttype.json"
OUTPUT_MODEL_DIR = AI_ENGINE_DIR / "models" / "fao56_ner_model"

# --- AUGMENTASI DATA (SYNTHETIC DATASET GENERATOR) ---
FARMER_TEMPLATES = [
    "Kang, lahan saya terkena wabah {}.",
    "Ada serangan {} di blok timur, parah banget.",
    "Pestisida yang cocok buat {} apa ya?",
    "Daun padi saya menguning, sepertinya gara-gara {}.",
    "Bulan ini {} lagi musim di desa kami.",
    "Tolong analisis gejala {} pada tanaman jagung.",
    "Bagaimana mitigasi awal untuk {}?",
    "Kemarin saya lihat banyak {} nempel di batang.",
    "Lahan 2 hektar habis dimakan {} dalam semalam.",
    "Obat sistemik untuk {} harganya berapa?"
]

def load_and_augment_data(json_path: Path):
    """Membaca Pesttype.json dan meracik ribuan dataset sintetis untuk training."""
    logger.info(f"Membaca dataset dari: {json_path}")
    
    if not json_path.exists():
        logger.error(f"File tidak ditemukan: {json_path}")
        logger.error("Pastikan nama file benar (perhatikan huruf besar/kecil 'Pesttype.json').")
        return []

    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            logger.error("Format JSON tidak valid!")
            return []
    
    pest_list = []
    items = data.get('data', data) if isinstance(data, dict) else data
    
    for item in items:
        if isinstance(item, dict) and 'nama' in item:
            pest_list.append(item['nama'])
        elif isinstance(item, str):
            pest_list.append(item)

    if not pest_list:
        logger.error("Gagal mengekstrak nama hama dari JSON.")
        return []

    logger.info(f"Ditemukan {len(pest_list)} entitas hama. Memulai augmentasi...")

    training_data = []
    for pest in pest_list:
        for template in FARMER_TEMPLATES:
            text = template.format(pest)
            # Hitung index karakter untuk Entity HAMA
            start_idx = text.find(pest)
            end_idx = start_idx + len(pest)
            
            # Format SpaCy V3: (text, {"entities": [(start, end, label)]})
            training_data.append((text, {"entities": [(start_idx, end_idx, "HAMA")]}))
    
    # Acak dataset agar model tidak menghafal urutan
    random.shuffle(training_data)
    logger.info(f"Dataset berhasil diracik! Total: {len(training_data)} kalimat.")
    return training_data

def train_ner(train_data, output_dir: Path, iterations: int = 35):
    """Arsitektur Training Neural Network untuk NLP."""
    logger.info("Menginisialisasi arsitektur Model Bahasa Indonesia (id)...")
    nlp = spacy.blank("id")
    
    # Tambahkan 'ner' ke pipeline jika belum ada
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")
        
    # Daftarkan label entitas ke arsitektur jaringan
    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    logger.info(f"Memulai proses Deep Learning selama {iterations} epoch...")
    
    # Matikan pipeline lain agar fokus hanya pada NER
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes), warnings.catch_warnings():
        warnings.filterwarning("ignore", category=UserWarning, module='spacy')
        
        optimizer = nlp.begin_training()
        
        for itn in range(iterations):
            random.shuffle(train_data)
            losses = {}
            
            # Penggunaan Minibatch yang dinamis (membesar eksponensial)
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
            
            for batch in batches:
                examples = []
                for text, annotations in batch:
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    examples.append(example)
                
                # Update bobot (weights) dengan sistem Dropout 0.2 untuk mencegah overfitting
                nlp.update(
                    examples,
                    drop=0.2,
                    sgd=optimizer,
                    losses=losses,
                )
            
            # Tampilkan progress setiap 5 epoch
            if (itn + 1) % 5 == 0 or (itn + 1) == iterations:
                logger.info(f"Epoch {itn+1:02d}/{iterations} selesai -> Loss: {losses['ner']:.4f}")

    # Buat direktori jika belum ada dan simpan model
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Menyimpan bobot model ke: {output_dir}")
    nlp.to_disk(output_dir)
    logger.info("✅ Training Selesai! Model FAO-56 siap diintegrasikan.")

if __name__ == "__main__":
    print("="*60)
    print(" COGNIFY - FAO-56 NLP ENGINE TRAINING SCRIPT ".center(60))
    print("="*60)
    
    dataset = load_and_augment_data(DATA_PATH)
    
    if dataset:
        train_ner(dataset, OUTPUT_MODEL_DIR, iterations=35)