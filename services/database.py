import sqlite3
from flask import current_app
from config import Config

def get_db_path():
    """Database path safely fetch karne ke liye (context ho ya na ho)"""
    try:
        return current_app.config["DATABASE_PATH"]
    except RuntimeError:
        return Config.DATABASE_PATH

def get_connection():
    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            place_id TEXT PRIMARY KEY, 
            name TEXT NOT NULL, 
            category TEXT,
            address TEXT, 
            phone TEXT, 
            website TEXT, 
            lat REAL, 
            lon REAL,
            opening_hours TEXT, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    connection.close()

def save_leads(leads):
    connection = get_connection()
    for lead in leads:
        if not lead.get("place_id"):
            continue
        connection.execute("""
            INSERT INTO leads (place_id, name, category, address, phone, website, lat, lon, opening_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(place_id) DO UPDATE SET
            name=excluded.name, category=excluded.category, address=excluded.address,
            phone=excluded.phone, website=excluded.website, lat=excluded.lat,
            lon=excluded.lon, opening_hours=excluded.opening_hours
        """, (
            lead.get("place_id"),
            lead.get("name"),
            lead.get("category"),
            lead.get("address"),
            lead.get("phone"),
            lead.get("website"),
            lead.get("lat"),
            lead.get("lon"),
            lead.get("opening_hours")
        ))
    connection.commit()
    connection.close()

def get_leads():
    connection = get_connection()
    rows = connection.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    connection.close()
    return [dict(row) for row in rows]

def delete_leads(place_ids):
    connection = get_connection()
    if place_ids:
        connection.executemany("DELETE FROM leads WHERE place_id=?", [(x,) for x in place_ids])
        connection.commit()
    connection.close()