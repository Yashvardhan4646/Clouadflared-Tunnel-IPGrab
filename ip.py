import os
import json
import requests

LOG_FILE = "visits.txt"

def fetch_ip_info(ip: str):
    """Fetch IP geolocation and ASN data from ipinfo.io."""
    url = f"https://ipinfo.io/{ip}/json"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
        print(f"Error: API returned status code {res.status_code} for IP {ip}")
    except requests.RequestException as e:
        print(f"Network error resolving IP {ip}: {e}")
    return None

def process_log():
    if not os.path.exists(LOG_FILE):
        print(f"Log file '{LOG_FILE}' not found. No visits to process.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "|" not in line:
                continue

            parts = line.split("|")
            if len(parts) < 2:
                continue

            # Extract IP field: expects "IP: <address>"
            ip_segment = parts[1].strip()
            if ":" not in ip_segment:
                continue

            ip = ip_segment.split(":", 1)[1].strip()
            if not ip or ip == "Unavailable":
                continue

            data = fetch_ip_info(ip)
            if data:
                print(json.dumps(data, indent=4))

if __name__ == "__main__":
    process_log()

