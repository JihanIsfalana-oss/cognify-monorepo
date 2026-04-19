# cloud_backend/app/services/geo_radar.py
import pygeohash as pgh
from app.core.firebase import db

def get_geohash_range(lat: float, lon: float, radius_km: float):
    lat_degree = radius_km / 111.32
    lon_degree = radius_km / (111.32 * abs(math.cos(math.radians(lat))))
    
    lower_lat, upper_lat = lat - lat_degree, lat + lat_degree
    lower_lon, upper_lon = lon - lon_degree, lon + lon_degree
    
    lower_hash = pgh.encode(lower_lat, lower_lon, precision=6)
    upper_hash = pgh.encode(upper_lat, upper_lon, precision=6)
    
    return lower_hash, upper_hash

def scan_nearby_threats(lat: float, lon: float, radius_km: float):
    lower_hash, upper_hash = get_geohash_range(lat, lon, radius_km)
    
    threats_ref = db.collection("radar_hama")
    query = threats_ref.where("geohash", ">=", lower_hash).where("geohash", "<=", upper_hash)
    
    results = []
    for doc in query.stream():
        data = doc.to_dict()
        distance = pgh.geohash_approximate_distance(
            pgh.encode(lat, lon), data['geohash']
        )
        if distance <= (radius_km * 1000):
            results.append({"id": doc.id, **data})
            
    return results