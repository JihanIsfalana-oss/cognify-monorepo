from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum

# ==========================================
# 1. ENUMS (Restriksi Nilai Standar)
# ==========================================
class PestType(str, Enum):
    WBC = "Wereng Batang Coklat"
    PENGGEREK_BATANG = "Penggerek Batang"
    BLAST = "Penyakit Blast"
    AMAN = "Tidak Ada Hama"

class CropType(str, Enum):
    PADI = "Padi"
    CABE = "Cabai"
    BAWANG = "Bawang Merah"

class DeviceStatus(str, Enum):
    ACTIVE = "Active"
    POWER_SAVING = "Sleep"
    ERROR = "Sensor Error"

# ==========================================
# 2. EDGE TELEMETRY SCHEMAS (Dari LattePanda ke Cloud)
# ==========================================
class BioPhysicalData(BaseModel):
    soil_moisture: float = Field(..., ge=0.0, le=100.0, description="Persentase kelembapan tanah (Kapasitif)")
    ph_level: float = Field(..., ge=0.0, le=14.0, description="Kadar pH tanah dari elektroda gelas")
    temperature_c: float = Field(..., ge=-10.0, le=60.0, description="Suhu atmosferik dari DHT22")
    humidity_rel: float = Field(..., ge=0.0, le=100.0, description="Kelembapan atmosferik dari DHT22")

class AIInferenceData(BaseModel):
    pest_detected: PestType = Field(default=PestType.AMAN, description="Hasil deteksi OpenVINO INT8")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Tingkat keyakinan model (0.0 - 1.0)")
    latency_ms: int = Field(..., description="Waktu eksekusi inferensi lokal di LattePanda (ms)")

class TelemetryPayload(BaseModel):
    device_id: str = Field(..., min_length=5, description="ID unik unit Master (LattePanda)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Waktu data dikirim (UTC)")
    status: DeviceStatus = Field(default=DeviceStatus.ACTIVE)
    battery_level: float = Field(..., ge=0.0, le=100.0, description="Kapasitas baterai 18650 (%)")
    bio_physical: BioPhysicalData
    ai_inference: Optional[AIInferenceData] = None # Opsional jika Node sedang tidak melakukan periodic inference

    @field_validator('timestamp', mode='before')
    def parse_timestamp(cls, value):
        # Memastikan format timestamp dari ESP32 konsisten
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

# ==========================================
# 3. NLP & AGRONOMIC SCHEMAS (Cloud ke Frontend)
# ==========================================
class NLPRequest(BaseModel):
    raw_text: str = Field(..., min_length=3, max_length=500, description="Input bahasa natural dari petani")

class NLPExtractionResult(BaseModel):
    komoditas: CropType
    luas_lahan_ha: float = Field(..., gt=0.0, description="Luas lahan dalam Hektar")
    lokasi: str = Field(..., description="Desa/Kecamatan hasil ekstraksi (e.g., Kandanghaur)")
    confidence: float = Field(..., ge=0.0, le=1.0)

# ==========================================
# 4. DECISION SUPPORT SCHEMAS (FAO-56 & DBSCAN)
# ==========================================
class IrrigationRecommendation(BaseModel):
    v_std: float = Field(..., description="Volume air standar FAO-56 harian (Liter/Ha)")
    v_deficit: float = Field(default=0.0, description="Kompensasi defisit dari jadwal sebelumnya")
    v_next: float = Field(..., description="Total volume rekomendasi (V_std + V_deficit)")
    action_required: bool = Field(default=True)

class RadarCluster(BaseModel):
    cluster_id: int
    pest_type: PestType
    center_latitude: float = Field(..., ge=-90.0, le=90.0)
    center_longitude: float = Field(..., ge=-180.0, le=180.0)
    radius_km: float = Field(..., description="Radius penyebaran klaster dari DBSCAN")
    affected_nodes: int = Field(..., description="Jumlah perangkat Edge dalam klaster")
    risk_level: str = Field(..., pattern="^(Rendah|Waspada|Bahaya)$")

# ==========================================
# 5. GLOBAL RESPONSE WRAPPER
# ==========================================
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None