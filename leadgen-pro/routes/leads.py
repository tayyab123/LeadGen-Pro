from flask import Blueprint, request, jsonify
from services.database import get_leads, delete_leads

leads_bp = Blueprint("leads", __name__)

@leads_bp.get("/api/leads")
def all_leads():
    leads = get_leads()
    return jsonify({"leads": leads, "count": len(leads)})

@leads_bp.delete("/api/leads")
def remove_leads():
    data = request.get_json(silent=True) or {}
    ids = data.get("place_ids", [])
    if not isinstance(ids, list):
        return jsonify({"error": "place_ids must be a list."}), 400
    delete_leads([str(x) for x in ids])
    return jsonify({"success": True})
