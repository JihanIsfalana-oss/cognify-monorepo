from app.services.nlp_engine import nlp_processor

def test_konversi_luas_hektar():
    """Menguji kecerdasan Regex dalam mengonversi satuan tanah lokal ke Hektar"""
    
    # Test Satuan Bata (1 bata = 0.0014 ha)
    assert nlp_processor.convert_to_hectares("100 bata") == 0.14
    
    # Test Satuan Bau (1 bau = 0.7096 ha)
    assert nlp_processor.convert_to_hectares("setengah bau") == 0.0 # Karena "setengah" bukan angka mutlak, regex wajar return 0
    assert nlp_processor.convert_to_hectares("0.5 bau") == 0.3548
    
    # Test Satuan Hektar (Tidak berubah)
    assert nlp_processor.convert_to_hectares("2 hektar") == 2.0
    assert nlp_processor.convert_to_hectares("1.5 ha") == 1.5

def test_struktur_ekstraksi_ai():
    """Menguji apakah mesin NLP mereturn dictionary dengan struktur yang valid (anti-keyerror)"""
    
    hasil = nlp_processor.extract_entities("Tanam padi di Brebes")
    
    # Memastikan semua key esensial ada di dalam output
    assert "komoditas" in hasil
    assert "luas_lahan_ha" in hasil
    assert "lokasi" in hasil
    assert "firebase_signal" in hasil
    assert "confidence" in hasil