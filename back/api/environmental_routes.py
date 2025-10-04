"""
Environmental data API routes
"""
from flask import Blueprint, jsonify, request
from services.environmental_service import EnvironmentalService

environmental_bp = Blueprint('environmental', __name__)
env_service = EnvironmentalService()


@environmental_bp.route('/api/environmental')
def get_environmental_data():
    """
    Get environmental data from Copernicus CDS API
    
    Query params (REQUIRED):
        - lat (float): Latitude (required for Africa focus)
        - lon (float): Longitude (required for Africa focus)
        - location (optional): Location name
        - country (optional): Country name
    
    Returns comprehensive environmental data:
    - Air quality (PM2.5, NO2, O3, SO2, CO)
    - Temperature and heat wave risk
    - Vegetation coverage (NDVI)
    - Water quality
    - CO2 emissions
    - Climate risks (floods, droughts)
    
    Data source: Copernicus Climate Data Store (CDS)
    Geographic focus: Africa
    """
    # Get coordinates (required)
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    
    # Optional parameters
    location = request.args.get('location')
    country = request.args.get('country')
    
    # Validate coordinates
    if lat is None or lon is None:
        return jsonify({
            "error": "Missing required parameters",
            "message": "Both 'lat' and 'lon' coordinates are required",
            "example": "/api/environmental?lat=6.5244&lon=3.3792&country=Nigeria",
            "focus": "Africa region"
        }), 400
    
    # Validate Africa region (approximate bounds)
    if not (-35 <= lat <= 37 and -20 <= lon <= 55):
        return jsonify({
            "warning": "Coordinates outside Africa region",
            "message": "This API is optimized for African locations",
            "provided": {"lat": lat, "lon": lon},
            "africa_bounds": {
                "lat": "-35 to 37",
                "lon": "-20 to 55"
            }
        }), 400
    
    try:
        # Fetch environmental data from Copernicus
        data = env_service.get_environmental_data(lat, lon, location, country)
        
        return jsonify({
            "success": True,
            "data": data,
            "source": "Copernicus Climate Data Store (CDS)",
            "focus_region": "Africa",
            "cached": True,
            "cache_duration": "1 hour"
        })
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch environmental data",
            "message": str(e),
            "coordinates": {"lat": lat, "lon": lon}
        }), 500
