# ai_engine/src/convert_to_openvino.py
import os
from ultralytics import YOLO

def export_pest_model():
    print("[COGNIFY] Inisialisasi Edge AI Engine...")
    
    # 1. Tentukan path model
    model_name = "yolov8n.pt"
    
    print(f"[COGNIFY] Memuat model {model_name}...")
    model = YOLO(model_name)
    
    print("[COGNIFY] Memulai kompilasi ke Arsitektur Intel OpenVINO...")
    # 2. Proses Konversi (Export)
    exported_path = model.export(
        format="openvino", 
        half=True,  
        optimize=True,
        imgsz=640
    )
    
    print(f"[COGNIFY] Konversi Sukses!")
    print(f"File OpenVINO tersimpan di: {exported_path}")

if __name__ == "__main__":
    export_pest_model()