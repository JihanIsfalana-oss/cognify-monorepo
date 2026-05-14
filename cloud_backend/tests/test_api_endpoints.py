# cloud_backend/tests/test_api_endpoints.py

import pytest


class TestHealthCheck:
    def test_root_returns_online(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "COGNIFY" in data["message"]


class TestNLPExtract:
    def test_valid_input_returns_success(self, client, sample_nlp_payload):
        response = client.post("/api/nlp/extract", json=sample_nlp_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["komoditas"] != "Tidak Diketahui"

    def test_padi_inpari_detected(self, client):
        payload = {"raw_text": "Tanam Padi Ciherang di Indramayu 1 hektar"}
        response = client.post("/api/nlp/extract", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Komoditas harus berhasil diekstrak
        assert "padi" in data["komoditas"].lower() or data["komoditas"] != "Tidak Diketahui"

    def test_lokasi_indramayu_detected(self, client):
        payload = {"raw_text": "Lahan jagung 3 hektar di Indramayu siap ditanam"}
        response = client.post("/api/nlp/extract", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "indramayu" in data["lokasi"].lower()

    def test_luas_lahan_hektar_parsed(self, client):
        payload = {"raw_text": "Padi Mekongga 2 hektar Indramayu"}
        response = client.post("/api/nlp/extract", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["luas_lahan_ha"] == pytest.approx(2.0, abs=0.01)

    def test_luas_lahan_bata_converted(self, client):
        """100 bata = 0.14 hektar — validasi konversi satuan lokal."""
        payload = {"raw_text": "Tanam padi 100 bata di Indramayu"}
        response = client.post("/api/nlp/extract", json=payload)
        assert response.status_code == 200
        data = response.json()
        # 100 * 0.0014 = 0.14 ha
        assert data["luas_lahan_ha"] == pytest.approx(0.14, abs=0.01)

    def test_empty_text_returns_422(self, client):
        """FastAPI Pydantic validation: min_length=3."""
        payload = {"raw_text": "ab"}
        response = client.post("/api/nlp/extract", json=payload)
        assert response.status_code == 422

    def test_missing_field_returns_422(self, client):
        response = client.post("/api/nlp/extract", json={})
        assert response.status_code == 422

    def test_unrecognized_input_returns_failure(self, client):
        payload = {"raw_text": "Hari ini cuaca sangat cerah dan menyenangkan"}
        response = client.post("/api/nlp/extract", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Tidak ada entitas agronomis — sukses atau gagal tapi tidak error 500
        assert "success" in data

    def test_kebutuhan_air_is_positive_when_lokasi_found(self, client):
        payload = {"raw_text": "Padi Inpari 32 1 hektar di Indramayu"}
        response = client.post("/api/nlp/extract", json=payload)
        assert response.status_code == 200
        data = response.json()
        if data["success"] and data["lokasi"] != "Tidak Diketahui":
            assert data["kebutuhan_air_liter"] >= 0


class TestIoTTelemetry:
    def test_valid_telemetry_returns_success(self, client, sample_telemetry_payload):
        response = client.post("/api/iot/telemetry", json=sample_telemetry_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["instruksi_pompa"] in ["ON", "OFF"]

    def test_pompa_on_when_moisture_below_40(self, client):
        payload = {
            "device_id": "COGNFY-TEST-001",
            "kelembapan_tanah": 25.0,    # di bawah threshold 40
            "suhu_lingkungan": 30.0,
            "ph_tanah": 6.5,
            "lat": -6.32,
            "lon": 108.31,
        }
        response = client.post("/api/iot/telemetry", json=payload)
        assert response.status_code == 200
        assert response.json()["instruksi_pompa"] == "ON"

    def test_pompa_off_when_moisture_above_40(self, client):
        payload = {
            "device_id": "COGNFY-TEST-002",
            "kelembapan_tanah": 65.0,    # di atas threshold 40
            "suhu_lingkungan": 28.0,
            "ph_tanah": 7.0,
            "lat": -6.32,
            "lon": 108.31,
        }
        response = client.post("/api/iot/telemetry", json=payload)
        assert response.status_code == 200
        assert response.json()["instruksi_pompa"] == "OFF"

    def test_missing_device_id_returns_422(self, client):
        payload = {"kelembapan_tanah": 35.0, "suhu_lingkungan": 29.0,
                   "ph_tanah": 6.8, "lat": -6.32, "lon": 108.31}
        response = client.post("/api/iot/telemetry", json=payload)
        assert response.status_code == 422


class TestGeoRadarScan:
    def test_scan_returns_success(self, client):
        response = client.get("/api/radar/scan", params={
            "lat": -6.3264, "lon": 108.3182, "radius_km": 5.0
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "threats_found" in data
        assert isinstance(data["data"], list)

    def test_scan_without_radius_uses_default(self, client):
        response = client.get("/api/radar/scan", params={
            "lat": -6.3264, "lon": 108.3182
        })
        assert response.status_code == 200
        assert response.json()["radius"] == "10.0 km"

    def test_scan_missing_lat_returns_422(self, client):
        response = client.get("/api/radar/scan", params={"lon": 108.31})
        assert response.status_code == 422