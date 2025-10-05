"""
Main API routes
"""
from flask import Blueprint, jsonify
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Root endpoint - API information"""
    return jsonify({
        "name": "Climate and Social Justice Map API",
        "version": "1.0.0",
        "description": "Backend API for integrating environmental, socioeconomic, and democratic data",
        "features": {
            "caching": "1 hour cache for API responses",
            "rate_limiting": "200 requests/day, 50 requests/hour",
            "openstreetmap_ready": True,
            "modular_architecture": True
        },
        "endpoints": {
            "/api/environmental": "Get environmental data (from external APIs)",
            "/api/socioeconomic": "Get socioeconomic data (from external APIs)",
            "/api/democratic": "Get democratic participation data (from external sources)",
            "/api/vulnerability": "Calculate vulnerability index (IVSA)",
            "/api/reports": "Citizen environmental reports",
            "/api/health": "API health check"
        },
        "note": "Data is fetched dynamically from external APIs. See API_INTEGRATION_GUIDE.md"
    })


@main_bp.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "cache_enabled": True,
        "rate_limiting_enabled": True,
        "data_source": "external_apis",
        "timestamp": datetime.now().isoformat()
    })
