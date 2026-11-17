import requests
from flask import current_app

PLACES_URL = "https://api.geoapify.com/v2/places"

CATEGORY_MAP = {
    "restaurant": "catering.restaurant", "restaurants": "catering.restaurant",
    "cafe": "catering.cafe", "coffee": "catering.cafe",
    "hotel": "accommodation.hotel", "hotels": "accommodation.hotel",
    "school": "education.school", "university": "education.university",
    "hospital": "healthcare.hospital", "clinic": "healthcare.clinic",
    "pharmacy": "healthcare.pharmacy", "software": "office.company",
    "software house": "office.company", "real estate": "commercial",
    "shop": "commercial", "store": "commercial", "office": "office",
    "gym": "leisure.sport", "bank": "service.financial",
    "college":  "education.college", "university": "education.university",
    
}

def resolve_categories(keyword):
    key = keyword.strip().lower()
    return CATEGORY_MAP.get(key, "commercial,catering,accommodation,education,healthcare,office,retail,service")

def search_places(lat, lon, radius, limit, keyword):
    api_key = current_app.config.get("GEOAPIFY_API_KEY")
    categories = resolve_categories(keyword)
    params = {
        "categories": categories,
        "filter": f"circle:{lon},{lat},{radius}",
        "bias": f"proximity:{lon},{lat}",
        "limit": limit,
        "apiKey": api_key,
    }
    try:
        response = requests.get(PLACES_URL, params=params, timeout=30)
        if response.status_code == 401:
            raise RuntimeError("Geoapify rejected the API key. Please check your key.")
        if response.status_code == 429:
            raise RuntimeError("Geoapify request limit reached. Please wait and try again.")
        response.raise_for_status()
        payload = response.json()
    except requests.Timeout as exc:
        raise RuntimeError("Business search timed out. Please try again.") from exc
    except requests.RequestException as exc:
        raise RuntimeError("Unable to reach Geoapify Places API. Check your connection.") from exc

    leads = []
    for feature in payload.get("features", []):
        props = feature.get("properties") or {}
        raw = ((props.get("datasource") or {}).get("raw") or {})
        coords = (feature.get("geometry") or {}).get("coordinates") or [None, None]
        name = props.get("name") or raw.get("name")
        if not name:
            continue
        website = props.get("website") or raw.get("website") or raw.get("contact:website")
        phone = props.get("contact") or raw.get("phone") or raw.get("contact:phone")
        if isinstance(phone, dict):
            phone = phone.get("phone") or phone.get("mobile")
        if isinstance(website, list):
            website = website[0] if website else None
        place_id = props.get("place_id") or props.get("datasource", {}).get("raw", {}).get("id")
        leads.append({
            "place_id": str(place_id or ""),
            "name": name,
            "category": ", ".join(props.get("categories") or []) or keyword,
            "address": props.get("formatted") or props.get("address_line2") or "Not Available",
            "phone": phone or "Not Available",
            "website": website or "Not Available",
            "lat": coords[1], "lon": coords[0],
            "opening_hours": props.get("opening_hours") or "Not Available",
        })
    return leads
