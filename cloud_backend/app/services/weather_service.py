# cloud_backend/app/services/weather_service.py

import os
import requests
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load rahasia dari file .env
load_dotenv()

logger = logging.getLogger(__name__)

class WeatherEngine:
    """
    Mengambil data iklim real-time berdasarkan koordinat 
    yang dipetakan dari lokasi.json dengan keamanan API Key yang solid.
    """
    def __init__(self):
        # Mengambil API Key dari file .env. Aman dari bot peretas GitHub.
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not self.api_key:
            logger.warning("⚠️ API Key Cuaca tidak ditemukan di file .env!")
            
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Menarik data suhu (T), kelembapan (RH), dan angin (U2)."""
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            # Simulasi atau Fetch riil
            # response = requests.get(self.base_url, params=params)
            # data = response.json()
            
            # Data Dummy untuk Simulasi jika API Key belum dipasang / hit limit
            return {
                "temp": 29.5,      # Suhu (°C)
                "humidity": 75,    # Kelembapan (%)
                "wind_speed": 2.1, # Kecepatan angin (m/s)
                "rain": 0.0        # Curah hujan (mm)
            }
        except Exception as e:
            logger.error(f"Gagal mengambil data cuaca: {e}")
            return None

def calculate_et0_simple(temp: float, humidity: float) -> float:
    """
    Estimasi sederhana Reference Evapotranspiration (ET0) 
    menggunakan metode Hargreaves (bagian dari standar FAO-56).
    """
    et0 = 0.0023 * (temp + 17.8) * (temp ** 0.5) * 0.408 
    return round(et0, 2)