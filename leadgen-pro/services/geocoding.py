import requests
from flask import current_app

BASE_URL = "https://api.geoapify.com/v1/geocode/search"

def geocode_location(location):
    api_key = current_app.config.get("GEOAPIFY_API_KEY")
    if not api_key:
        raise RuntimeError("Geoapify API key is not configured. Add it to your .env file.")
    try:
        response = requests.get(
            BASE_URL,
            params={"text": location, "format": "json", "limit": 1, "apiKey": api_key},
            timeout=20,
        )
        if response.status_code == 401:
            raise RuntimeError("Geoapify rejected the API key. Check your .env configuration.")
        if response.status_code == 429:
            raise RuntimeError("Geoapify request limit reached. Please try again later.")
        response.raise_for_status()
        data = response.json()
    except requests.Timeout as exc:
        raise RuntimeError("Location lookup timed out. Please try again.") from exc
    except requests.RequestException as exc:
        raise RuntimeError("Could not connect to Geoapify. Check your internet connection.") from exc

    results = data.get("results") or []
    if not results:
        raise ValueError("We couldn't find that location. Try a city name with its country.")
    first = results[0]
    return {"lat": first["lat"], "lon": first["lon"], "formatted": first.get("formatted", location)}
