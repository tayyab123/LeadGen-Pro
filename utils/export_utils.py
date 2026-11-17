ALLOWED_FIELDS = ["name", "category", "address", "phone", "website", "place_id", "lat", "lon", "opening_hours"]

def normalize_export_rows(data):
    rows = data.get("leads", []) if isinstance(data, dict) else []
    if not isinstance(rows, list):
        return []
    normalized = []
    for row in rows:
        if isinstance(row, dict):
            normalized.append({field: row.get(field, "Not Available") for field in ALLOWED_FIELDS})
    return normalized
