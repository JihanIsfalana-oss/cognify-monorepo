# cloud_backend/app/services/fao56_integrator.py

import re
from typing import Dict, Any

class FAO56Integrator:
    """
    Sistem Integrasi yang menggabungkan 3 Model AI:
    1. Model Botani (Komoditas & Varietas)
    2. Model Geospasial (Lokasi & Firebase Trigger)
    3. Model Linguistik (Teks Natural Petani)
    """
    
    UNIT_CONVERSION = {
        "hektar": 1.0, "ha": 1.0,
        "bata": 0.0014,  # 1 bata = 14m2 = 0.0014 ha
        "tumbak": 0.0014,
        "ru": 0.0014,
        "bau": 0.7,      # 1 bau = ~0.7 ha
        "meter": 0.0001, "m2": 0.0001
    }

    def normalize_land_area(self, raw_value: str) -> float:
        """Mengonversi satuan lokal ke Satuan Internasional (Hektar)."""
        # Ekstrak angka dan satuan menggunakan regex
        match = re.search(r'(\d+(?:\.\d+)?)\s*([a-zA-Z2]+)', raw_value.lower())
        if not match: return 0.0
        
        val, unit = float(match.group(1)), match.group(2)
        multiplier = self.UNIT_CONVERSION.get(unit, 1.0)
        return round(val * multiplier, 4)

    def integrate(self, text: str, model_results: Dict[str, Any]) -> Dict[str, Any]:
        """Menggabungkan semua data menjadi objek utuh FAO-56."""
        
        # Ambil Luas Lahan dari Model Linguistik dan Normalisasi
        raw_area = model_results.get("raw_luas", "0 ha")
        normalized_area = self.normalize_land_area(raw_area)
        
        # Bangun Response Terintegrasi
        final_payload = {
            "fao56_status": "READY",
            "metadata": {
                "source_text": text,
                "confidence": model_results.get("confidence", 0.0)
            },
            "agronomy": {
                "crop": model_results.get("komoditas"),
                "variety": model_results.get("varietas"),
                "area_ha": normalized_area, # Satuan Internasional
            },
            "geospatial": {
                "location": model_results.get("lokasi"),
                "firebase_ref": model_results.get("lokasi_ref"), # Sinyal untuk Cuaca API
            }
        }
        return final_payload
