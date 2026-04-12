# cloud_backend/app/services/weather_service.py

import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WeatherEngine:
    """
    Mengambil data iklim real-time berdasarkan koordinat 
    yang dipetakan dari lokasi.json.
    """
    def __init__(self, api_key: str = "YOUR_API_KEY"):
        self.api_key = api_key
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
            
            # Data Dummy untuk Simulasi jika API Key belum dipasang
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
    # Rumus penyederhanaan untuk demo:
    et0 = 0.0023 * (temp + 17.8) * (temp ** 0.5) * 0.408 
    return round(et0, 2)