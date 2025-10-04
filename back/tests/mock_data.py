"""
Mock data for testing
Use these data points to test the API with various locations
"""
from datetime import datetime


def get_mock_environmental_data():
    """Get mock environmental data for testing - OpenStreetMap compatible coordinates"""
    return [
        {
            "id": 1,
            "location": {"lat": 40.3833, "lon": -3.7167, "name": "Madrid Sur - Vallecas", "country": "Spain"},
            "air_quality": {"pm25": 45.2, "no2": 38.5, "ozone": 62.1},
            "temperature": 28.5,
            "vegetation_coverage": 15.3,
            "flood_risk": "medium",
            "co2_emissions": 8.2,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 2,
            "location": {"lat": 41.3974, "lon": 2.1694, "name": "Barcelona - Gràcia", "country": "Spain"},
            "air_quality": {"pm25": 32.1, "no2": 28.3, "ozone": 55.4},
            "temperature": 26.2,
            "vegetation_coverage": 28.7,
            "flood_risk": "low",
            "co2_emissions": 5.8,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 3,
            "location": {"lat": 28.6139, "lon": 77.2090, "name": "Nueva Delhi", "country": "India"},
            "air_quality": {"pm25": 153.4, "no2": 87.6, "ozone": 92.3},
            "temperature": 35.2,
            "vegetation_coverage": 8.2,
            "flood_risk": "medium",
            "co2_emissions": 15.7,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 4,
            "location": {"lat": -6.2088, "lon": 106.8456, "name": "Jakarta", "country": "Indonesia"},
            "air_quality": {"pm25": 68.9, "no2": 52.3, "ozone": 75.8},
            "temperature": 31.7,
            "vegetation_coverage": 14.5,
            "flood_risk": "high",
            "co2_emissions": 11.3,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 5,
            "location": {"lat": -23.5505, "lon": -46.6333, "name": "São Paulo", "country": "Brasil"},
            "air_quality": {"pm25": 44.2, "no2": 39.8, "ozone": 64.5},
            "temperature": 24.3,
            "vegetation_coverage": 21.7,
            "flood_risk": "medium",
            "co2_emissions": 8.9,
            "timestamp": datetime.now().isoformat()
        }
    ]


def get_mock_socioeconomic_data():
    """Get mock socioeconomic data for testing"""
    return [
        {
            "id": 1,
            "location": {"lat": 40.3833, "lon": -3.7167, "name": "Madrid Sur - Vallecas", "country": "Spain"},
            "average_income": 18500,
            "poverty_index": 28.5,
            "basic_services_access": {"water": 95, "health": 82, "education": 88},
            "human_development_index": 0.72,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 2,
            "location": {"lat": 41.3974, "lon": 2.1694, "name": "Barcelona - Gràcia", "country": "Spain"},
            "average_income": 32000,
            "poverty_index": 12.3,
            "basic_services_access": {"water": 98, "health": 95, "education": 96},
            "human_development_index": 0.88,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 3,
            "location": {"lat": 28.6139, "lon": 77.2090, "name": "Nueva Delhi", "country": "India"},
            "average_income": 3200,
            "poverty_index": 58.7,
            "basic_services_access": {"water": 68, "health": 52, "education": 71},
            "human_development_index": 0.48,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 4,
            "location": {"lat": -6.2088, "lon": 106.8456, "name": "Jakarta", "country": "Indonesia"},
            "average_income": 4800,
            "poverty_index": 48.3,
            "basic_services_access": {"water": 72, "health": 61, "education": 76},
            "human_development_index": 0.55,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 5,
            "location": {"lat": -23.5505, "lon": -46.6333, "name": "São Paulo", "country": "Brasil"},
            "average_income": 8500,
            "poverty_index": 38.9,
            "basic_services_access": {"water": 82, "health": 74, "education": 85},
            "human_development_index": 0.64,
            "timestamp": datetime.now().isoformat()
        }
    ]


def get_mock_democratic_data():
    """Get mock democratic participation data for testing"""
    return [
        {
            "id": 1,
            "location": {"lat": 40.3833, "lon": -3.7167, "name": "Madrid Sur - Vallecas", "country": "Spain"},
            "electoral_participation": 58.2,
            "citizen_participation_spaces": 3,
            "transparency_index": 65,
            "active_organizations": 12,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 2,
            "location": {"lat": 41.3974, "lon": 2.1694, "name": "Barcelona - Gràcia", "country": "Spain"},
            "electoral_participation": 74.5,
            "citizen_participation_spaces": 8,
            "transparency_index": 82,
            "active_organizations": 24,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 3,
            "location": {"lat": 28.6139, "lon": 77.2090, "name": "Nueva Delhi", "country": "India"},
            "electoral_participation": 52.3,
            "citizen_participation_spaces": 2,
            "transparency_index": 42,
            "active_organizations": 8,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 4,
            "location": {"lat": -6.2088, "lon": 106.8456, "name": "Jakarta", "country": "Indonesia"},
            "electoral_participation": 58.7,
            "citizen_participation_spaces": 3,
            "transparency_index": 48,
            "active_organizations": 11,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 5,
            "location": {"lat": -23.5505, "lon": -46.6333, "name": "São Paulo", "country": "Brasil"},
            "electoral_participation": 61.4,
            "citizen_participation_spaces": 4,
            "transparency_index": 54,
            "active_organizations": 14,
            "timestamp": datetime.now().isoformat()
        }
    ]
