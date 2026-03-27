# modules/location.py - Real-time Location Store for Jarvis
import json
import os
import requests
from config import YOUR_CITY

LOCATION_FILE = "data/location.json"
if not os.path.exists("data"):
    os.makedirs("data")

def get_current_location():
    """Retrieve the last stored location or fallback to IP-based location."""
    if os.path.exists(LOCATION_FILE):
        try:
            with open(LOCATION_FILE, "r") as f:
                return json.load(f)
        except:
            pass
            
    # Fallback: IP-based location
    try:
        res = requests.get("http://ip-api.com/json", timeout=5)
        data = res.json()
        if data["status"] == "success":
            loc_data = {
                "lat": data["lat"],
                "lon": data["lon"],
                "city": data["city"],
                "country": data["country"],
                "source": "ip"
            }
            save_location(loc_data)
            return loc_data
    except:
        pass
        
    return {"city": YOUR_CITY, "lat": None, "lon": None, "source": "config"}

def save_location(data):
    """Store location data persistently."""
    with open(LOCATION_FILE, "w") as f:
        json.dump(data, f, indent=4)

def update_from_telegram(lat, lon, city=None):
    """Update location from Telegram's live or static location sharing."""
    loc_data = {
        "lat": lat,
        "lon": lon,
        "city": city or "Unknown (from Telegram)",
        "source": "telegram"
    }
    save_location(loc_data)
    print(f"📍 Location updated: {lat}, {lon}")
    return loc_data
