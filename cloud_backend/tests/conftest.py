# cloud_backend/conftest.py

import json
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# ── 1. PYTHONPATH ─────────────────────────────────────────────────────────────
# Agar import "from app.xxx import yyy" bekerja dari root cloud_backend/
sys.path.insert(0, str(Path(__file__).resolve().parent))


# ── 2. MOCK FIREBASE SEBELUM MODUL APAPUN DIIMPORT ───────────────────────────

mock_firestore_client = MagicMock()
mock_collection        = MagicMock()
mock_document          = MagicMock()
mock_batch             = MagicMock()

# Rantai method Firestore yang dipakai di main.py dan services
mock_firestore_client.collection.return_value  = mock_collection
mock_collection.document.return_value          = mock_document
mock_collection.add.return_value               = (MagicMock(), MagicMock())
mock_document.set.return_value                 = None
mock_batch.set.return_value                    = None
mock_batch.commit.return_value                 = None
mock_firestore_client.batch.return_value       = mock_batch

# Patch firebase_admin di level sys.modules agar semua import terpengaruh
sys.modules["firebase_admin"]                        = MagicMock()
sys.modules["firebase_admin.credentials"]            = MagicMock()
sys.modules["firebase_admin.firestore"]              = MagicMock(
    client=MagicMock(return_value=mock_firestore_client),
    SERVER_TIMESTAMP="__server_timestamp__"
)
sys.modules["google.cloud"]                          = MagicMock()
sys.modules["google.cloud.firestore"]                = MagicMock(
    SERVER_TIMESTAMP="__server_timestamp__"
)


# ── 3. FAKE serviceAccountKey.json ───────────────────────────────────────────
# Dibuat sementara di memory agar path di config.py tidak raise FileNotFoundError

@pytest.fixture(scope="session", autouse=True)
def fake_service_account_key(tmp_path_factory):
    """Buat file kredensial Firebase palsu untuk session testing."""
    tmp = tmp_path_factory.mktemp("creds")
    fake_key = {
        "type": "service_account",
        "project_id": "cognify-test",
        "private_key_id": "fake-key-id",
        "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0Z3VS5JJcds3xHn/ygWep4PAtEsHABAbVH4DvR0mHgjHFpkr\n-----END RSA PRIVATE KEY-----\n",
        "client_email": "test@cognify-test.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    key_path = tmp / "serviceAccountKey.json"
    key_path.write_text(json.dumps(fake_key))

    # Override path di settings 
    with patch("app.core.config.Settings.FIREBASE_CREDS_PATH", new=key_path):
        yield key_path


# ── 4. MOCK WEATHER ENGINE (mencegah hit API eksternal) ──────────────────────

@pytest.fixture(autouse=True)
def mock_weather_engine(mocker):
    """Semua test tidak akan pernah hit OpenWeatherMap API."""
    mocker.patch(
        "app.services.weather_service.WeatherEngine.get_weather_data",
        return_value={
            "temp": 29.5,
            "temp_max": 33.0,
            "temp_min": 24.0,
            "humidity": 75,
            "wind_speed": 2.1,
            "rain": 0.0,
        }
    )
    
@pytest.fixture(autouse=True)
def mock_geo_radar(mocker):
    """
    Mock scan_nearby_threats agar tidak hit Firestore.
    Return list kosong = kondisi normal tanpa wabah terdeteksi.
    """
    mocker.patch(
        "app.main.scan_nearby_threats",
        return_value=[]
    )


# ── 5. FASTAPI TEST CLIENT ────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    """
    Buat TestClient setelah semua mock aktif.
    Scope module agar tidak re-create client setiap test.
    """
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        yield c


# ── 6. SAMPLE DATA FIXTURES ──────────────────────────────────────────────────

@pytest.fixture
def sample_nlp_payload():
    return {"raw_text": "Saya mau tanam Padi Inpari 32 di lahan 2 hektar di Indramayu"}

@pytest.fixture
def sample_telemetry_payload():
    return {
        "device_id": "CGNFY-EDGE-001",
        "kelembapan_tanah": 35.5,
        "suhu_lingkungan": 29.0,
        "ph_tanah": 6.8,
        "lat": -6.3264,
        "lon": 108.3182,
    }