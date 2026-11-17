from flask import Blueprint, request, jsonify, current_app
from services.geocoding import geocode_location
from services.geoapify import search_places
from services.database import save_leads

search_bp = Blueprint("search", __name__)

@search_bp.post("/api/search")
def search():
    data = request.get_json(silent=True) or {}
    keyword = str(data.get("keyword", "")).strip()
    location = str(data.get("location", "")).strip()
    if not keyword:
        return jsonify({"error": "Enter a business category or keyword."}), 400
    if not location:
        return jsonify({"error": "Enter a city or location."}), 400
    try:
        radius = max(500, min(int(data.get("radius", 5000)), 50000))
        limit = max(1, min(int(data.get("limit", 50)), 500))
        coordinates = geocode_location(location)
        leads = search_places(coordinates["lat"], coordinates["lon"], radius, limit, keyword)
        seen, unique = set(), []
        for lead in leads:
            key = lead["place_id"] or f'{lead["name"].lower()}|{lead["address"].lower()}'
            if key not in seen:
                seen.add(key)
                unique.append(lead)
        save_leads(unique)
        return jsonify({"leads": unique, "count": len(unique), "location": coordinates["formatted"]})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502
    except (TypeError, ValueError):
        return jsonify({"error": "Radius and result limit must be valid numbers."}), 400
    except Exception:
        current_app.logger.exception("Unexpected business search error")
        return jsonify({"error": "Something went wrong while searching. Please try again."}), 500
