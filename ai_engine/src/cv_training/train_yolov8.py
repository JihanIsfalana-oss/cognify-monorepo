# ai_engine/src/cv_training/train_yolov8.py

import os
import logging
from pathlib import Path
from ultralytics import YOLO
import torch

# --- KONFIGURASI LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - 👁️ %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- SETUP PATH ---
CURRENT_DIR = Path(__file__).resolve().parent
AI_ENGINE_DIR = CURRENT_DIR.parent.parent

DATASET_YAML_PATH = AI_ENGINE_DIR / "data" / "cv_dataset" / "dataset.yaml"
OUTPUT_MODEL_DIR = AI_ENGINE_DIR / "models" / "cv_models"

def setup_environment():
    """Mengecek ketersediaan GPU untuk akselerasi training."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        logger.info(f"GPU Terdeteksi: {torch.cuda.get_device_name(0)}")
        logger.info("Training akan diakselerasi menggunakan CUDA.")
    else:
        logger.warning("Tidak ada GPU terdeteksi. Menggunakan CPU (akan memakan waktu lebih lama).")
    return device

def train_yolov8_model(data_path: Path, output_dir: Path, epochs: int = 50, imgsz: int = 640):
    """
    Arsitektur Training YOLOv8 untuk Deteksi Hama (Computer Vision).
    Menggunakan pre-trained nano model (yolov8n.pt) untuk performa cepat di Edge.
    """
    if not data_path.exists():
        logger.error(f"File konfigurasi dataset tidak ditemukan di: {data_path}")
        logger.error("Pastikan Anda sudah menyiapkan foto dan file dataset.yaml")
        return

    device = setup_environment()
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Memuat model dasar YOLOv8n (Nano)...")
    model = YOLO("yolov8n.pt") 

    logger.info(f"Memulai proses Deep Learning CV selama {epochs} epoch...")
    
    # --- PROSES TRAINING ---
    results = model.train(
        data=str(data_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=16,         
        device=device,
        project=str(output_dir),
        name="hama_detector_v1",
        exist_ok=True,
        patience=10,       # Early stopping jika model tidak berkembang selama 10 epoch
        optimizer='auto',
        verbose=True
    )

    logger.info(f"Training selesai! Metrik Evaluasi mAP50-95: {results.box.map:.4f}")

    # --- VALIDASI & EXPORT KE OPENVINO ---
    logger.info("Melakukan validasi akhir pada dataset validasi...")
    model.val()

    logger.info("Mengonversi bobot PyTorch (.pt) ke format Intel OpenVINO (.xml/.bin)...")
    export_path = model.export(
        format="openvino", 
        half=True,  # FP16 quantization untuk mempercepat inferensi di Edge
        int8=False  
    )
    
    logger.info(f"Konversi berhasil! Model OpenVINO tersimpan di: {export_path}")
    logger.info("Model ini siap ditanamkan ke dalam arsitektur Edge Runtime.")

if __name__ == "__main__":
    print("="*60)
    print(" COGNIFY - COMPUTER VISION (YOLOv8) TRAINING SCRIPT ".center(60))
    print("="*60)
    
    train_yolov8_model(DATASET_YAML_PATH, OUTPUT_MODEL_DIR, epochs=50)