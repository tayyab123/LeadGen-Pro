# LeadGen Pro
**Discover Businesses. Generate Leads. Grow Faster.**

LeadGen Pro is a Flask business lead discovery dashboard powered by the Geoapify Geocoding and Places APIs. It searches real API data, deduplicates results, stores leads locally in SQLite, displays map markers, and exports CSV or Excel files.

## Requirements
- Python 3.11.9
- A Geoapify account and API key
- Internet connection

## Setup (Windows PowerShell)
```powershell
cd leadgen-pro
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and add your key:
```env
GEOAPIFY_API_KEY=your_real_key_here
FLASK_SECRET_KEY=use_a_long_random_secret
```

Get a key from https://myprojects.geoapify.com/ . Keep it private; the backend reads it from `.env` and does not send it to browser JavaScript.

## Run
```powershell
python app.py
```
Open http://127.0.0.1:5000

## Use
1. Enter a business category or keyword (for example `restaurant`, `hotel`, `pharmacy`, or `software house`).
2. Enter a city or location, including country where useful.
3. Choose radius and maximum results.
4. Press **Find businesses**.
5. Search within the results, filter by contact availability, select rows, or load saved leads.
6. Export the current result set (or selected rows) to CSV or Excel.

## API routes
- `GET /` — dashboard
- `POST /api/search` — geocode and search nearby places
- `GET /api/health` — service health
- `GET /api/config/status` — reports whether a key is configured (never returns the key)
- `GET /api/leads` — locally saved leads
- `DELETE /api/leads` — delete leads by `place_ids`
- `POST /api/export/csv` — CSV export
- `POST /api/export/excel` — formatted Excel export

## Notes and data use
Geoapify may not return a phone number, website, or opening hours for every place. Missing information is shown as **Not Available**. The app does not fabricate results or contact details. Search categories are mapped to Geoapify category identifiers where a known mapping is provided; a general set of place categories is used for other keywords, so refine your keyword and radius if the results are broad.

Review Geoapify's current terms, attribution, API limits, and data-use/licensing conditions before storing, exporting, or redistributing returned data. This local app stores leads in SQLite for convenience; retention and downstream use remain your responsibility and must comply with the applicable terms. The map uses OpenStreetMap tiles with attribution.

## Project structure
```text
leadgen-pro/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── routes/
│   ├── __init__.py
│   ├── search.py
│   ├── export.py
│   └── leads.py
├── services/
│   ├── __init__.py
│   ├── geocoding.py
│   ├── geoapify.py
│   └── database.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   ├── duplicate_remover.py
│   └── export_utils.py
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/app.js
└── database/
    └── leads.db (created automatically on first run)
```

## Troubleshooting
- **API key not configured:** copy `.env.example` to `.env` and add a valid key.
- **Invalid key / quota:** verify the key and project usage in Geoapify.
- **No results:** try a broader category, larger radius, or a more specific location.
- **No phone or website:** these fields are optional in the source data.
- **Map tiles unavailable:** check internet access; map tiles are served by OpenStreetMap.

The `.env` file is intentionally not included in the ZIP. Create it locally from `.env.example` so your private key is not accidentally shared.
