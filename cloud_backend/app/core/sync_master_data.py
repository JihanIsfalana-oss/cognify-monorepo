# cloud_backend/app/core/sync_master_data.py

import json
from pathlib import Path
from firebase import db

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "ai_engine" / "data" / "nlp_dataset"

def sync_json_to_firebase(json_filename: str, collection_name: str):
    print(f"[COGNIFY] Memulai sinkronisasi {json_filename} ke koleksi '{collection_name}'...")
    
    file_path = DATA_DIR / json_filename
    if not file_path.exists():
        print(f"❌ Error: File {json_filename} tidak ditemukan di {file_path}")
        return

    # Baca file JSON lokal
    with open(file_path, "r", encoding="utf-8") as f:
        data_json = json.load(f).get("data", [])

    # Upload ke Firebase secara Batch untuk efisiensi
    batch = db.batch()
    collection_ref = db.collection(collection_name)

    count = 0
    for item in data_json:
        # Gunakan nama sebagai ID Dokumen agar tidak duplikat (opsional)
        doc_id = item.get("nama", f"auto_id_{count}").replace(" ", "_").lower()
        doc_ref = collection_ref.document(doc_id)
        batch.set(doc_ref, item, merge=True) # merge=True agar tidak menimpa data lain yang ada
        count += 1

    # Eksekusi Batch
    batch.commit()
    print(f"✅ Sukses! {count} data dari {json_filename} berhasil di-push ke Firebase Firestore.")

if __name__ == "__main__":
    print("[COGNIFY] Memulai Sinkronisasi Master Data...")
    
    # 1. Sync Komoditas & Varietas
    sync_json_to_firebase("jenis_tanaman.json", "master_komoditas")
    
    # 2. Sync Lokasi & Firebase Signal
    sync_json_to_firebase("lokasi.json", "master_lokasi")
    
    print("Seluruh Master Data telah tersinkronisasi dengan (Cloud)!")