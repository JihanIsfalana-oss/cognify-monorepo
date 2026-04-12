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
DATA_DIR = AI_ENGINE_DIR / "data" / "nlp_dataset"
OUTPUT_MODEL_DIR = AI_ENGINE_DIR / "models" / "fao56_model" 

# --- TEMPLATE AUGMENTASI DATA (KOMBINASI KOMODITAS & LOKASI) ---
TEMPLATES = [
    "Saya mau buka lahan untuk tanam {komoditas} di daerah {lokasi}.",
    "Rencana bulan ini nanam {komoditas} di lahan wilayah {lokasi}.",
    "Sawah di {lokasi} sudah siap ditanami {komoditas}.",
    "Kang, butuh bibit {komoditas} untuk dikirim ke {lokasi}.",
    "Cuaca di {lokasi} lagi bagus buat mulai nanam {komoditas}.",
    "Persiapan bajak sawah komoditas {komoditas} daerah {lokasi}.",
    "Mau coba uji tanam {komoditas} di sentra pertanian {lokasi}."
]

def load_datasets():
    """Membaca dan mengekstrak entitasnya secara presisi."""
    komoditas_list = []
    lokasi_list = []

    # 1. Load Komoditas
    try:
        with open(DATA_DIR / "jenis_tanaman.json", 'r', encoding='utf-8') as f:
            data_k = json.load(f).get('data', [])
            # Mengambil gabungan Komoditas dan Varietas
            komoditas_list = [item['nama'] for item in data_k if 'nama' in item]
    except Exception as e:
        logger.error(f"Gagal memuat jenis_tanaman.json: {e}")

    # 2. Load Lokasi
    try:
        with open(DATA_DIR / "lokasi.json", 'r', encoding='utf-8') as f:
            data_l = json.load(f).get('data', [])
            lokasi_list = [item['nama'] for item in data_l if 'nama' in item]
    except Exception as e:
        logger.error(f"Gagal memuat lokasi.json: {e}")

    return komoditas_list, lokasi_list

def generate_training_data(komoditas_list, lokasi_list):
    """Meracik dataset silang (Cross-Product) dengan Kalkulasi Index Presisi Mutlak."""
    training_data = []
    
    for komo in komoditas_list:
        for lok in lokasi_list:
            for temp in TEMPLATES:
                # 1. Bentuk kalimat utuh
                text = temp.format(komoditas=komo, lokasi=lok)
                
                # 2. Kalkulasi Index Presisi Mutlak (Mencegah Bug .find())
                start_k = len(temp.split("{komoditas}")[0].format(lokasi=lok))
                start_l = len(temp.split("{lokasi}")[0].format(komoditas=komo))
                
                end_k = start_k + len(komo)
                end_l = start_l + len(lok)
                
                # 3. Validasi Keamanan Lapis Baja
                if max(start_k, start_l) < min(end_k, end_l):
                    logger.warning(f"Terdeteksi overlap di kalimat: {text}")
                    continue 
                    
                training_data.append((text, {"entities": [
                    (start_k, end_k, "KOMODITAS"),
                    (start_l, end_l, "LOKASI")
                ]}))
                
    random.shuffle(training_data)
    logger.info(f"✅ Dataset diracik dengan Index Presisi! Total kombinasi: {len(training_data)} kalimat.")
    return training_data

def train_ner(train_data, output_dir: Path, iterations: int = 30):
    logger.info("Inisialisasi Model FAO-56...")
    nlp = spacy.blank("id")
    ner = nlp.add_pipe("ner", last=True) if "ner" not in nlp.pipe_names else nlp.get_pipe("ner")
        
    ner.add_label("KOMODITAS")
    ner.add_label("LOKASI")

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes), warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module='spacy')
        optimizer = nlp.begin_training()
        
        for itn in range(iterations):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
            
            for batch in batches:
                examples = [Example.from_dict(nlp.make_doc(text), annots) for text, annots in batch]
                nlp.update(examples, drop=0.2, sgd=optimizer, losses=losses)
            
            if (itn + 1) % 5 == 0 or (itn + 1) == iterations:
                logger.info(f"Epoch {itn+1:02d}/{iterations} Selesai | Loss: {losses['ner']:.4f}")

    output_dir.mkdir(parents=True, exist_ok=True)
    nlp.to_disk(output_dir)
    logger.info("✅ Training Selesai! Model FAO-56 telah siap.")

if __name__ == "__main__":
    komo_data, lok_data = load_datasets()
    if komo_data and lok_data:
        dataset = generate_training_data(komo_data, lok_data)
        train_ner(dataset, OUTPUT_MODEL_DIR, iterations=30)