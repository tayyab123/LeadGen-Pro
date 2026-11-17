from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
import pandas as pd
from utils.export_utils import normalize_export_rows

export_bp = Blueprint("export", __name__)

@export_bp.post("/api/export/csv")
def export_csv():
    rows = normalize_export_rows(request.get_json(silent=True) or {})
    if not rows:
        return jsonify({"error": "There are no leads to export."}), 400
    buffer = BytesIO()
    pd.DataFrame(rows).to_csv(buffer, index=False, encoding="utf-8-sig")
    buffer.seek(0)
    return send_file(buffer, mimetype="text/csv", as_attachment=True, download_name="leadgen-pro-leads.csv")

@export_bp.post("/api/export/excel")
def export_excel():
    rows = normalize_export_rows(request.get_json(silent=True) or {})
    if not rows:
        return jsonify({"error": "There are no leads to export."}), 400
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        frame = pd.DataFrame(rows)
        frame.to_excel(writer, index=False, sheet_name="Business Leads")
        sheet = writer.sheets["Business Leads"]
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        from openpyxl.styles import Font, PatternFill, Alignment
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="4338CA")
            cell.alignment = Alignment(vertical="center")
        for column_cells in sheet.columns:
            width = min(max(max(len(str(c.value or "")) for c in column_cells) + 2, 14), 48)
            sheet.column_dimensions[column_cells[0].column_letter].width = width
    buffer.seek(0)
    return send_file(buffer, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True, download_name="leadgen-pro-leads.xlsx")
