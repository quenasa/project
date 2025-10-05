"""
Socioeconomic data API routes
"""
from flask import Blueprint, jsonify, request
from services.socioeconomic_service import SocioeconomicService

socioeconomic_bp = Blueprint('socioeconomic', __name__)
soc_service = SocioeconomicService()


@socioeconomic_bp.route('/api/socioeconomic')
def get_socioeconomic_data():
    """
    Get socioeconomic data from WorldPop API
    
    Query params (REQUIRED):
        - lat (float): Latitude (required for Africa focus)
        - lon (float): Longitude (required for Africa focus)
        - location (optional): Location name
        - country (optional): Country name
    
    Returns socioeconomic indicators:
    - Population density and demographics
    - Poverty index
    - Access to basic services (water, health, education)
    - Income level estimates
    - Human Development Index (local)
    
    Data source: WorldPop Spatial Data Infrastructure (SDI) API
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
            "example": "/api/socioeconomic?lat=6.5244&lon=3.3792&country=Nigeria",
            "focus": "Africa region"
        }), 400
    
    # Validate Africa region
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
        # Fetch socioeconomic data from WorldPop
        data = soc_service.get_socioeconomic_data(lat, lon, location, country)
        
        return jsonify({
            "success": True,
            "data": data,
            "source": "WorldPop SDI API",
            "focus_region": "Africa",
            "cached": True,
            "cache_duration": "1 hour"
        })
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch socioeconomic data",
            "message": str(e),
            "coordinates": {"lat": lat, "lon": lon}
        }), 500
