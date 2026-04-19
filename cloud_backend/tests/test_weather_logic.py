from app.services.weather_service import calculate_et0_simple
from app.services.weather_bridge import sync_weather_by_ai_signal

def test_rumus_evapotranspirasi_et0():
    """Menguji kepastian rumus matematika irigasi (Hargreaves method)"""
    suhu = 30.0
    kelembapan = 70.0
    
    et0 = calculate_et0_simple(suhu, kelembapan)
    
    # ET0 harus berupa angka float dan lebih dari 0 di hari panas
    assert isinstance(et0, float)
    assert et0 > 0.0
    assert et0 < 10.0 # Mustahil penguapan lebih dari 10mm/hari di Indonesia

def test_bridge_lokasi_tidak_dikenal():
    """Menguji respon sistem jika AI mendeteksi lokasi yang tidak ada di database"""
    respon = sync_weather_by_ai_signal("Atlantis")
    
    assert respon["success"] is False
    assert "tidak terdaftar" in respon["message"].lower()