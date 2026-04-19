def test_health_check(client):
    """Memastikan server FastAPI bisa menyala dan merespon"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_iot_telemetry_pompa_on(client):
    """
    Simulasi ESP32 mengirim data tanah kering.
    Sistem harus merespon dengan perintah POMPA ON.
    """
    payload = {
        "device_id": "ESP32-COGNIFY-01",
        "kelembapan_tanah": 25.5, # Kering (di bawah 40)
        "suhu_lingkungan": 32.0,
        "ph_tanah": 6.5
    }
    
    response = client.post("/api/iot/telemetry", json=payload)
    data = response.json()
    
    assert response.status_code == 200
    assert data["success"] is True
    assert data["instruksi_pompa"] == "ON"

def test_iot_telemetry_pompa_off(client):
    """
    Simulasi ESP32 mengirim data tanah basah.
    Sistem harus merespon dengan perintah POMPA OFF.
    """
    payload = {
        "device_id": "ESP32-COGNIFY-01",
        "kelembapan_tanah": 85.0, # Basah (di atas 40)
        "suhu_lingkungan": 28.0,
        "ph_tanah": 6.5
    }
    
    response = client.post("/api/iot/telemetry", json=payload)
    data = response.json()
    
    assert response.status_code == 200
    assert data["instruksi_pompa"] == "OFF"

def test_nlp_extract_valid(client):
    """Simulasi Frontend mengirim input lahan petani"""
    payload = {
        "raw_text": "Saya mau tanam bawang merah bima brebes 1.5 hektar di daerah Brebes"
    }
    
    response = client.post("/api/nlp/extract", json=payload)
    data = response.json()
    
    assert response.status_code == 200
    # Meskipun gagal narik API cuaca, sistem harus tetap success karena AI berhasil ekstraksi
    assert data["success"] is True 
    assert data["luas_lahan_ha"] == 1.5
    assert "kebutuhan_air_liter" in data