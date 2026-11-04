import os
import urllib.request
import zipfile
import io
import json
import csv
from datetime import datetime, timezone

REFERENCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app", "data", "reference"))
os.makedirs(REFERENCE_DIR, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': '*/*'
}

def fetch_amfi():
    print("--- Fetching AMFI NAVAll.txt ---")
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = resp.read()
    dest = os.path.join(REFERENCE_DIR, "amfi_navall.txt")
    with open(dest, "wb") as f:
        f.write(data)
    lines = data.decode("utf-8", errors="ignore").splitlines()
    schemes = [l for l in lines if ";" in l and not l.startswith("Scheme Code")]
    print(f"AMFI saved to {dest}: {len(data):,} bytes, {len(schemes):,} scheme records.")

def fetch_bse():
    print("--- Fetching BSE SCRIP.zip ---")
    url = "https://www.bseindia.com/downloads/Help/file/SCRIP.zip"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as resp:
        zip_bytes = resp.read()
    dest_zip = os.path.join(REFERENCE_DIR, "bse_scrip.zip")
    with open(dest_zip, "wb") as f:
        f.write(zip_bytes)
    print(f"BSE SCRIP.zip saved: {len(zip_bytes):,} bytes.")
    
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    print("Files in BSE zip:", zf.namelist())

def fetch_nse():
    print("--- Fetching NSE EQUITY_L.csv ---")
    url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
    dest = os.path.join(REFERENCE_DIR, "nse_equities.csv")
    with open(dest, "wb") as f:
        f.write(data)
    print(f"NSE equities saved: {len(data):,} bytes.")

def fetch_nse_etfs():
    print("--- Fetching NSE ETFs ---")
    url = "https://www.nseindia.com/api/etf"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
    dest = os.path.join(REFERENCE_DIR, "nse_etfs.json")
    with open(dest, "wb") as f:
        f.write(data)
    parsed = json.loads(data.decode("utf-8"))
    print(f"NSE ETFs saved: {len(data):,} bytes, {len(parsed.get('data', []))} ETFs.")

if __name__ == "__main__":
    fetch_amfi()
    fetch_bse()
    fetch_nse()
    fetch_nse_etfs()
    print("All authoritative snapshots updated successfully!")
