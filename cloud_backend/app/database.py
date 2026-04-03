# cloud_backend/app/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# 1. Tentukan lokasi file database lokal (akan otomatis terbuat bernama cognify_local.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./cognify_local.db"

# 2. Buat "Mesin" penghubung
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Buat pabrik Sesi (Session) untuk transaksi data
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Kelas dasar untuk membuat tabel
Base = declarative_base()

# --- MODEL TABEL DATABASE ---
class TelemetryRecord(Base):
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    kelembapan_tanah = Column(Float)
    suhu_lingkungan = Column(Float)
    ph_tanah = Column(Float)
    status_pompa = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)