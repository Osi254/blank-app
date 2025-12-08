# utils_locations.py
import os
import math
import pandas as pd
import pgeocode  # pip install pgeocode

DATA_DIR = "data"
JOB_SITES_FILE = os.path.join(DATA_DIR, "job_sites.csv")

os.makedirs(DATA_DIR, exist_ok=True)

def load_job_sites():
    if os.path.exists(JOB_SITES_FILE):
        return pd.read_csv(JOB_SITES_FILE)
    else:
        cols = [
            "site_name", "address", "city", "state", "zip_code",
            "trade", "needed_workers", "latitude", "longitude"
        ]
        return pd.DataFrame(columns=cols)

def save_job_sites(df):
    df.to_csv(JOB_SITES_FILE, index=False)

_nom = pgeocode.Nominatim("us")

def geocode_zip(zip_code: str):
    rec = _nom.query_postal_code(str(zip_code))
    if rec is None or pd.isna(rec.latitude) or pd.isna(rec.longitude):
        return None, None
    return float(rec.latitude), float(rec.longitude)

def haversine(lat1, lon1, lat2, lon2):
    # all args in decimal degrees
    R = 6371.0  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # distance in km
