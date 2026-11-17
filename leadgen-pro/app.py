
import os
from flask import Flask, render_template, jsonify
from config import Config
from routes.search import search_bp
from routes.export import export_bp
from routes.leads import leads_bp
from services.database import init_db


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    # Initialize database
    init_db()

    # Register blueprints
    app.register_blueprint(search_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(leads_bp)

    @app.get("/")
    def dashboard():
        return render_template("index.html")

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "LeadGen Pro"
        })

    @app.get("/api/config/status")
    def config_status():
        return jsonify({
            "configured": bool(
                app.config.get("GEOAPIFY_API_KEY")
            )
        })

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
