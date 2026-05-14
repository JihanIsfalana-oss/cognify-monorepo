# cloud_backend/tests/test_nlp_engine.py

import pytest
from app.services.nlp_engine import FAO56HybridEngine, process_farmer_input


@pytest.fixture(scope="module")
def engine():
    """Singleton engine — dibuat sekali per module."""
    return FAO56HybridEngine()


class TestEntityExtraction:
    def test_engine_initializes(self, engine):
        assert engine is not None

    def test_padi_inpari_32_extracted(self, engine):
        result = engine.extract_entities("Saya tanam Padi Inpari 32 di Indramayu")
        assert result["komoditas"] != "Tidak Diketahui"

    def test_lokasi_indramayu_extracted(self, engine):
        result = engine.extract_entities("Lahan padi 2 hektar di Indramayu")
        assert result["lokasi"].lower() == "indramayu"

    def test_lokasi_karawang_extracted(self, engine):
        result = engine.extract_entities("Jagung Bisi 18 di Karawang 3 ha")
        assert result["lokasi"].lower() == "karawang"

    def test_firebase_signal_assigned_for_valid_lokasi(self, engine):
        result = engine.extract_entities("Padi Ciherang Indramayu 1 hektar")
        if result["lokasi"].lower() == "indramayu":
            assert result["firebase_signal"] == "ID-JB-IM"

    def test_unknown_entity_returns_default(self, engine):
        result = engine.extract_entities("Hari ini sangat cerah sekali di luar rumah")
        assert result["komoditas"] == "Tidak Diketahui"
        assert result["lokasi"] == "Tidak Diketahui"

    def test_confidence_range_valid(self, engine):
        result = engine.extract_entities("Padi Inpari 32 di Indramayu 2 hektar")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_process_farmer_input_wrapper(self):
        result = process_farmer_input("Tanam jagung 1 hektar di Sragen")
        assert isinstance(result, dict)
        assert "komoditas" in result
        assert "lokasi" in result
        assert "confidence" in result


class TestUnitConversion:
    def test_hektar_unit(self, engine):
        assert engine.convert_to_hectares("2 hektar") == pytest.approx(2.0)

    def test_ha_abbreviation(self, engine):
        assert engine.convert_to_hectares("1.5 ha") == pytest.approx(1.5)

    def test_bata_to_hektar(self, engine):
        # 100 bata × 0.0014 = 0.14 ha
        assert engine.convert_to_hectares("100 bata") == pytest.approx(0.14, abs=0.001)

    def test_tumbak_to_hektar(self, engine):
        assert engine.convert_to_hectares("50 tumbak") == pytest.approx(0.07, abs=0.001)

    def test_bau_to_hektar(self, engine):
        # 1 bau × 0.7096 = 0.7096 ha
        assert engine.convert_to_hectares("1 bau") == pytest.approx(0.7096, abs=0.001)

    def test_meter_to_hektar(self, engine):
        # 5000 m2 × 0.0001 = 0.5 ha
        assert engine.convert_to_hectares("5000 meter") == pytest.approx(0.5, abs=0.001)

    def test_no_unit_returns_zero(self, engine):
        assert engine.convert_to_hectares("Tidak ada angka di sini") == 0.0

    def test_comma_decimal_separator(self, engine):
        # Format angka Indonesia: 1,5 hektar
        assert engine.convert_to_hectares("1,5 ha") == pytest.approx(1.5, abs=0.001)