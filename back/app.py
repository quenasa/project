"""
Climate and Social Justice Map - Backend API
Flask application that provides RESTful endpoints for environmental,
socioeconomic, and democratic data integration.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
app.config['JSON_SORT_KEYS'] = False

# Mock data for demonstration - In production, these would call external APIs
MOCK_ENVIRONMENTAL_DATA = [
    {
        "id": 1,
        "location": {"lat": 40.4168, "lon": -3.7038, "name": "Madrid Sur"},
        "air_quality": {"pm25": 45.2, "no2": 38.5, "ozone": 62.1},
        "temperature": 28.5,
        "vegetation_coverage": 15.3,
        "flood_risk": "medium",
        "co2_emissions": 8.2,
        "timestamp": datetime.now().isoformat()
    },
    {
        "id": 2,
        "location": {"lat": 41.3851, "lon": 2.1734, "name": "Barcelona Norte"},
        "air_quality": {"pm25": 32.1, "no2": 28.3, "ozone": 55.4},
        "temperature": 26.2,
        "vegetation_coverage": 28.7,
        "flood_risk": "low",
        "co2_emissions": 5.8,
        "timestamp": datetime.now().isoformat()
    }
]

MOCK_SOCIOECONOMIC_DATA = [
    {
        "id": 1,
        "location": {"lat": 40.4168, "lon": -3.7038, "name": "Madrid Sur"},
        "average_income": 18500,
        "poverty_index": 28.5,
        "basic_services_access": {"water": 95, "health": 82, "education": 88},
        "human_development_index": 0.72,
        "timestamp": datetime.now().isoformat()
    },
    {
        "id": 2,
        "location": {"lat": 41.3851, "lon": 2.1734, "name": "Barcelona Norte"},
        "average_income": 32000,
        "poverty_index": 12.3,
        "basic_services_access": {"water": 98, "health": 95, "education": 96},
        "human_development_index": 0.88,
        "timestamp": datetime.now().isoformat()
    }
]

MOCK_DEMOCRATIC_DATA = [
    {
        "id": 1,
        "location": {"lat": 40.4168, "lon": -3.7038, "name": "Madrid Sur"},
        "electoral_participation": 58.2,
        "citizen_participation_spaces": 3,
        "transparency_index": 65,
        "active_organizations": 12,
        "timestamp": datetime.now().isoformat()
    },
    {
        "id": 2,
        "location": {"lat": 41.3851, "lon": 2.1734, "name": "Barcelona Norte"},
        "electoral_participation": 74.5,
        "citizen_participation_spaces": 8,
        "transparency_index": 82,
        "active_organizations": 24,
        "timestamp": datetime.now().isoformat()
    }
]


@app.route('/')
def index():
    """Root endpoint - API information"""
    return jsonify({
        "name": "Climate and Social Justice Map API",
        "version": "1.0.0",
        "description": "Backend API for integrating environmental, socioeconomic, and democratic data",
        "endpoints": {
            "/api/environmental": "Get environmental data",
            "/api/socioeconomic": "Get socioeconomic data",
            "/api/democratic": "Get democratic participation data",
            "/api/vulnerability": "Calculate vulnerability index (IVSA)",
            "/api/reports": "Citizen environmental reports",
            "/api/health": "API health check"
        }
    })


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/environmental')
def get_environmental_data():
    """
    Get environmental data (air quality, temperature, vegetation, etc.)
    Query params: location (optional)
    """
    location = request.args.get('location')
    
    if location:
        filtered_data = [d for d in MOCK_ENVIRONMENTAL_DATA if location.lower() in d['location']['name'].lower()]
        return jsonify({"data": filtered_data, "count": len(filtered_data)})
    
    return jsonify({"data": MOCK_ENVIRONMENTAL_DATA, "count": len(MOCK_ENVIRONMENTAL_DATA)})


@app.route('/api/socioeconomic')
def get_socioeconomic_data():
    """
    Get socioeconomic data (income, poverty, services access, etc.)
    Query params: location (optional)
    """
    location = request.args.get('location')
    
    if location:
        filtered_data = [d for d in MOCK_SOCIOECONOMIC_DATA if location.lower() in d['location']['name'].lower()]
        return jsonify({"data": filtered_data, "count": len(filtered_data)})
    
    return jsonify({"data": MOCK_SOCIOECONOMIC_DATA, "count": len(MOCK_SOCIOECONOMIC_DATA)})


@app.route('/api/democratic')
def get_democratic_data():
    """
    Get democratic participation data (electoral participation, organizations, etc.)
    Query params: location (optional)
    """
    location = request.args.get('location')
    
    if location:
        filtered_data = [d for d in MOCK_DEMOCRATIC_DATA if location.lower() in d['location']['name'].lower()]
        return jsonify({"data": filtered_data, "count": len(filtered_data)})
    
    return jsonify({"data": MOCK_DEMOCRATIC_DATA, "count": len(MOCK_DEMOCRATIC_DATA)})


@app.route('/api/vulnerability')
def calculate_vulnerability():
    """
    Calculate the Socio-environmental Vulnerability Index (IVSA)
    Combines environmental, socioeconomic, and democratic data
    Returns: high, medium, or low vulnerability classification
    """
    vulnerability_data = []
    
    for i in range(len(MOCK_ENVIRONMENTAL_DATA)):
        env = MOCK_ENVIRONMENTAL_DATA[i]
        soc = MOCK_SOCIOECONOMIC_DATA[i]
        dem = MOCK_DEMOCRATIC_DATA[i]
        
        # Simple vulnerability calculation (normalized 0-100)
        env_score = (env['air_quality']['pm25'] + env['co2_emissions'] * 5) / 2
        soc_score = soc['poverty_index']
        dem_score = 100 - dem['electoral_participation']
        
        # Weighted average
        vulnerability_score = (env_score * 0.4 + soc_score * 0.35 + dem_score * 0.25)
        
        # Classification
        if vulnerability_score >= 60:
            level = "high"
            color = "#FF4444"  # Red
        elif vulnerability_score >= 35:
            level = "medium"
            color = "#FFA500"  # Orange
        else:
            level = "low"
            color = "#44FF44"  # Green
        
        vulnerability_data.append({
            "location": env['location'],
            "vulnerability_score": round(vulnerability_score, 2),
            "vulnerability_level": level,
            "color": color,
            "factors": {
                "environmental": round(env_score, 2),
                "socioeconomic": round(soc_score, 2),
                "democratic": round(dem_score, 2)
            },
            "timestamp": datetime.now().isoformat()
        })
    
    return jsonify({"data": vulnerability_data, "count": len(vulnerability_data)})


# Citizen reports storage (in-memory for demo - would use database in production)
citizen_reports = []


@app.route('/api/reports', methods=['GET', 'POST'])
def handle_reports():
    """
    GET: Retrieve citizen environmental reports
    POST: Submit a new environmental report
    """
    if request.method == 'GET':
        report_type = request.args.get('type')
        if report_type:
            filtered = [r for r in citizen_reports if r['type'] == report_type]
            return jsonify({"data": filtered, "count": len(filtered)})
        return jsonify({"data": citizen_reports, "count": len(citizen_reports)})
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['type', 'location', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": "Missing required fields",
                "required": required_fields
            }), 400
        
        report = {
            "id": len(citizen_reports) + 1,
            "type": data['type'],  # e.g., "illegal_dump", "deforestation", "water_issue"
            "location": data['location'],  # {lat, lon, name}
            "description": data['description'],
            "status": "pending",  # pending, verified, resolved
            "timestamp": datetime.now().isoformat(),
            "reporter": data.get('reporter', 'anonymous')
        }
        
        citizen_reports.append(report)
        
        return jsonify({
            "message": "Report submitted successfully",
            "report": report
        }), 201


@app.route('/api/reports/<int:report_id>', methods=['GET', 'PUT'])
def handle_report(report_id):
    """
    GET: Retrieve a specific report
    PUT: Update report status
    """
    report = next((r for r in citizen_reports if r['id'] == report_id), None)
    
    if not report:
        return jsonify({"error": "Report not found"}), 404
    
    if request.method == 'GET':
        return jsonify(report)
    
    elif request.method == 'PUT':
        data = request.get_json()
        if 'status' in data:
            report['status'] = data['status']
        return jsonify({
            "message": "Report updated successfully",
            "report": report
        })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Climate and Social Justice Map API                       ║
    ║  Backend Server Starting...                               ║
    ║                                                           ║
    ║  Running on: http://localhost:{port}                      ║
    ║  Debug mode: {debug}                                      ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
